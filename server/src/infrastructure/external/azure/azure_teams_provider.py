import requests
import re
from typing import List, Optional
from domain.ports import TeamsProvider
from domain.models import Message
from infrastructure.config.settings import settings

class AzureTeamsProvider(TeamsProvider):
    
    # Initialize Azure credentials from the settings and set the token placeholder.
    def __init__(self):
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.tenant_id = settings.AZURE_TENANT_ID
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.access_token = None

    # Authenticate with Microsoft Azure using OAuth2 Client Credentials flow to get an access token.
    def get_access_token(self) -> str:
        data = {
            'client_id': self.client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json().get('access_token', "")

    # Manage the access token and refresh it if necessary.
    def get_valid_token(self) -> str:
        if not self.access_token:
            self.access_token = self.get_access_token()
        return self.access_token

    # Fetch all groups that are provisioned as Teams from Microsoft Graph.
    def get_all_teams(self) -> List[dict]:
        try:
            url = "https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/any(x:x eq 'Team')"
            headers = {'Authorization': f'Bearer {self.get_valid_token()}'}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return []
            return response.json().get('value', [])
        except Exception:
            return []

    # Fetch all channels for a specific team ID.
    def get_channels(self, team_id: str) -> List[dict]:
        try:
            url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
            headers = {'Authorization': f'Bearer {self.get_valid_token()}'}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return []
            return response.json().get('value', [])
        except Exception:
            return []

    # Cleans HTML tags from the message body content.
    def clean_message_content(self, raw_html: str) -> str:
        if not raw_html: 
            return ""
        clean = re.sub('<[^<]+?>', '', raw_html)
        return clean.strip()

    # Map a Graph API message dictionary to a domain Message model.
    def map_to_domain_message(self, data: dict, team_id: str, channel_id: str) -> Optional[Message]:
        body = data.get('body') or {}
        raw_body = body.get('content')
        
        if not raw_body:
            return None
            
        clean_text = self.clean_message_content(raw_body)
        if not clean_text:
            return None
        
        from_data = data.get('from') or {}
        user_data = from_data.get('user') or {}
        sender_name = user_data.get('displayName', 'System')
        
        return Message(
            externalId=data.get('id'),
            content=clean_text,
            sender=sender_name,
            timestamp=data.get('createdDateTime', ""),
            teamId=team_id,
            channelId=channel_id,
            analyzed=False,
            scores=None
        )

    # Fetch messages and their replies from a channel since the last sync date.
    def get_new_messages(self, team_id: str, channel_id: str, last_sync: Optional[str]) -> List[Message]:
        try:
            domain_messages = []
            skip = 0
            top = 50
            keep_fetching = True
            token = self.get_valid_token()
            headers = {'Authorization': f'Bearer {token}'}

            while keep_fetching:
                url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages?$expand=replies&$top={top}&$skip={skip}"
                
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    break
                
                data = response.json()
                raw_messages = data.get('value', [])
                
                if len(raw_messages) < top:
                    keep_fetching = False
                else:
                    skip += top

                for msg in reversed(raw_messages):
                    msg_date = msg.get('createdDateTime')
                    
                    if not last_sync or (msg_date and msg_date > last_sync):
                        mapped = self.map_to_domain_message(msg, team_id, channel_id)
                        if mapped:
                            domain_messages.append(mapped)
                    
                    replies = msg.get('replies', [])
                    for reply in reversed(replies):
                        reply_date = reply.get('createdDateTime')
                        if not last_sync or (reply_date and reply_date > last_sync):
                            mapped_reply = self.map_to_domain_message(reply, team_id, channel_id)
                            if mapped_reply:
                                domain_messages.append(mapped_reply)

            return domain_messages
            
        except Exception as e:
            print(f"Error: {e}")
            return []
        
    # Checks user permissions, admin status, and owned teams from Azure.
    def get_user_permissions(self, email: str) -> dict:
        try:
            token = self.get_valid_token()
            headers = {'Authorization': f'Bearer {token}'}
            
            user_url = f"https://graph.microsoft.com/v1.0/users/{email}"
            user_res = requests.get(user_url, headers=headers)
            
            if user_res.status_code != 200:
                return {"in_org": False, "is_admin": False, "is_owner": False, "owned_teams": []}
            
            user_data = user_res.json()
            user_id = user_data.get('id')

            roles_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf"
            roles_res = requests.get(roles_url, headers=headers)
            
            is_admin = False
            if roles_res.status_code == 200:
                roles = roles_res.json().get('value', [])
                is_admin = any(role.get('displayName') == "Global Administrator" for role in roles)

            owned_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/ownedObjects/microsoft.graph.group"
            owned_res = requests.get(owned_url, headers=headers)
            
            owned_teams_ids = []
            if owned_res.status_code == 200:
                groups = owned_res.json().get('value', [])
                owned_teams_ids = [
                    g.get('id') for g in groups 
                    if "Team" in g.get('resourceProvisioningOptions', [])
                ]

            return {
                "in_org": True,
                "is_admin": is_admin,
                "is_owner": len(owned_teams_ids) > 0, 
                "owned_teams": owned_teams_ids
            }
        except Exception:
            return {"in_org": False, "is_admin": False, "is_owner": False, "owned_teams": []}
            
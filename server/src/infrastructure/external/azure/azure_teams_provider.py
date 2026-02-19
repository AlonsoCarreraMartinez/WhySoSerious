import requests
from typing import List, Optional
from domain.ports import TeamsProvider
from domain.models import Message
from infrastructure.config.settings import settings

class AzureTeamsProvider(TeamsProvider):
    
    # Initialize Azure credentials from the settings and set the token placeholder.
    def __init__(self):
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.tenant_id = settings.TENANT_ID
        self._token = None

    # Authenticate with Microsoft Azure using OAuth2 Client Credentials flow to get an access token.
    def get_access_token(self) -> str:

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'client_id': self.client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        response = requests.post(url, data=data)
        response.raise_for_status()

        return response.json().get('access_token')

    # Property to manage the access token.
    @property
    def token(self):
        if not self._token:
            self._token = self.get_access_token()
        return self._token

    # Fetch all teams from Microsoft Graph.
    def get_all_teams(self) -> List[dict]:

        url = "https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/any(x:x eq 'Team')"
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)

        return response.json().get('value', [])

    # Fetch channels for a specific team.
    def get_channels(self, team_id: str) -> List[dict]:

        url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)

        return response.json().get('value', [])

    # Fetch new messages since the last synchronization date.
    def get_new_messages(self, team_id: str, channel_id: str, last_sync: Optional[str]) -> List[Message]:
        
        url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)
        data = response.json().get('value', [])
        
        messages = []
        for msg_data in data:
            
            timestamp = msg_data.get("createdDateTime")
            if last_sync and timestamp <= last_sync:
                continue

            messages.append(Message(
                externalId=msg_data.get("id"),
                content=msg_data.get("body", {}).get("content", ""),
                sender=msg_data.get("from", {}).get("user", {}).get("displayName", "Unknown"),
                timestamp=timestamp,
                teamId=team_id,
                channelId=channel_id,
                analyzed=False,  
                scores=None      
            ))
            
        return messages
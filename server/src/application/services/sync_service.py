from datetime import datetime, timedelta
import uuid
from typing import List
from domain.ports import MessageRepository, TeamsProvider, BurnoutRepository
from domain.models import ConversationSession, Message

class SyncService:

    # Initialize repositories and provider. 
    def __init__(self, message_repo: MessageRepository, teams_provider: TeamsProvider,burnout_repo: BurnoutRepository): 
        self.message_repo = message_repo
        self.teams_provider = teams_provider
        self.burnout_repo = burnout_repo
        self.target_teams = ["León", "Oviedo", "La Bañeza"]

    # Syncs messages and handles session grouping logic.
    def sync_messages(self):
        print("Starting synchronization.")
        teams = self.teams_provider.get_all_teams()

        if teams is None:
            return

        for team in teams:
            team_name = team.get('displayName')
            if team_name not in self.target_teams:
                continue
            
            channels = self.teams_provider.get_channels(team['id'])
            if channels is None:
                continue

            for channel in channels:
                channel_name = channel.get('displayName')
                last_db_date = self.message_repo.get_last_sync_timestamp(channel['id'])
                
                new_messages = self.teams_provider.get_new_messages(
                    team_id=team['id'], 
                    channel_id=channel['id'], 
                    last_sync=last_db_date
                )
                
                if not new_messages:
                    continue
                
                for msg in new_messages:
                    msg.teamName = team_name
                    msg.channelName = channel_name
                    
                    self.assign_session(msg, team['id'], channel['id'])
                    
                    self.message_repo.save(msg)

        print("\nSynchronization completed.")

    # Determine if a message belongs to an existing session or a new one.
    def assign_session(self, msg: Message, team_id: str, channel_id: str):
        if msg.parentId:
            msg.sessionId = f"session_{msg.parentId}"
        else:
            new_session_id = f"session_{msg.externalId}"
            
            if msg.channelName == "General":
                last_msg = self.message_repo.get_last_message_by_channel(channel_id)
                
                if not last_msg or not last_msg.sessionId:
                    msg.sessionId = new_session_id
                else:
                    fmt = "%Y-%m-%dT%H:%M:%SZ"
                    try:
                        current_t = datetime.strptime(msg.timestamp[:19] + "Z", fmt)
                        last_t = datetime.strptime(last_msg.timestamp[:19] + "Z", fmt)
                        
                        if (current_t - last_t) > timedelta(minutes=20):
                            msg.sessionId = new_session_id
                        else:
                            msg.sessionId = last_msg.sessionId
                    except Exception:
                        msg.sessionId = new_session_id
            else:
                msg.sessionId = new_session_id
        
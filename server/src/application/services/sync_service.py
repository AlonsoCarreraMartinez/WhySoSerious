from typing import List
from domain.ports import MessageRepository, TeamsProvider

class SyncService:

    # Initialize repository and provider.
    def __init__(self, message_repo: MessageRepository, teams_provider: TeamsProvider):

        self.message_repo = message_repo
        self.teams_provider = teams_provider
        self.target_teams = ["León", "Oviedo", "La Bañeza"]  # Filter for target teams 

    # Syncs messages from target Teams and channels to the database.
    def sync_messages(self):
        
        print("Starting synchronization.")
        
        teams = self.teams_provider.get_all_teams()

        if teams is None:
            print("Error: Could not fetch teams from provider.")
            return

        for team in teams:

            team_name = team.get('displayName')
            
            if team_name not in self.target_teams:
                continue
            
            print(f"\nSyncing Team: {team_name}")
            
            channels = self.teams_provider.get_channels(team['id'])

            if channels is None:
                print(f" Skipping team {team_name}: Could not fetch channels.")
                continue

            for channel in channels:
                
                channel_name = channel.get('displayName')
                print(f" Processing channel: {channel_name}")
                
                last_db_date = self.message_repo.get_last_sync_timestamp(channel['id'])
                
                new_messages = self.teams_provider.get_new_messages(
                    team_id=team['id'], 
                    channel_id=channel['id'], 
                    last_sync=last_db_date
                )
                
                if new_messages is None:
                    print(f"  Warning: Could not fetch messages for channel {channel_name}.")
                    continue
                
                for msg in new_messages:
                    
                    msg.teamName = team_name
                    msg.channelName = channel_name
                    self.message_repo.save(msg)

        print("\nSynchronization completed.")
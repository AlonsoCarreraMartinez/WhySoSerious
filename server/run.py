import uvicorn
import sys
import os
import argparse
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
load_dotenv()

# Launch server
def start_server():

    print("\nLaunching Server")
    uvicorn.run(
        "infrastructure.api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

# Execute the full data synchronization and AI analysis.
def run_sync():
   
    print("\nStarting synchronization and analysis")
    
    from infrastructure.persistence.repositories.mongo_message_repository import MongoMessageRepository
    from infrastructure.persistence.repositories.mongo_team_repository import MongoTeamRepository
    from infrastructure.persistence.repositories.mongo_channel_repository import MongoChannelRepository
    from infrastructure.persistence.repositories.mongo_burnout_repository import MongoBurnoutRepository
    from infrastructure.persistence.repositories.mongo_notification_repository import MongoNotificationRepository
    from infrastructure.external.azure.azure_teams_provider import AzureTeamsProvider
    from infrastructure.external.notifications.mongo_notification_observer import MongoNotificationObserver
    from application.services.sync_service import SyncService
    from application.services.burnout_service import BurnoutService
    
    try:
        
        message_repo = MongoMessageRepository()
        team_repo = MongoTeamRepository()
        channel_repo = MongoChannelRepository()
        burnout_repo = MongoBurnoutRepository()
        notification_repo = MongoNotificationRepository()
        azure_provider = AzureTeamsProvider()

        sync_service = SyncService(message_repo, azure_provider, burnout_repo)
        burnout_service = BurnoutService(message_repo, team_repo, channel_repo, burnout_repo)
        
        notification_observer = MongoNotificationObserver(notification_repo)
        sync_service.add_observer(notification_observer)
        burnout_service.add_observer(notification_observer)
        
        sync_service.sync_messages()
        burnout_service.analyze_data()
        
        print("\nSynchronization and analysis finished successfully")
        
    except Exception as e:
        print(f"\nError: {e}")

# python run.py --sync
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="WhySoSerious CLI")
    parser.add_argument('--sync', action='store_true', help='Run full sync and analysis')
    
    args = parser.parse_args()

    if args.sync:
        run_sync()
    else:
        start_server()
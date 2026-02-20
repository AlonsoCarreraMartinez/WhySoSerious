from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from application.services.sync_service import SyncService
from application.services.burnout_service import BurnoutService

class TaskScheduler:
   
    def __init__(self, sync_service: SyncService, burnout_service: BurnoutService):

        self.scheduler = BackgroundScheduler()
        self.sync_service = sync_service
        self.burnout_service = burnout_service

    # Sync messages from Teams and analyzed data and update burnout scores.
    def scheduled_job(self):
       
        print("\n[CRON JOB] Starting automated background tasks")
        
        # PIPELINE.
        try:

            self.sync_service.sync_messages()
            self.burnout_service.analyzed_data()

            print("[CRON JOB] Background tasks completed successfully\n")

        except Exception as e:

            print(f"[CRON JOB] Error during automated execution: {e}")

    # Configures and starts the scheduler.
    def start(self):
        
        # Runs once every hour on the hour (minute="0").
        self.scheduler.add_job(
            self.scheduled_job,
            CronTrigger(minute="0"),     
            id="sync_and_analyze_burnout_job"
        )
        
        self.scheduler.start()
        
        # Scheduler shuts down.
        atexit.register(lambda: self.scheduler.shutdown())
    
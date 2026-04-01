import uuid
from datetime import datetime
from domain.ports import NotificationObserver, NotificationRepository
from domain.models import Notification

class MongoNotificationObserver(NotificationObserver):

    # Initializes the observer with the notification repository.
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    # Notifies when the synchronization process finishes.
    def on_sync_completed(self, message_count: int):
        if message_count == 0:
            title = "System Update"
            message = "No new messages to analyze in the current cycle."
        else:
            title = "Analysis Complete"
            message = f"Successfully analyzed {message_count} new messages across monitored teams."

        notif = Notification(
            _id=str(uuid.uuid4()),
            title=title,
            message=message,
            date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            target_team=None 
        )
        self.repository.save(notif)

    # Notifies when a team or channel crosses the critical burnout threshold.
    def on_critical_burnout(self, target_name: str, parent_team: str, score: float, is_channel: bool):
        if is_channel:
            title = "Critical Channel Alert"
            message = f"Channel '{target_name}' in Team '{parent_team}' has reached a critical burnout level."
        else:
            title = "Critical Burnout Alert"
            message = f"Team '{target_name}' has reached a critical burnout level. Immediate attention is advised."

        notif = Notification(
            _id=str(uuid.uuid4()),
            title=title,
            message=message,
            date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            target_team=parent_team 
        )
        self.repository.save(notif)
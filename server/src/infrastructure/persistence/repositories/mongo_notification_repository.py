from typing import List
from domain.ports import NotificationRepository
from domain.models import Notification
from infrastructure.persistence.mongo_client import mongo_client

class MongoNotificationRepository(NotificationRepository):
    
    # Access the 'notifications' collection in the database.
    def __init__(self):
        self.collection = mongo_client.get_collection("notifications")

    # Saves a notification to the database.
    def save(self, notification: Notification):
        self.collection.insert_one(notification.model_dump(by_alias=True))

    # Retrieves notifications applicable to a specific user based on their roles.
    def get_for_user(self, is_admin: bool, managed_teams: List[str]) -> List[Notification]:
        query = {}
        if not is_admin:
            
            query["$or"] = [
                {"target_team": None},
                {"target_team": {"$in": managed_teams}}
            ]
            
        cursor = self.collection.find(query).sort("date", -1).limit(50)
        return [Notification(**doc) for doc in cursor]

    # Marks a notification as read for a specific user email.
    def mark_as_read(self, notification_id: str, email: str):
        self.collection.update_one(
            {"_id": notification_id},
            {"$addToSet": {"read_by": email}}
        )
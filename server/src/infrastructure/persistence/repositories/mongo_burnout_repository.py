from typing import List
from domain.ports import BurnoutRepository
from domain.models import ConversationSession, HealthTrend
from infrastructure.persistence.mongo_client import mongo_client

class MongoBurnoutRepository(BurnoutRepository):
    
    # Access the 'ConversationSession' and 'HealthTrend' collections in the database.
    def __init__(self):
        self.sessions_collection = mongo_client.get_collection("sessions")
        self.trends_collection = mongo_client.get_collection("trends")

    # Saves or updates a conversation session.
    def save_session(self, session: ConversationSession):
        
        update_data = {
            "endTime": session.endTime,
            "messageCount": session.messageCount
        }
        
        if session.sessionScores:
            update_data["sessionScores"] = session.sessionScores.model_dump()

        self.sessions_collection.update_one(
            {"_id": session.id},
            {
                "$setOnInsert": {
                    "channelId": session.channelId,
                    "teamId": session.teamId,
                    "startTime": session.startTime,
                },
                "$set": update_data
            },
            upsert=True
        )

    # Retrieves all sessions for a specific channel.
    def get_sessions_by_channel(self, channel_id: str) -> List[ConversationSession]:
        cursor = self.sessions_collection.find({"channelId": channel_id})
        return [ConversationSession(**doc) for doc in cursor]

    # Saves a health trend point for historical charts.
    def save_trend(self, trend: HealthTrend):
        self.trends_collection.insert_one(trend.model_dump(by_alias=True, exclude_none=True))
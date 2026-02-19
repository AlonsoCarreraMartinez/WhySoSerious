from typing import List
from domain.ports import ChannelRepository
from domain.models import Channel, BertScores
from infrastructure.persistence.mongo_client import mongo_client

class MongoChannelRepository(ChannelRepository):
    
    # Access the 'channel' collection in the database.
    def __init__(self):
        self.collection = mongo_client.get_collection("channels")

    # Fetch all channels that belong to a specific team name.
    def get_by_team(self, team_name: str) -> List[Channel]:

        cursor = self.collection.find({"team_name": team_name})
        
        return [Channel(**doc) for doc in cursor] # Convert each MongoDB document into a Channel model object using unpacking (**).

    # Update the specific channel's scores calculated by the AI.
    def update_burnout_metrics(self, channel_id: str, scores: BertScores):
        
        self.collection.update_one(
            {"_id": channel_id},
            {"$set": {"burnout_mean": scores.model_dump()}},
            upsert=False
        )
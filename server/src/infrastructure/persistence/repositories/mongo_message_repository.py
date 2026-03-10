from typing import List, Optional
from domain.ports import MessageRepository
from domain.models import Message
from infrastructure.persistence.mongo_client import mongo_client

class MongoMessageRepository(MessageRepository):
    
    # Access the 'message' collection in the database.
    def __init__(self):
        self.collection = mongo_client.get_collection("messages")

    # Saves a message to the database.
    def save(self, message: Message):
    
        self.collection.update_one(
            {"_id": message.externalId},
            {"$set": message.model_dump(by_alias=True)},
            upsert=True
        )

    # Returns all messages that haven't been processed by the BERT model yet.
    def get_unanalyzed(self) -> List[Message]:
        
        cursor = self.collection.find({"analyzed": False})
        
        return [Message(**doc) for doc in cursor] # Convert each MongoDB document into a Message model object using unpacking (**).

    # Marks a list of messages as analyzed and clears their content for privacy.
    def mark_as_analyzed(self, message_ids: List[str]):
        if not message_ids:
            return
            
        self.collection.update_many(
            {"_id": {"$in": message_ids}},
            {
                "$set": {
                    "analyzed": True,
                    "content": None  
                }
            }
        )

    # Returns the timestamp of the last message saved for a specific channel.
    def get_last_sync_timestamp(self, channel_id: str) -> Optional[str]:

        last_message = self.collection.find_one(
            {"channelId": channel_id},
            sort=[("timestamp", -1)]
        )
        
        return last_message.get("timestamp") if last_message else None
    
    # Returns the last message saved for a specific channel to compare timestamps.
    def get_last_message_by_channel(self, channel_id: str) -> Optional[Message]:
        doc = self.collection.find_one(
            {"channelId": channel_id},
            sort=[("timestamp", -1)]
        )
        if doc:
            return Message(**doc)
        return None
from typing import Optional
from domain.ports import UserRepository
from domain.models import User
from infrastructure.persistence.mongo_client import mongo_client

class MongoUserRepository(UserRepository):

    # Access the 'user' collection in the database.
    def __init__(self):
        self.collection = mongo_client.get_collection("users")

    # Fetches a user by their MongoDB ID or external ID.
    def get_by_id(self, user_id: str) -> Optional[User]:
        
        user_data = self.collection.find_one({"externalId": user_id})

        if user_data:
            return User(**user_data) # Convert each MongoDB document into a User model object using unpacking (**).
        
        return None

    # Fetches a user by their email address for authentication.
    def get_by_email(self, email: str) -> Optional[User]:

        user_data = self.collection.find_one({"email": email})
        
        if user_data:
            return User(**user_data) # Convert each MongoDB document into a User model object using unpacking (**).
        
        return None
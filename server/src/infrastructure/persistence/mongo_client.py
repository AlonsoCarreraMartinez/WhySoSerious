from pymongo import MongoClient
from infrastructure.config.settings import settings

class Mongo_client:

    def __init__(self):
        
        self.client = MongoClient(settings.MONGO_URI) # Establish connection using the URI from the .env file.
        self.db = self.client.get_database("whysoserious_db") # Access the specific database.

    # Returns a specific collection form the database. 
    def get_collection(self, name: str):

        return self.db[name]
    
# Singleton instance used across the entire application.
mongo_client = Mongo_client()
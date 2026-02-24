from typing import Optional, List
from domain.ports import TeamRepository
from domain.models import Team, BertScores
from infrastructure.persistence.mongo_client import mongo_client

class MongoTeamRepository(TeamRepository):
   
    # Access the 'teams' collection in the database.
    def __init__(self):
        self.collection = mongo_client.get_collection("teams")

    # Fetch a single team using its external Microsoft ID.
    def get_by_id(self, team_id: str) -> Optional[Team]:
       
        team_data = self.collection.find_one({"externalId": team_id})
        
        if team_data:
            return Team(**team_data)
        
        return None

    # Search for all teams where the manager field matches the provided email/ID.
    def get_by_manager(self, manager: str) -> List[Team]:
       
        cursor = self.collection.find({"manager": manager})
        
        return [Team(**doc) for doc in cursor] # Convert each MongoDB document into a Team model object using unpacking (**).

    # Update the team's global scores calculated by the BurnoutService.
    def update_burnout_metrics(self, team_id: str, scores: BertScores):
        
        self.collection.update_one(
            {"_id": team_id},
            {"$set": {"burnout_mean": scores.model_dump()}},
            upsert=False 
        )

    # Fetches all teams stored in the database.
    def get_all(self) -> List[Team]:

        cursor = self.collection.find({})
        return [Team(**doc) for doc in cursor] # Convert each MongoDB document into a Team model object using unpacking (**).
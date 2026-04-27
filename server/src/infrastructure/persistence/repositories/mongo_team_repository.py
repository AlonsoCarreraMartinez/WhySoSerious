from typing import Optional, List
from domain.ports import TeamRepository
from domain.models import Team, MBIScores, ContextMetrics, WBIScores
from infrastructure.persistence.mongo_client import mongo_client

class MongoTeamRepository(TeamRepository):
   
    # Access the 'teams' collection in the database.
    def __init__(self):
        self.collection = mongo_client.get_collection("teams")

    # Fetch a single team using its external Microsoft ID.
    def get_by_id(self, team_id: str) -> Optional[Team]:
       
        team_data = self.collection.find_one({"_id": team_id})
        
        if team_data:
            return Team(**team_data)
        
        return None

    # Search for all teams where the manager field matches the provided email/ID.
    def get_by_manager(self, manager: str) -> List[Team]:
       
        cursor = self.collection.find({"managers": manager})
        
        return [Team(**doc) for doc in cursor] 

    # Update the team's global scores calculated by the BurnoutService.
    def update_burnout_metrics(self, team_id: str, mbi: MBIScores, wbi: WBIScores, context: Optional[ContextMetrics] = None):
        update_data = {
            "burnout_mean": mbi.model_dump(),
            "wbi_scores": wbi.model_dump()
        }
        if context:
            update_data["context_metrics"] = context.model_dump()
            
        self.collection.update_one(
            {"_id": team_id},
            {"$set": update_data},
            upsert=False 
        )

    # Fetches all teams stored in the database.
    def get_all(self) -> List[Team]:
        cursor = self.collection.find({})
        return [Team(**doc) for doc in cursor]
    
    # Fetches all teams where a specific email is listed in the managers array.
    def get_teams_by_manager(self, manager_email: str) -> List[Team]:
        
        query = {"managers": {"$regex": f"^{manager_email}$", "$options": "i"}}
        cursor = self.collection.find(query)
        return [Team(**doc) for doc in cursor]
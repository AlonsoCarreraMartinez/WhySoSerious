import sys
import os
import random
from datetime import datetime

sys.path.append(os.getcwd())

from app.database import db
from app.auth import hash_password

def seed_database():
    
    db.users.delete_many({})
    db.teams.delete_many({})
    db.message_blocks.delete_many({})
    
    db.users.insert_one({
        "_id": "Guillermo",
        "username": "Guillermo",
        "role": "admin",
        "teams": [], 
        "password": hash_password("1234")
    })

    # Team names
    teams_list = ["Team-Alpha", "Team-Beta", "Team-Gamma"]
    users_per_team = 3
    
   
    for team_name in teams_list:
       
        team_suffix = team_name.split('-')[1] 
        
        members = []
        team_manager = ""
        
        # Create users 
        for i in range(1, users_per_team + 1):
            username = f"User-{team_suffix}-{i}"
            members.append(username)
            
            # Assign first user of the team as the manager
            role = "user"
            if i == 1:
                role = "manager"
                team_manager = username 
            
            # Insert User
            db.users.insert_one({
                "_id": username,
                "username": username,
                "role": role,
                "teams": [team_name],
                "password": hash_password("1234")
            })
            
            # Create messages 
            num_msgs = random.randint(1, 2)
            for _ in range(num_msgs):
                scores = {
                    "politeness": round(random.uniform(1, 10), 2),
                    "sarcasm": round(random.uniform(0, 5), 2),
                    "toxicity": round(random.uniform(0, 3), 2)
                }
                
                msg_data = {
                    "user": username,
                    "message": f"Auto-generated message from {username}",
                    "timestamp": datetime.utcnow(),
                    "scores": scores
                }
                
                db.message_blocks.insert_one({
                    "start_time": datetime.utcnow(),
                    "end_time": datetime.utcnow(),
                    "participants": [username],
                    "messages": [msg_data],
                    "aggregated_scores": scores
                })
        
        # Create teams
        db.teams.insert_one({
            "_id": team_name,
            "manager": team_manager, 
            "members": members
        })
      
if __name__ == "__main__":
    seed_database()
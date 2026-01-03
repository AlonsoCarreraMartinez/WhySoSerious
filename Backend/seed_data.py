import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"

if not MONGO_URI:
    print("ERROR: MONGO_URI not found in .env file")
    exit()

def seed_database():
    print("Starting data seeding...")
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print("Clearing old collections...")
    db.users.drop()
    db.teams.drop()
    db.channels.drop()

    default_password = generate_password_hash("password123")

    users = [
        {"_id": "alonso@ww5dl.onmicrosoft.com", "name": "Alonso Carrera", "role": "admin", "teams": ["Oviedo", "La Bañeza", "León"], "password": default_password},
        {"_id": "admin@ww5dl.onmicrosoft.com", "name": "Guillermo Menguez", "role": "admin", "teams": ["Oviedo", "La Bañeza", "León"], "password": default_password},
        {"_id": "AdeleV@ww5dl.onmicrosoft.com", "name": "Adele Vance", "role": "employee", "teams": ["Oviedo", "La Bañeza"], "password": default_password},
        {"_id": "LidiaH@ww5dl.onmicrosoft.com", "name": "Lidia Holloway", "role": "employee", "teams": ["La Bañeza", "León"], "password": default_password},
        {"_id": "IsaiahL@ww5dl.onmicrosoft.com", "name": "Isaiah Langer", "role": "employee", "teams": ["La Bañeza", "León"], "password": default_password},
        {"_id": "PattiF@ww5dl.onmicrosoft.com", "name": "Patti Fernandez", "role": "employee", "teams": ["León"], "password": default_password}
    ]
    db.users.insert_many(users)
    print(f"{len(users)} Users created.")

    channels = [
        {"_id": "19:05601fabb9c24d0d8b886a81930db632@thread.tacv2", "name": "General", "team_name": "Oviedo", "burnout_mean": None},
        {"_id": "19:fkU-S486HJhltOLqMvIPEjG5ysazsLRRJkTVaUSWR3Q1@thread.tacv2", "name": "Backlogs", "team_name": "Oviedo", "burnout_mean": None},
        
        {"_id": "19:V9L6UbA2VFe687KF-be3mDmUGRFO-xrynXuxweCYBdU1@thread.tacv2", "name": "General", "team_name": "La Bañeza", "burnout_mean": None},
        {"_id": "19:afa71eb9c66f4b60a30c705e393508fb@thread.tacv2", "name": "Backlogs", "team_name": "La Bañeza", "burnout_mean": None},
        
        {"_id": "19:qWJHf8j1OmMmc2OvIR2bfHF5Il5ZRNoo6Ou0JvhSzao1@thread.tacv2", "name": "General", "team_name": "León", "burnout_mean": None},
        {"_id": "19:16ddf8b922294f76b8738c2cd07de9d6@thread.tacv2", "name": "Backlogs", "team_name": "León", "burnout_mean": None}
    ]
    
    db.channels.insert_many(channels)
    print(f"{len(channels)} Channels created.")

    teams = [
        {
            "_id": "Oviedo",
            "name": "Oviedo", 
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "AdeleV@ww5dl.onmicrosoft.com"],
            "channels": [
                "19:05601fabb9c24d0d8b886a81930db632@thread.tacv2",
                "19:fkU-S486HJhltOLqMvIPEjG5ysazsLRRJkTVaUSWR3Q1@thread.tacv2"
            ],
            "burnout_mean": None
        },
        {
            "_id": "La Bañeza",
            "name": "La Bañeza", 
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "LidiaH@ww5dl.onmicrosoft.com", "IsaiahL@ww5dl.onmicrosoft.com", "AdeleV@ww5dl.onmicrosoft.com"],
            "channels": [
                "19:V9L6UbA2VFe687KF-be3mDmUGRFO-xrynXuxweCYBdU1@thread.tacv2",
                "19:afa71eb9c66f4b60a30c705e393508fb@thread.tacv2"
            ],
            "burnout_mean": None
        },
        {
            "_id": "León",
            "name": "León", 
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "LidiaH@ww5dl.onmicrosoft.com", "PattiF@ww5dl.onmicrosoft.com", "IsaiahL@ww5dl.onmicrosoft.com"],
            "channels": [
                "19:qWJHf8j1OmMmc2OvIR2bfHF5Il5ZRNoo6Ou0JvhSzao1@thread.tacv2",
                "19:16ddf8b922294f76b8738c2cd07de9d6@thread.tacv2"
            ],
            "burnout_mean": None
        }
    ]

    db.teams.insert_many(teams)
    print(f"{len(teams)} Teams created.")
    print("Database ready.")

if __name__ == "__main__":
    seed_database()
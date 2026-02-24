import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"

if not MONGO_URI:
    exit()

def seed_database():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    db.users.drop()
    db.teams.drop()
    db.channels.drop()
    db.messages.drop()

    users = [
        {"_id": "alonso@ww5dl.onmicrosoft.com", "name": "Alonso Carrera", "role": "employee", "teams": ["Oviedo", "La Bañeza", "León"]},
        {"_id": "admin@ww5dl.onmicrosoft.com", "name": "Guillermo Menguez", "role": "admin", "teams": ["Oviedo", "La Bañeza", "León"]},
        {"_id": "AdeleV@ww5dl.onmicrosoft.com", "name": "Adele Vance", "role": "employee", "teams": ["Oviedo", "La Bañeza"]},
        {"_id": "LidiaH@ww5dl.onmicrosoft.com", "name": "Lidia Holloway", "role": "employee", "teams": ["La Bañeza", "León"]},
        {"_id": "IsaiahL@ww5dl.onmicrosoft.com", "name": "Isaiah Langer", "role": "employee", "teams": ["La Bañeza", "León"]},
        {"_id": "PattiF@ww5dl.onmicrosoft.com", "name": "Patti Fernandez", "role": "employee", "teams": ["León"]}
    ]
    db.users.insert_many(users)

    channels = [
        {"_id": "19:V9L6UbA2VFe687KF-be3mDmUGRFO-xrynXuxweCYBdU1@thread.tacv2", "name": "General", "team_name": "Oviedo", "burnout_mean": None},
        {"_id": "19:05601fabb9c24d0d8b886a81930db632@thread.tacv2", "name": "Backlogs", "team_name": "Oviedo", "burnout_mean": None},
        {"_id": "19:fkU-S486HJhltOLqMvIPEjG5ysazsLRRJkTVaUSWR3Q1@thread.tacv2", "name": "General", "team_name": "La Bañeza", "burnout_mean": None},
        {"_id": "19:afa71eb9c66f4b60a30c705e393508fb@thread.tacv2", "name": "Backlogs", "team_name": "La Bañeza", "burnout_mean": None},
        {"_id": "19:qWJHf8j1OmMmc2OvIR2bfHF5Il5ZRNoo6Ou0JvhSzao1@thread.tacv2", "name": "General", "team_name": "León", "burnout_mean": None},
        {"_id": "19:16ddf8b922294f76b8738c2cd07de9d6@thread.tacv2", "name": "Backlogs", "team_name": "León", "burnout_mean": None}
    ]
    db.channels.insert_many(channels)

    teams = [
        {
            "_id": "Oviedo",
            "name": "Oviedo", 
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "AdeleV@ww5dl.onmicrosoft.com"],
            "channels": ["19:V9L6UbA2VFe687KF-be3mDmUGRFO-xrynXuxweCYBdU1@thread.tacv2", "19:05601fabb9c24d0d8b886a81930db632@thread.tacv2"],
            "burnout_mean": None
        },
        {
            "_id": "La Bañeza",
            "name": "La Bañeza", 
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "LidiaH@ww5dl.onmicrosoft.com", "IsaiahL@ww5dl.onmicrosoft.com", "AdeleV@ww5dl.onmicrosoft.com"],
            "channels": ["19:fkU-S486HJhltOLqMvIPEjG5ysazsLRRJkTVaUSWR3Q1@thread.tacv2", "19:afa71eb9c66f4b60a30c705e393508fb@thread.tacv2"],
            "burnout_mean": None
        },
        {
            "_id": "León",
            "name": "León", 
            "manager": "admin@ww5dl.onmicrosoft.com",
            "members": ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "LidiaH@ww5dl.onmicrosoft.com", "PattiF@ww5dl.onmicrosoft.com", "IsaiahL@ww5dl.onmicrosoft.com"],
            "channels": ["19:qWJHf8j1OmMmc2OvIR2bfHF5Il5ZRNoo6Ou0JvhSzao1@thread.tacv2", "19:16ddf8b922294f76b8738c2cd07de9d6@thread.tacv2"],
            "burnout_mean": None
        }
    ]

    db.teams.insert_many(teams)

if __name__ == "__main__":
    seed_database()
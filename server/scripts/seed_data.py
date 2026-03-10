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
    db.sessions.drop()  
    db.trends.drop()    

    users = [
        {"_id": "alonso@ww5dl.onmicrosoft.com", "name": "Alonso Carrera", "role": "employee", "teams": ["Oviedo", "La Bañeza", "León"]},
        {"_id": "admin@ww5dl.onmicrosoft.com", "name": "Guillermo Menguez", "role": "admin", "teams": ["Oviedo", "La Bañeza", "León"]},
        {"_id": "AdeleV@ww5dl.onmicrosoft.com", "name": "Adele Vance", "role": "employee", "teams": ["Oviedo", "La Bañeza"]},
        {"_id": "LidiaH@ww5dl.onmicrosoft.com", "name": "Lidia Holloway", "role": "employee", "teams": ["La Bañeza", "León"]},
        {"_id": "IsaiahL@ww5dl.onmicrosoft.com", "name": "Isaiah Langer", "role": "employee", "teams": ["La Bañeza", "León"]},
        {"_id": "PattiF@ww5dl.onmicrosoft.com", "name": "Patti Fernandez", "role": "employee", "teams": ["León"]}
    ]
    db.users.insert_many(users)

    m_oviedo = ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "AdeleV@ww5dl.onmicrosoft.com"]
    m_banneza = ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "LidiaH@ww5dl.onmicrosoft.com", "IsaiahL@ww5dl.onmicrosoft.com", "AdeleV@ww5dl.onmicrosoft.com"]
    m_leon = ["alonso@ww5dl.onmicrosoft.com", "admin@ww5dl.onmicrosoft.com", "LidiaH@ww5dl.onmicrosoft.com", "PattiF@ww5dl.onmicrosoft.com", "IsaiahL@ww5dl.onmicrosoft.com"]

    channels = [
        {"_id": "19:V9L6UbA2VFe687KF-be3mDmUGRFO-xrynXuxweCYBdU1@thread.tacv2", "name": "General", "team_name": "Oviedo", "visibility": "public", "channel_type": "chat", "members": m_oviedo, "description": None, "burnout_mean": None},
        {"_id": "19:05601fabb9c24d0d8b886a81930db632@thread.tacv2", "name": "Backlogs", "team_name": "Oviedo", "visibility": "public", "channel_type": "post", "members": m_oviedo, "description": None, "burnout_mean": None},
        {"_id": "19:fkU-S486HJhltOLqMvIPEjG5ysazsLRRJkTVaUSWR3Q1@thread.tacv2", "name": "General", "team_name": "La Bañeza", "visibility": "public", "channel_type": "chat", "members": m_banneza, "description": None, "burnout_mean": None},
        {"_id": "19:afa71eb9c66f4b60a30c705e393508fb@thread.tacv2", "name": "Backlogs", "team_name": "La Bañeza", "visibility": "public", "channel_type": "post", "members": m_banneza, "description": None, "burnout_mean": None},
        {"_id": "19:qWJHf8j1OmMmc2OvIR2bfHF5Il5ZRNoo6Ou0JvhSzao1@thread.tacv2", "name": "General", "team_name": "León", "visibility": "public", "channel_type": "chat", "members": m_leon, "description": None, "burnout_mean": None},
        {"_id": "19:16ddf8b922294f76b8738c2cd07de9d6@thread.tacv2", "name": "Backlogs", "team_name": "León", "visibility": "public", "channel_type": "post", "members": m_leon, "description": None, "burnout_mean": None}
    ]
    db.channels.insert_many(channels)

    teams = [
        {"_id": "Oviedo", "manager": "alonso@ww5dl.onmicrosoft.com", "visibility": "public", "members": m_oviedo, "channels": ["19:V9L6UbA2VFe687KF-be3mDmUGRFO-xrynXuxweCYBdU1@thread.tacv2", "19:05601fabb9c24d0d8b886a81930db632@thread.tacv2"], "description": None, "burnout_mean": None},
        {"_id": "La Bañeza", "manager": "alonso@ww5dl.onmicrosoft.com", "visibility": "public", "members": m_banneza, "channels": ["19:fkU-S486HJhltOLqMvIPEjG5ysazsLRRJkTVaUSWR3Q1@thread.tacv2", "19:afa71eb9c66f4b60a30c705e393508fb@thread.tacv2"], "description": None, "burnout_mean": None},
        {"_id": "León", "manager": "admin@ww5dl.onmicrosoft.com", "visibility": "public", "members": m_leon, "channels": ["19:qWJHf8j1OmMmc2OvIR2bfHF5Il5ZRNoo6Ou0JvhSzao1@thread.tacv2", "19:16ddf8b922294f76b8738c2cd07de9d6@thread.tacv2"], "description": None, "burnout_mean": None}
    ]
    db.teams.insert_many(teams)

if __name__ == "__main__":
    seed_database()
    print("Database created.")
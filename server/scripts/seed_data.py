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
        {"_id": "alonso@ww5dl.onmicrosoft.com", "name": "Alonso Carrera", "role": "admin", "managed_teams": ["Oviedo", "La Bañeza", "León"], "teams": ["Oviedo", "La Bañeza", "León"]},
        {"_id": "laura.gomez.wss@ww5dl.onmicrosoft.com", "name": "Laura Gómez", "role": "employee", "managed_teams": ["Oviedo"], "teams": ["Oviedo"]},
        {"_id": "carlos.ruiz.wss@ww5dl.onmicrosoft.com", "name": "Carlos Ruiz", "role": "employee", "managed_teams": [], "teams": ["Oviedo"]},
        {"_id": "elena.martinez.wss@ww5dl.onmicrosoft.com", "name": "Elena Martínez", "role": "employee", "managed_teams": [], "teams": ["La Bañeza", "León"]},
        {"_id": "david.castro.wss@ww5dl.onmicrosoft.com", "name": "David Castro", "role": "employee", "managed_teams": [], "teams": ["León"]},
        {"_id": "sara.prieto.wss@ww5dl.onmicrosoft.com", "name": "Sara Prieto", "role": "employee", "managed_teams": [], "teams": ["La Bañeza"]}
    ]
    db.users.insert_many(users)

    m_oviedo = ["alonso@ww5dl.onmicrosoft.com", "laura.gomez.wss@ww5dl.onmicrosoft.com", "carlos.ruiz.wss@ww5dl.onmicrosoft.com"]
    m_banneza = ["alonso@ww5dl.onmicrosoft.com", "elena.martinez.wss@ww5dl.onmicrosoft.com", "sara.prieto.wss@ww5dl.onmicrosoft.com"]
    m_leon = ["alonso@ww5dl.onmicrosoft.com", "elena.martinez.wss@ww5dl.onmicrosoft.com", "david.castro.wss@ww5dl.onmicrosoft.com"]

    channels = [
        {"_id": "19:fekKOuCfsS_r80LHqVBX-e2a9d-AOgTgzRBz8_SY_zQ1@thread.tacv2", "name": "General", "team_name": "Oviedo", "visibility": "public", "channel_type": "chat", "members": m_oviedo, "description": None, "burnout_mean": None},
        {"_id": "19:d620251b96a1462bbc37ff231346e03a@thread.tacv2", "name": "Backlogs", "team_name": "Oviedo", "visibility": "public", "channel_type": "post", "members": m_oviedo, "description": None, "burnout_mean": None},
        {"_id": "19:ZVA-eFd1fFaNzfDQL1VZItsUPd4vct66B8b6zAjgifI1@thread.tacv2", "name": "General", "team_name": "La Bañeza", "visibility": "public", "channel_type": "chat", "members": m_banneza, "description": None, "burnout_mean": None},
        {"_id": "19:K9S9mLknrjv4GPX-hjRGs_59nIfal41Jtw7LNz1dlIM1@thread.tacv2", "name": "Backlogs", "team_name": "La Bañeza", "visibility": "private", "channel_type": "post", "members": m_banneza, "description": None, "burnout_mean": None},
        {"_id": "19:VoMt5dNfALRG4sqbg-3avl70xUqkAT9CuXkBM27ZrzA1@thread.tacv2", "name": "General", "team_name": "León", "visibility": "public", "channel_type": "chat", "members": m_leon, "description": None, "burnout_mean": None},
        {"_id": "19:hUXP3MiobZkf1IRRWafix7QRwYTnr-ubRWSSrIC9gyI1@thread.tacv2", "name": "Backlogs", "team_name": "León", "visibility": "shared", "channel_type": "post", "members": m_leon, "description": None, "burnout_mean": None},
        {"_id": "19:7dQijFm6mtNkuN9vqlOXQTu1Nt1g9-yCvqQrDLm9QmE1@thread.tacv2", "name": "Compartido", "team_name": "León", "visibility": "shared", "channel_type": "chat", "members": m_leon, "description": None, "burnout_mean": None}
    ]
    db.channels.insert_many(channels)

    teams = [
        {"_id": "Oviedo", "managers": ["laura.gomez.wss@ww5dl.onmicrosoft.com", "alonso@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_oviedo, "channels": ["19:fekKOuCfsS_r80LHqVBX-e2a9d-AOgTgzRBz8_SY_zQ1@thread.tacv2", "19:d620251b96a1462bbc37ff231346e03a@thread.tacv2"], "description": None, "burnout_mean": None},
        {"_id": "La Bañeza", "managers": ["alonso@ww5dl.onmicrosoft.com"], "visibility": "private", "members": m_banneza, "channels": ["19:ZVA-eFd1fFaNzfDQL1VZItsUPd4vct66B8b6zAjgifI1@thread.tacv2", "19:K9S9mLknrjv4GPX-hjRGs_59nIfal41Jtw7LNz1dlIM1@thread.tacv2"], "description": None, "burnout_mean": None},
        {"_id": "León", "managers": ["alonso@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_leon, "channels": ["19:VoMt5dNfALRG4sqbg-3avl70xUqkAT9CuXkBM27ZrzA1@thread.tacv2", "19:hUXP3MiobZkf1IRRWafix7QRwYTnr-ubRWSSrIC9gyI1@thread.tacv2", "19:7dQijFm6mtNkuN9vqlOXQTu1Nt1g9-yCvqQrDLm9QmE1@thread.tacv2"], "description": None, "burnout_mean": None}
    ]
    db.teams.insert_many(teams)

if __name__ == "__main__":
    seed_database()
    print("Database created.")
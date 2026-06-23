import os
import random
from datetime import datetime, timedelta
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"

if not MONGO_URI:
    exit()

def generate_mock_scores(base_e, base_c, base_i, noise=0.1):
    e = min(max(base_e + random.uniform(-noise, noise), 0.0), 1.0)
    c = min(max(base_c + random.uniform(-noise, noise), 0.0), 1.0)
    i = min(max(base_i + random.uniform(-noise, noise), 0.0), 1.0)
    b_index = (e + c + i) / 3.0
    
    wbi_e = min(e * random.uniform(1.0, 1.2), 1.0)
    wbi_c = min(c * random.uniform(1.0, 1.2), 1.0)
    wbi_i = min(i * random.uniform(1.0, 1.2), 1.0)
    wbi = (wbi_e + wbi_c + wbi_i) / 3.0
    
    mbi = {
        "exhaustion": round(e, 2),
        "cynicism": round(c, 2),
        "inefficacy": round(i, 2),
        "burnout_index": round(b_index, 2)
    }
    
    wbi_scores = {
        "wbi": round(wbi, 2),
        "wbi_e": round(wbi_e, 2),
        "wbi_c": round(wbi_c, 2),
        "wbi_i": round(wbi_i, 2)
    }
    
    context = {
        "avg_overtime": random.choice([1.0, 1.1, 1.2]),
        "avg_density": round(random.uniform(0.5, 3.5), 2),
        "avg_latency": round(random.uniform(2.0, 15.0), 2)
    }
    
    return mbi, wbi_scores, context

def seed_test_database():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    db.users.drop()
    db.teams.drop()
    db.channels.drop()
    db.messages.drop()
    db.sessions.drop()  
    db.trends.drop()    

    users = [
        {"_id": "alonso@ww5dl.onmicrosoft.com", "name": "Alonso Carrera", "role": "admin", "managed_teams": ["Oviedo", "La Bañeza", "León"], "teams": ["Oviedo", "La Bañeza", "León", "Astorga", "Ponferrada", "Benavente"]},
        {"_id": "laura.gomez.wss@ww5dl.onmicrosoft.com", "name": "Laura Gómez", "role": "employee", "managed_teams": ["Oviedo", "Astorga"], "teams": ["Oviedo", "Astorga"]},
        {"_id": "carlos.ruiz.wss@ww5dl.onmicrosoft.com", "name": "Carlos Ruiz", "role": "employee", "managed_teams": [], "teams": ["Oviedo"]},
        {"_id": "elena.martinez.wss@ww5dl.onmicrosoft.com", "name": "Elena Martínez", "role": "employee", "managed_teams": ["La Bañeza", "León", "Ponferrada"], "teams": ["La Bañeza", "León", "Ponferrada"]},
        {"_id": "david.castro.wss@ww5dl.onmicrosoft.com", "name": "David Castro", "role": "employee", "managed_teams": [], "teams": ["León", "Ponferrada"]},
        {"_id": "sara.prieto.wss@ww5dl.onmicrosoft.com", "name": "Sara Prieto", "role": "employee", "managed_teams": ["Benavente"], "teams": ["La Bañeza", "Benavente"]}
    ]
    db.users.insert_many(users)

    team_profiles = {
        "Oviedo": (0.15, 0.10, 0.12),    
        "La Bañeza": (0.45, 0.40, 0.35), 
        "León": (0.75, 0.80, 0.60),
        "Astorga": (0.30, 0.25, 0.20),
        "Ponferrada": (0.25, 0.30, 0.25),
        "Benavente": (0.20, 0.20, 0.15)
    }

    m_oviedo = ["alonso@ww5dl.onmicrosoft.com", "laura.gomez.wss@ww5dl.onmicrosoft.com", "carlos.ruiz.wss@ww5dl.onmicrosoft.com"]
    m_banneza = ["alonso@ww5dl.onmicrosoft.com", "elena.martinez.wss@ww5dl.onmicrosoft.com", "sara.prieto.wss@ww5dl.onmicrosoft.com"]
    m_leon = ["alonso@ww5dl.onmicrosoft.com", "elena.martinez.wss@ww5dl.onmicrosoft.com", "david.castro.wss@ww5dl.onmicrosoft.com"]
    m_astorga = ["laura.gomez.wss@ww5dl.onmicrosoft.com", "alonso@ww5dl.onmicrosoft.com"]
    m_ponferrada = ["elena.martinez.wss@ww5dl.onmicrosoft.com", "david.castro.wss@ww5dl.onmicrosoft.com"]
    m_benavente = ["sara.prieto.wss@ww5dl.onmicrosoft.com", "alonso@ww5dl.onmicrosoft.com"]

    channels_data = [
        {"_id": "19:fekKOuCfsS_r80LHqVBX-e2a9d-AOgTgzRBz8_SY_zQ1@thread.tacv2", "name": "General", "team_name": "Oviedo", "visibility": "public", "channel_type": "chat", "members": m_oviedo},
        {"_id": "19:d620251b96a1462bbc37ff231346e03a@thread.tacv2", "name": "Backlogs", "team_name": "Oviedo", "visibility": "public", "channel_type": "post", "members": m_oviedo},
        {"_id": "19:ZVA-eFd1fFaNzfDQL1VZItsUPd4vct66B8b6zAjgifI1@thread.tacv2", "name": "General", "team_name": "La Bañeza", "visibility": "public", "channel_type": "chat", "members": m_banneza},
        {"_id": "19:K9S9mLknrjv4GPX-hjRGs_59nIfal41Jtw7LNz1dlIM1@thread.tacv2", "name": "Backlogs", "team_name": "La Bañeza", "visibility": "private", "channel_type": "post", "members": m_banneza},
        {"_id": "19:VoMt5dNfALRG4sqbg-3avl70xUqkAT9CuXkBM27ZrzA1@thread.tacv2", "name": "General", "team_name": "León", "visibility": "public", "channel_type": "chat", "members": m_leon},
        {"_id": "19:hUXP3MiobZkf1IRRWafix7QRwYTnr-ubRWSSrIC9gyI1@thread.tacv2", "name": "Backlogs", "team_name": "León", "visibility": "shared", "channel_type": "post", "members": m_leon},
        {"_id": "19:7dQijFm6mtNkuN9vqlOXQTu1Nt1g9-yCvqQrDLm9QmE1@thread.tacv2", "name": "Compartido", "team_name": "León", "visibility": "shared", "channel_type": "chat", "members": m_leon},
        {"_id": "19:JUDeU2rNE2ptQ_Nq37k8HQ7cTFiHsRzhwbQoQw_bdBs1@thread.tacv2", "name": "Chat", "team_name": "Astorga", "visibility": "public", "channel_type": "chat", "members": m_astorga},
        {"_id": "19:S9mU39ED8aKwRJtJyaOrQp1wcn1SLictDaonHVDbzHg1@thread.tacv2", "name": "Post", "team_name": "Ponferrada", "visibility": "public", "channel_type": "post", "members": m_ponferrada},
        {"_id": "19:a_cwRylXvljSIB1GPxIbdcMjT6CeIFgVWxZIMUUkfSI1@thread.tacv2", "name": "General", "team_name": "Benavente", "visibility": "public", "channel_type": "chat", "members": m_benavente}
    ]

    teams_data = [
        {"_id": "Oviedo", "managers": ["laura.gomez.wss@ww5dl.onmicrosoft.com", "alonso@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_oviedo, "channels": ["19:fekKOuCfsS_r80LHqVBX-e2a9d-AOgTgzRBz8_SY_zQ1@thread.tacv2", "19:d620251b96a1462bbc37ff231346e03a@thread.tacv2"]},
        {"_id": "La Bañeza", "managers": ["alonso@ww5dl.onmicrosoft.com"], "visibility": "private", "members": m_banneza, "channels": ["19:ZVA-eFd1fFaNzfDQL1VZItsUPd4vct66B8b6zAjgifI1@thread.tacv2", "19:K9S9mLknrjv4GPX-hjRGs_59nIfal41Jtw7LNz1dlIM1@thread.tacv2"]},
        {"_id": "León", "managers": ["alonso@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_leon, "channels": ["19:VoMt5dNfALRG4sqbg-3avl70xUqkAT9CuXkBM27ZrzA1@thread.tacv2", "19:hUXP3MiobZkf1IRRWafix7QRwYTnr-ubRWSSrIC9gyI1@thread.tacv2", "19:7dQijFm6mtNkuN9vqlOXQTu1Nt1g9-yCvqQrDLm9QmE1@thread.tacv2"]},
        {"_id": "Astorga", "managers": ["laura.gomez.wss@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_astorga, "channels": ["19:JUDeU2rNE2ptQ_Nq37k8HQ7cTFiHsRzhwbQoQw_bdBs1@thread.tacv2"]},
        {"_id": "Ponferrada", "managers": ["elena.martinez.wss@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_ponferrada, "channels": ["19:S9mU39ED8aKwRJtJyaOrQp1wcn1SLictDaonHVDbzHg1@thread.tacv2"]},
        {"_id": "Benavente", "managers": ["sara.prieto.wss@ww5dl.onmicrosoft.com"], "visibility": "public", "members": m_benavente, "channels": ["19:a_cwRylXvljSIB1GPxIbdcMjT6CeIFgVWxZIMUUkfSI1@thread.tacv2"]}
    ]

    start_date = datetime(2026, 3, 1)
    end_date = datetime(2026, 7, 30)
    total_days = (end_date - start_date).days

    trends = []
    sessions = []
    
    for team in teams_data:
        base_e, base_c, base_i = team_profiles[team["_id"]]
        latest_mbi = None
        latest_wbi = None
        latest_ctx = None
        
        for hours_passed in range(0, total_days * 24 + 1, 6): 
            trend_date = start_date + timedelta(hours=hours_passed)
            mbi, wbi, ctx = generate_mock_scores(base_e, base_c, base_i)
            latest_mbi = mbi
            latest_wbi = wbi
            latest_ctx = ctx
            
            trends.append({
                "targetId": team["_id"],
                "type": "team",
                "date": trend_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "score": mbi,
                "wbi": wbi,
                "context": ctx
            })
        
        team["burnout_mean"] = latest_mbi 
        team["wbi_scores"] = latest_wbi
        team["context_metrics"] = latest_ctx

    for chan in channels_data:
        team_name = chan["team_name"]
        base_e, base_c, base_i = team_profiles[team_name]
        latest_mbi = None
        latest_wbi = None
        latest_ctx = None

        for hours_passed in range(0, total_days * 24 + 1, 6):
            trend_date = start_date + timedelta(hours=hours_passed)
            mbi, wbi, ctx = generate_mock_scores(base_e, base_c, base_i)
            latest_mbi = mbi
            latest_wbi = wbi
            latest_ctx = ctx
            
            trends.append({
                "targetId": chan["_id"],
                "type": "channel",
                "date": trend_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "score": mbi,
                "wbi": wbi,
                "context": ctx
            })
        
        chan["burnout_mean"] = latest_mbi
        chan["wbi_scores"] = latest_wbi
        chan["context_metrics"] = latest_ctx

        for i in range(15):
            random_days = random.randint(0, total_days)
            session_start = start_date + timedelta(days=random_days, hours=random.randint(8, 20))
            session_end = session_start + timedelta(minutes=random.randint(5, 60))
            msg_count = random.randint(3, 40)
            
            sess_mbi, sess_wbi, _ = generate_mock_scores(base_e, base_c, base_i, noise=0.2)
            
            sessions.append({
                "_id": str(uuid.uuid4()),
                "channelId": chan["_id"],
                "teamId": team_name,
                "startTime": session_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endTime": session_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "messageCount": msg_count,
                "overtime_factor": random.choice([1.0, 1.1, 1.2]),
                "density": round(random.uniform(0.5, 3.5), 2),
                "latency": round(random.uniform(2.0, 15.0), 2),
                "sessionScores": sess_mbi,
                "wbi_scores": sess_wbi
            })

    db.channels.insert_many(channels_data)
    db.teams.insert_many(teams_data)
    db.trends.insert_many(trends)
    db.sessions.insert_many(sessions)

if __name__ == "__main__":
    seed_test_database()
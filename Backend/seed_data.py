import pymongo
from pymongo import MongoClient
import sys
import os
from dotenv import load_dotenv
import bcrypt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"

COLLECTION_USERS = "users"
COLLECTION_TEAMS = "teams"

TEAM_A = "Team A"

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

ADMIN_EMAIL = "admin@ww5dl.onmicrosoft.com"
MANAGER_EMAIL = "alonso@ww5dl.onmicrosoft.com"
USER_EMAIL = "adele.vance@ww5dl.onmicrosoft.com"

users = [
    {
        "_id": ADMIN_EMAIL,
        "username": ADMIN_EMAIL,
        "name": "Guillermo Admin",
        "email": ADMIN_EMAIL,
        "password": get_password_hash("password123"),
        "role": "admin",
        "teams": [TEAM_A] 
    },
    {
        "_id": MANAGER_EMAIL,
        "username": MANAGER_EMAIL,
        "name": "Alonso Manager",
        "email": MANAGER_EMAIL,
        "password": get_password_hash("password123"),
        "role": "manager",
        "teams": [TEAM_A] # Todos en Team A
    },
    {
        "_id": USER_EMAIL,
        "username": USER_EMAIL,
        "name": "Adele Vance",
        "email": USER_EMAIL,
        "password": get_password_hash("password123"),
        "role": "user",
        "teams": [TEAM_A] # Todos en Team A
    }
]

teams = [
    {
        "_id": TEAM_A,
        "name": TEAM_A,
        "manager": MANAGER_EMAIL, # Alonso es el manager
        "members": [ADMIN_EMAIL, MANAGER_EMAIL, USER_EMAIL] # Todos son miembros
    }
]

def seed_db():
    if not MONGO_URI:
        print("ERROR: MONGO_URI not found in .env")
        return

    client = None
    try:
        print("Connecting to MongoDB Atlas Cluster...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        client.admin.command('ping')
        print("Connected to Cluster.")

        users_coll = db[COLLECTION_USERS]
        users_coll.delete_many({}) 
        users_coll.insert_many(users)
        print(f"Inserted {len(users)} users.")

        teams_coll = db[COLLECTION_TEAMS]
        teams_coll.delete_many({}) 
        teams_coll.insert_many(teams)
        print(f"Inserted {len(teams)} teams.")
        
        print("\nACCESS SUMMARY")
        print(f"Admin:   {ADMIN_EMAIL}")
        print(f"Manager: {MANAGER_EMAIL}")
        print(f"User:    {USER_EMAIL}")
        print(f"All added to: {TEAM_A}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        if client:
            client.close()
            print("Connection closed.")

if __name__ == "__main__":
    seed_db()
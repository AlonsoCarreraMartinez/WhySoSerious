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

    
    print("Clearing old collections (users, teams)...")
    db.users.drop()
    db.teams.drop()

    default_password = generate_password_hash("password123")

    users = [
       
        {
            "_id": "alonso@ww5dl.onmicrosoft.com",
            "name": "Alonso Carrera",
            "role": "admin",
            "teams": ["Oviedo", "La Bañeza", "León"],
            "password": default_password
        },
        {
            "_id": "admin@ww5dl.onmicrosoft.com",
            "name": "Guillermo Menguez",
            "role": "admin", 
            "teams": ["Oviedo", "La Bañeza", "León"],
            "password": default_password
        },
      
        {
            "_id": "AdeleV@ww5dl.onmicrosoft.com",
            "name": "Adele Vance",
            "role": "employee",
            "teams": ["Oviedo", "La Bañeza"],
            "password": default_password
        },
        {
            "_id": "LidiaH@ww5dl.onmicrosoft.com",
            "name": "Lidia Holloway",
            "role": "employee",
            "teams": ["La Bañeza", "León"],
            "password": default_password
        },
        {
            "_id": "IsaiahL@ww5dl.onmicrosoft.com",
            "name": "Isaiah Langer",
            "role": "employee",
            "teams": ["La Bañeza", "León"],
            "password": default_password
        },
        {
            "_id": "PattiF@ww5dl.onmicrosoft.com",
            "name": "Patti Fernandez",
            "role": "employee",
            "teams": ["León"],
            "password": default_password
        }
    ]

    db.users.insert_many(users)
    print(f"{len(users)} Users created.")

    teams = [
        {
            "_id": "Oviedo",
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": [
                "alonso@ww5dl.onmicrosoft.com", 
                "admin@ww5dl.onmicrosoft.com", 
                "AdeleV@ww5dl.onmicrosoft.com"
            ]
        },
        {
            "_id": "La Bañeza",
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": [
                "alonso@ww5dl.onmicrosoft.com", 
                "admin@ww5dl.onmicrosoft.com", 
                "LidiaH@ww5dl.onmicrosoft.com",
                "IsaiahL@ww5dl.onmicrosoft.com",
                "AdeleV@ww5dl.onmicrosoft.com"
            ]
        },
        {
            "_id": "León",
            "manager": "alonso@ww5dl.onmicrosoft.com",
            "members": [
                "alonso@ww5dl.onmicrosoft.com", 
                "admin@ww5dl.onmicrosoft.com", 
                "LidiaH@ww5dl.onmicrosoft.com",
                "PattiF@ww5dl.onmicrosoft.com",
                "IsaiahL@ww5dl.onmicrosoft.com"
            ]
        }
    ]

    db.teams.insert_many(teams)
    print(f"{len(teams)} Teams created.")
    print("Database ready to receive messages.")

if __name__ == "__main__":
    seed_database()
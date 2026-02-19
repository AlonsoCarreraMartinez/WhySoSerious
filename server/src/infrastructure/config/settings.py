import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Azure / Graph API
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    

# Singleton instance to be used across the infrastructure layer.
settings = Settings()
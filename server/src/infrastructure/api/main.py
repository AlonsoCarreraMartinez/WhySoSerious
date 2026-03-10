from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.api.routers import teams, burnout, channels 
from infrastructure.external.scheduler.scheduler import TaskScheduler
from application.services.sync_service import SyncService
from application.services.burnout_service import BurnoutService
from infrastructure.persistence.repositories.mongo_message_repository import MongoMessageRepository
from infrastructure.persistence.repositories.mongo_team_repository import MongoTeamRepository
from infrastructure.persistence.repositories.mongo_channel_repository import MongoChannelRepository
from infrastructure.persistence.repositories.mongo_burnout_repository import MongoBurnoutRepository
from infrastructure.external.azure.azure_teams_provider import AzureTeamsProvider

# python -m venv .venv
# uvicorn src.infrastructure.api.main:app --reload
# set PYTHONPATH=src && uvicorn infrastructure.api.main:app --reload
# http://127.0.0.1:8000/


# Initialize the FastAPI application instance.
app = FastAPI(title="WhySoSerious")

# Configure CORS to allow requests from the React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection.
message_repo = MongoMessageRepository()
team_repo = MongoTeamRepository()
channel_repo = MongoChannelRepository()
burnout_repo = MongoBurnoutRepository()
azure_provider = AzureTeamsProvider()

sync_service = SyncService(message_repo, azure_provider, burnout_repo)
burnout_service = BurnoutService(message_repo, team_repo, channel_repo, burnout_repo)

# Initialize the Background Task Scheduler to manage automated Cron Jobs.
task_scheduler = TaskScheduler(sync_service, burnout_service)


# Launch the background scheduler to start syncing and analyzing data automatically.
@app.on_event("startup")
async def startup_event():

    task_scheduler.start()
    print("Backend started and Cron Jobs scheduled")

# Routers.
app.include_router(teams.router, prefix="/api")
app.include_router(burnout.router, prefix="/api")
app.include_router(channels.router, prefix="/api")





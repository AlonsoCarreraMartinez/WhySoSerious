from infrastructure.external.azure.azure_teams_provider import AzureTeamsProvider
from infrastructure.persistence.repositories.mongo_team_repository import MongoTeamRepository
from infrastructure.persistence.repositories.mongo_burnout_repository import MongoBurnoutRepository
from infrastructure.persistence.repositories.mongo_channel_repository import MongoChannelRepository
from infrastructure.persistence.repositories.mongo_user_repository import MongoUserRepository
from application.services.auth_service import AuthService

# Singleton instances.
azure_provider = AzureTeamsProvider()
team_repository = MongoTeamRepository()
burnout_repository = MongoBurnoutRepository()
channel_repository = MongoChannelRepository()
user_repository = MongoUserRepository()
auth_service = AuthService(azure_provider, team_repository, user_repository)

# Returns the AuthService instance to be used by routers.
def get_auth_service() -> AuthService:
    return auth_service

# Returns the TeamRepository instance to be used by routers.
def get_team_repository() -> MongoTeamRepository:
    return team_repository

# Returns the BurnoutRepository instance to be used by routers.
def get_burnout_repository() -> MongoBurnoutRepository:
    return burnout_repository

# Returns the ChannelRepository instance to be used by routers.
def get_channel_repository() -> MongoChannelRepository:
    return channel_repository

# Returns the UserRepository instance to be used by routers.
def get_user_repository() -> MongoUserRepository:
    return user_repository
from infrastructure.external.azure.azure_teams_provider import AzureTeamsProvider
from infrastructure.persistence.repositories.mongo_team_repository import MongoTeamRepository
from application.services.auth_service import AuthService

# Singleton instances.
azure_provider = AzureTeamsProvider()
team_repository = MongoTeamRepository()
auth_service = AuthService(azure_provider)

# Returns the AuthService instance to be used by routers.
def get_auth_service() -> AuthService:
    
    return auth_service

# Returns the TeamRepository instance to be used by routers.
def get_team_repository() -> MongoTeamRepository:

    return team_repository
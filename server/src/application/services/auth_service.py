from domain.ports import TeamsProvider
from infrastructure.persistence.repositories.mongo_team_repository import MongoTeamRepository
from application.dtos import AuthStatusDTO

class AuthService:

    # Initializes the service with the Azure provider and Mongo repository.
    def __init__(self, teams_provider: TeamsProvider, team_repository: MongoTeamRepository):
        
        self.teams_provider = teams_provider
        self.team_repository = team_repository

    # Validates user access by checking Azure and cross-referencing with MongoDB data.
    def validate_user_access(self, email: str) -> AuthStatusDTO:
    
        if not email:
            return AuthStatusDTO(
                in_org=False, 
                is_admin=False, 
                is_owner=False, 
                auth_message="No email provided"
            )

        azure_info = self.teams_provider.get_user_permissions(email)

        if not azure_info["in_org"]:
            return AuthStatusDTO(
                in_org=False, 
                is_admin=False, 
                is_owner=False,
                auth_message="You do not belong to this organization."
            )

        if azure_info["is_admin"]:
            all_teams = self.team_repository.get_all_teams()
            if not all_teams:
                return AuthStatusDTO(
                    in_org=True, 
                    is_admin=True, 
                    is_owner=False,
                    auth_message="System is empty. No analyzed data found."
                )
            return AuthStatusDTO(in_org=True, is_admin=True, is_owner=False)

        if azure_info["is_owner"]:
            owned_ids = azure_info.get("owned_teams", [])
            db_teams = self.team_repository.get_teams_by_external_ids(owned_ids)
            if not db_teams:
                return AuthStatusDTO(
                    in_org=True, 
                    is_admin=False, 
                    is_owner=True,
                    auth_message="The teams you manage are empty. No analyzed data found."
                )

            return AuthStatusDTO(
                in_org=True, 
                is_admin=False, 
                is_owner=True,
                managed_teams=[t.name for t in db_teams]
            )

        return AuthStatusDTO(
            in_org=True, 
            is_admin=False, 
            is_owner=False,
            auth_message="You do not have access to this data."
        )
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
    
    # Temporary bypass method to evaluate user role directly from DB
    def verify_user_role_bypass(self, email: str) -> AuthStatusDTO:
        user_email = email.lower().strip()
        
        GLOBAL_ADMINS = ["alonso@ww5dl.onmicrosoft.com"] # Temporary list of global administrators (replace with your actual email)
        
        is_admin = user_email in GLOBAL_ADMINS
        
        managed_teams_docs = self.team_repository.get_teams_by_manager(user_email)
        managed_teams_names = [team.name for team in managed_teams_docs]
        
        is_owner = len(managed_teams_names) > 0
        
        if is_admin:
            auth_message = "Global Administrator"
        elif is_owner:
            auth_message = "Team Lead"
        else:
            auth_message = "Employee"

        return AuthStatusDTO(
            in_org=True, 
            is_admin=is_admin,
            is_owner=is_owner,
            managed_teams=managed_teams_names,
            auth_message=auth_message
        )
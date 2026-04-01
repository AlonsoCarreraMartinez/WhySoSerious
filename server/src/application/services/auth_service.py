from domain.ports import TeamsProvider, UserRepository
from infrastructure.persistence.repositories.mongo_team_repository import MongoTeamRepository
from application.dtos import AuthStatusDTO

class AuthService:

    # Initializes the service with the Azure provider and Mongo repository.
    def __init__(self, teams_provider: TeamsProvider, team_repository: MongoTeamRepository, user_repository: UserRepository):
        
        self.teams_provider = teams_provider
        self.team_repository = team_repository
        self.user_repository = user_repository

    # Validates user access by checking Azure and cross-referencing with MongoDB data.
    def validate_user_access(self, email: str) -> AuthStatusDTO:
    
        if not email:
            return AuthStatusDTO(
                in_org=False, 
                is_admin=False, 
                is_owner=False, 
                auth_message="No email provided"
            )

        db_user = self.user_repository.get_by_email(email)
        real_role = db_user.role.capitalize() if db_user else "Employee"

        azure_info = self.teams_provider.get_user_permissions(email)

        if not azure_info.get("in_org"):
            return AuthStatusDTO(
                in_org=False, 
                is_admin=False, 
                is_owner=False,
                auth_message="You do not belong to this organization.",
                db_role=real_role
            )

        if azure_info.get("is_admin"):
            all_teams = self.team_repository.get_all()
            if not all_teams:
                return AuthStatusDTO(
                    in_org=True, 
                    is_admin=True, 
                    is_owner=False,
                    auth_message="System is empty. No analyzed data found.",
                    db_role=real_role
                )
            
            teams_data = [{"name": t.name, "visibility": t.visibility} for t in all_teams]
            return AuthStatusDTO(in_org=True, is_admin=True, is_owner=False, managed_teams=teams_data, db_role=real_role)

        if azure_info.get("is_owner"):
            db_teams = self.team_repository.get_by_manager(email)
            if not db_teams:
                return AuthStatusDTO(
                    in_org=True, 
                    is_admin=False, 
                    is_owner=True,
                    auth_message="The teams you manage are empty. No analyzed data found.",
                    db_role=real_role
                )

            teams_data = [{"name": t.name, "visibility": t.visibility} for t in db_teams]
            return AuthStatusDTO(
                in_org=True, 
                is_admin=False, 
                is_owner=True,
                managed_teams=teams_data,
                db_role=real_role
            )

        return AuthStatusDTO(
            in_org=True, 
            is_admin=False, 
            is_owner=False,
            auth_message="You do not have access to this data.",
            db_role=real_role
        )
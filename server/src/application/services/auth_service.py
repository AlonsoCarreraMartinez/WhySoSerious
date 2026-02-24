from domain.ports import TeamsProvider

class AuthService:
    
    # inject the interface
    def __init__(self, teams_provider: TeamsProvider):
        self.teams_provider = teams_provider

    # Validates via Azure if the user exists in the organization
    def validate_user_access(self, email: str) -> dict:

        if not email:
            return {"in_org": False, "is_admin": False, "managed_teams": []}
            
        return self.teams_provider.get_user_permissions(email) # ESTAMOS USANDO UN PLACEHOLDER.
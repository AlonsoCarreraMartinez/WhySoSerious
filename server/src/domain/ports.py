from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User, Team, Channel, Message, BertScores

class UserRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: # Fetch user details by ID
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: # Fetch user by email for authentication
        pass

class TeamRepository(ABC):

    @abstractmethod
    def get_by_id(self, team_id: str) -> Optional[Team]: # Fetch team details by ID
        pass

    @abstractmethod
    def get_by_manager(self, manager: str) -> List[Team]: # Get all teams managed by a specific user
        pass

    @abstractmethod
    def update_burnout_metrics(self, team_id: str, scores: BertScores): # Update teams's bert scores.
        pass

class ChannelRepository(ABC):

    @abstractmethod
    def get_by_team(self, team_name: str) -> List[Channel]: # List all channels belonging to a team
        pass

    @abstractmethod
    def update_burnout_metrics(self, channel_id: str, scores: BertScores): # Update channel's bert scores.
        pass

class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: Message): # Save new messages.
        pass

    @abstractmethod
    def get_unanalyzed(self) -> List[Message]: # Fetch messages pending to analyze.
        pass

    @abstractmethod
    def update_scores(self, message_id: str, scores: BertScores): # Save BERT scores and mark as analyzed.
        pass

    def get_last_sync_timestamp(self, channel_id: str) -> Optional[str]: # Returns the timestamp of the last message saved for a specific channel.
        pass

# Port for external Microsoft Graph API communication (application/services/sync_service)
class TeamsProvider(ABC):

    @abstractmethod
    def get_all_teams(self) -> List[dict]: # Fetch all teams from Microsoft Graph.
        pass

    @abstractmethod
    def get_channels(self, team_id: str) -> List[dict]: # Fetch channels for a specific team.
        pass

    @abstractmethod
    def get_new_messages(self, team_id: str, channel_id: str, last_sync: Optional[str]) -> List[Message]: #Fetch new messages since the last synchronization date.
        pass

    

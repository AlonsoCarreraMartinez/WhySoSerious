from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User, Team, Channel, Message, BertScores


class UserRepository(ABC):
    
    # Fetch user details by ID.
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: 
        pass

    # Fetch user by email for authentication.
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: 
        pass


class TeamRepository(ABC):

    # Fetch team details by ID.
    @abstractmethod
    def get_by_id(self, team_id: str) -> Optional[Team]: 
        pass

    # Get all teams managed by a specific user.
    @abstractmethod
    def get_by_manager(self, manager: str) -> List[Team]: 
        pass

    # Update teams's bert scores.
    @abstractmethod
    def update_burnout_metrics(self, team_id: str, scores: BertScores): 
        pass

    # Fetches all teams stored in the database.
    @abstractmethod
    def get_all(self) -> List[Team]:
        pass


class ChannelRepository(ABC):

    # List all channels belonging to a team.
    @abstractmethod
    def get_by_team(self, team_name: str) -> List[Channel]: 
        pass

    # Update channel's bert scores.
    @abstractmethod
    def update_burnout_metrics(self, channel_id: str, scores: BertScores): 
        pass


class MessageRepository(ABC):

    # Save new messages.
    @abstractmethod
    def save(self, message: Message): 
        pass

    # Fetch messages pending to analyze.
    @abstractmethod
    def get_unanalyzed(self) -> List[Message]: 
        pass

    # Save BERT scores and mark as analyzed.
    @abstractmethod
    def update_scores(self, message_id: str, scores: BertScores): 
        pass

    # Returns the timestamp of the last message saved for a specific channel.
    @abstractmethod
    def get_last_sync_timestamp(self, channel_id: str) -> Optional[str]: 
        pass


class TeamsProvider(ABC):

    # Fetch all teams from Microsoft Graph.
    @abstractmethod
    def get_all_teams(self) -> List[dict]: 
        pass

    # Fetch channels for a specific team.
    @abstractmethod
    def get_channels(self, team_id: str) -> List[dict]: 
        pass

    # Fetch new messages since the last synchronization date.
    @abstractmethod
    def get_new_messages(self, team_id: str, channel_id: str, last_sync: Optional[str]) -> List[Message]: 
        pass

    # Checks if users exist, if users are Admin, and which teams they own.
    @abstractmethod
    def get_user_permissions(self, email: str) -> dict: 
        pass

    # Cleans HTML tags from the message body content.
    @abstractmethod
    def clean_message_content(self, raw_html: str) -> str: 
        pass

    # Map a Graph API message dictionary to a domain Message model.
    @abstractmethod
    def map_to_domain_message(self, data: dict, team_id: str, channel_id: str) -> Message: 
        pass
    

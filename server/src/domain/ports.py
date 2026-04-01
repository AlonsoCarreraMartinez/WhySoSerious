from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User, Team, Channel, Message, MBIScores, ConversationSession, HealthTrend, Notification


class UserRepository(ABC):
    
    # Fetch user details by ID.
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: 
        pass

    # Fetch user by email for authentication.
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: 
        pass

    # Fetches multiple users by a list of their IDs or Emails.
    @abstractmethod
    def get_by_ids(self, user_ids: List[str]) -> List[User]:
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
    def update_burnout_metrics(self, team_id: str, scores: MBIScores): 
        pass

    # Fetches all teams stored in the database.
    @abstractmethod
    def get_all(self) -> List[Team]:
        pass

    # Fetches all teams where a specific email is listed in the managers array.
    @abstractmethod
    def get_teams_by_manager(self, manager_email: str) -> List[Team]:
        pass

class ChannelRepository(ABC):

    # List all channels belonging to a team.
    @abstractmethod
    def get_by_team(self, team_name: str) -> List[Channel]: 
        pass

    # Update channel's bert scores.
    @abstractmethod
    def update_burnout_metrics(self, channel_id: str, scores: MBIScores): 
        pass

    # Fetches all channels stored in the database.
    @abstractmethod
    def get_all(self) -> List[Channel]:
        pass

    # Fetch a single channel by its ID.
    @abstractmethod
    def get_by_id(self, channel_id: str) -> Optional[Channel]:
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

    # Returns the timestamp of the last message saved for a specific channel.
    @abstractmethod
    def get_last_sync_timestamp(self, channel_id: str) -> Optional[str]: 
        pass

    # Returns the last message saved for a specific channel to compare timestamps.
    @abstractmethod
    def get_last_message_by_channel(self, channel_id: str) -> Optional[Message]:
        pass

    # Marks a list of messages as analyzed and clears their content for privacy.
    @abstractmethod
    def mark_as_analyzed(self, message_ids: List[str]): 
        pass

    # Retrieves the last N messages from a channel before a specific timestamp.
    @abstractmethod
    def get_previous_messages(self, channel_id: str, start_time_str: str, limit: int = 5) -> List[Message]:
        pass


class BurnoutRepository(ABC):

    # Saves or updates a conversation session.
    @abstractmethod
    def save_session(self, session: ConversationSession): 
        pass

    # Retrieves all sessions for a specific channel.
    @abstractmethod
    def get_sessions_by_channel(self, channel_id: str) -> List[ConversationSession]: 
        pass

    # Saves a health trend point for historical charts.
    @abstractmethod
    def save_trend(self, trend: HealthTrend): 
        pass

    # Retrieves historical health trend records for a specific target within a given timeframe.
    @abstractmethod
    def get_trends(self, target_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[HealthTrend]: 
        pass


class NotificationRepository(ABC):

    # Saves a notification to the database.
    @abstractmethod
    def save(self, notification: Notification): 
        pass

    # Retrieves notifications applicable to a specific user based on their roles.
    @abstractmethod
    def get_for_user(self, is_admin: bool, managed_teams: List[str]) -> List[Notification]: 
        pass

    # Marks a notification as read for a specific user email.
    @abstractmethod
    def mark_as_read(self, notification_id: str, email: str): 
        pass


class NotificationObserver(ABC):

    # Notifies when the synchronization process finishes.
    @abstractmethod
    def on_sync_completed(self, message_count: int): 
        pass

    # Notifies when a team or channel crosses the critical burnout threshold.
    @abstractmethod
    def on_critical_burnout(self, target_name: str, parent_team: str, score: float, is_channel: bool): 
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
    def map_to_domain_message(self, data: dict, team_id: str, channel_id: str, parent_id: Optional[str] = None) -> Optional[Message]:
        pass
    

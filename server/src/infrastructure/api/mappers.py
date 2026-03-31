from application.dtos import TeamDashboardResponseDTO, ChannelDashboardResponseDTO, HistoricalDataPointDTO, MemberResponseDTO
from domain.models import Team, Channel, HealthTrend, User
from datetime import datetime

# Helper to determine the string value for the frontend colors based on the percentage score.
def get_burnout_level(score: int) -> str:
    if score >= 75: return "critical"
    if score >= 50: return "high"
    if score >= 25: return "moderate"
    return "low"

# Transforms a Team domain model into a Dashboard DTO for frontend views.
def map_team_to_dashboard_dto(team: Team) -> TeamDashboardResponseDTO:
    b_score = int(team.burnout_mean.burnout_index * 100) if team.burnout_mean else 0
    exhaustion = int(team.burnout_mean.exhaustion * 100) if team.burnout_mean else 0
    cynicism = int(team.burnout_mean.cynicism * 100) if team.burnout_mean else 0
    inefficacy = int(team.burnout_mean.inefficacy * 100) if team.burnout_mean else 0
    
    return TeamDashboardResponseDTO(
        id=team.name, 
        name=team.name,
        visibility=team.visibility,
        memberCount=len(team.members),
        burnoutScore=b_score,
        burnoutLevel=get_burnout_level(b_score),
        exhaustion=exhaustion,
        cynicism=cynicism,
        inefficacy=inefficacy
    )

# Transforms a Channel domain model into a Dashboard DTO for frontend views.
def map_channel_to_dashboard_dto(channel: Channel) -> ChannelDashboardResponseDTO:
    b_score = int(channel.burnout_mean.burnout_index * 100) if channel.burnout_mean else 0
    exhaustion = int(channel.burnout_mean.exhaustion * 100) if channel.burnout_mean else 0
    cynicism = int(channel.burnout_mean.cynicism * 100) if channel.burnout_mean else 0
    inefficacy = int(channel.burnout_mean.inefficacy * 100) if channel.burnout_mean else 0
    
    return ChannelDashboardResponseDTO(
        id=channel.id,
        teamId=channel.team_name,
        name=channel.name,
        visibility=channel.visibility,
        memberCount=len(channel.members),
        burnoutScore=b_score,
        burnoutLevel=get_burnout_level(b_score),
        exhaustion=exhaustion,
        cynicism=cynicism,
        inefficacy=inefficacy
    )

# Transforms a HealthTrend domain model into a HistoricalDataPointDTO for frontend charts.
def map_trend_to_historical_dto(trend: HealthTrend) -> HistoricalDataPointDTO:
    date_obj = datetime.strptime(trend.date, "%Y-%m-%dT%H:%M:%SZ")
    formatted_date = date_obj.strftime("%b %d") 
    
    return HistoricalDataPointDTO(
        date=formatted_date,
        score=int(trend.score.burnout_index * 100),
        exhaustion=int(trend.score.exhaustion * 100),
        cynicism=int(trend.score.cynicism * 100),
        inefficacy=int(trend.score.inefficacy * 100)
    )

# Transforms a User domain model into a MemberResponseDTO, assigning the correct role.
def map_user_to_member_dto(user: User, is_manager: bool) -> MemberResponseDTO:
    user_email = getattr(user, 'email', '')
    user_name = getattr(user, 'name', user_email.split('@')[0]) 
    
    return MemberResponseDTO(
        id=user_email,
        name=user_name,
        email=user_email,
        role="Manager" if is_manager else "Member"
    )
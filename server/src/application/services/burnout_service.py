import uuid
from typing import List, Dict
from datetime import datetime
from domain.models import MBIScores, Message, ConversationSession
from domain.ports import MessageRepository, TeamRepository, ChannelRepository, BurnoutRepository
from src.infrastructure.ml.bert_inference import BertPredictor

class BurnoutService:

    # Inject repository interfaces through the constructor.
    def __init__(
        self, 
        message_repo: MessageRepository, 
        team_repo: TeamRepository, 
        channel_repo: ChannelRepository,
        burnout_repo: BurnoutRepository 
    ):
        
        # Store repositories and initialize the local AI model.
        self.message_repo = message_repo
        self.team_repo = team_repo
        self.channel_repo = channel_repo
        self.burnout_repo = burnout_repo
        self.predictor = BertPredictor()


    # Group unanalyzed messages into sessions, analyze them, and purge text.
    def analyze_data(self):
    
        unanalyzed_messages = self.message_repo.get_unanalyzed()
        
        if not unanalyzed_messages:
            print("No new messages.")
            return

        print(f"Batching {len(unanalyzed_messages)} new messages into sessions...")

        sessions_data = {}
        for msg in unanalyzed_messages:
            if not msg.content or not msg.sessionId:
                continue
            
            sid = msg.sessionId
            if sid not in sessions_data:
                sessions_data[sid] = {"channelId": msg.channelId, "teamId": msg.teamId, "msgs": []}
            
            sessions_data[sid]["msgs"].append(msg)

        for session_id, data in sessions_data.items():
            msgs = data["msgs"]
            channel_id = data["channelId"]
            team_id = data["teamId"]
            
            session_text = " ".join([m.content for m in msgs])
            
            results = self.predictor.extract_content_features(session_text)
            scores = MBIScores(**results)
            
            session = ConversationSession(
                _id=session_id,  
                channelId=channel_id,
                teamId=team_id,
                startTime=msgs[0].timestamp, 
                endTime=msgs[-1].timestamp, 
                messageCount=len(msgs),
                sessionScores=scores
            )
            self.burnout_repo.save_session(session)
            
            msg_ids = [m.externalId for m in msgs]
            self.message_repo.mark_as_analyzed(msg_ids)
            print(f"Session {session_id} analyzed and {len(msgs)} messages purged.")

        print("Updating global team and channel scores...")
        self.update_global_scores()
        print("Analysis complete.")

    # Calculate true mathematical means using Sessions (Not individual messages).
    def update_global_scores(self):
        
        teams = self.team_repo.get_all()

        for team in teams:
            
            channels = self.channel_repo.get_by_team(team.name) 
            if not channels:
                continue
                
            team_sums = {"e": 0.0, "c": 0.0, "i": 0.0, "b": 0.0}
            team_session_count = 0

            for channel in channels:
                
                sessions = self.burnout_repo.get_sessions_by_channel(channel.id)
                if not sessions:
                    continue

                chan_sums = {"e": 0.0, "c": 0.0, "i": 0.0, "b": 0.0}
                valid_chan_sessions = 0
                
                for s in sessions:
                    if s.sessionScores:
                        chan_sums["e"] += s.sessionScores.exhaustion
                        chan_sums["c"] += s.sessionScores.cynicism
                        chan_sums["i"] += s.sessionScores.inefficacy
                        chan_sums["b"] += s.sessionScores.burnout_index
                        valid_chan_sessions += 1

                if valid_chan_sessions > 0:
                    
                    mean_chan = MBIScores(
                        exhaustion=round(chan_sums["e"] / valid_chan_sessions, 2),
                        cynicism=round(chan_sums["c"] / valid_chan_sessions, 2),
                        inefficacy=round(chan_sums["i"] / valid_chan_sessions, 2),
                        burnout_index=round(chan_sums["b"] / valid_chan_sessions, 2)
                    )
                    
                    self.channel_repo.update_burnout_metrics(channel.id, mean_chan)
                    print(f"  > Metrics updated for Channel: '{channel.name}'")

                    team_sums["e"] += chan_sums["e"]
                    team_sums["c"] += chan_sums["c"]
                    team_sums["i"] += chan_sums["i"]
                    team_sums["b"] += chan_sums["b"]
                    team_session_count += valid_chan_sessions

            if team_session_count > 0:
                mean_team = MBIScores(
                    exhaustion=round(team_sums["e"] / team_session_count, 2),
                    cynicism=round(team_sums["c"] / team_session_count, 2),
                    inefficacy=round(team_sums["i"] / team_session_count, 2),
                    burnout_index=round(team_sums["b"] / team_session_count, 2)
                )
                
                self.team_repo.update_burnout_metrics(team.name, mean_team)
                print(f"Metrics updated for Team: {team.name}")
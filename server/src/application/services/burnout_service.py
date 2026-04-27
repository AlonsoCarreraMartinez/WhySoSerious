import uuid
from typing import List, Dict
from datetime import datetime
from domain.models import MBIScores, Message, ConversationSession
from domain.ports import MessageRepository, TeamRepository, ChannelRepository, BurnoutRepository, HealthTrend, NotificationObserver
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
        self.observers: List[NotificationObserver] = []

    # Adds an observer to listen for burnout alerts.
    def add_observer(self, observer: NotificationObserver):
        self.observers.append(observer)

    # Calculates Overtime, Density, and Latency based on session timestamps.
    def extract_context_features(self, start_time_str: str, end_time_str: str, message_count: int):
        
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        try:
            
            start_t = datetime.strptime(start_time_str[:19] + "Z", fmt)
            end_t = datetime.strptime(end_time_str[:19] + "Z", fmt)
            
            duration_minutes = (end_t - start_t).total_seconds() / 60.0
            duration_minutes = max(1.0, duration_minutes) 
        except Exception:
            start_t = datetime.utcnow()
            duration_minutes = 1.0

        hour = start_t.hour
        is_weekend = start_t.weekday() >= 5 
        
        if is_weekend:
            overtime_factor = 1.2 
        elif hour < 8 or hour >= 18:
            overtime_factor = 1.1 
        else:
            overtime_factor = 1.0 

        density = round(message_count / duration_minutes, 2)

        latency = round(duration_minutes / (message_count - 1), 2) if message_count > 1 else 0.0

        return overtime_factor, density, latency, duration_minutes


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
                sessions_data[sid] = {
                    "channelId": msg.channelId, 
                    "teamId": msg.teamId, 
                    "channelName": msg.channelName,
                    "msgs": []
                }
            
            sessions_data[sid]["msgs"].append(msg)

        for session_id, data in sessions_data.items():
            msgs = data["msgs"]
            channel_id = data["channelId"]
            team_id = data["teamId"]
            channel_name = data.get("channelName", "")
            
            start_time = msgs[0].timestamp
            end_time = msgs[-1].timestamp
            message_count = len(msgs)

            current_text = " ".join([m.content for m in msgs if m.content])
            session_text = current_text 
 
            is_chat = True 
            
            if is_chat:
                context_msgs = self.message_repo.get_previous_messages(channel_id, start_time, limit=5)
                if context_msgs:
                    context_text = " ".join([m.content for m in context_msgs if m.content])
                    session_text = f"[CONTEXTO PREVIO] {context_text} [SESIÓN ACTUAL] {current_text}"
            
            results = self.predictor.extract_content_features(session_text)
            
            e_val = results.get("exhaustion", 0.0)
            c_val = results.get("cynicism", 0.0)
            i_val = results.get("inefficacy", 0.0)
            b_index = results.get("burnout_index", 0.0)

            overtime_f, density_f, latency_f, duration_mins = self.extract_context_features(
                start_time, end_time, message_count
            )

            overtime_penalty = round(overtime_f - 1.0, 2)
            density_penalty = min(0.30, density_f * 0.05)
            latency_penalty = min(0.30, latency_f * 0.002)

            wbi_e = round(e_val + ((1.0 - e_val) * min(1.0, overtime_penalty + density_penalty)), 2)
            wbi_c = round(c_val + ((1.0 - c_val) * latency_penalty), 2)
            wbi_i = round(i_val + ((1.0 - i_val) * density_penalty), 2)

            wbi_final = round((wbi_e + wbi_c + wbi_i) / 3.0, 2)

            scores = MBIScores(
                exhaustion=e_val,
                cynicism=c_val,
                inefficacy=i_val,
                burnout_index=b_index,
                wbi=wbi_final,
                wbi_e=wbi_e,
                wbi_c=wbi_c,
                wbi_i=wbi_i
            )
            
            session = ConversationSession(
                id=session_id,  
                channelId=channel_id,
                teamId=team_id,
                startTime=start_time, 
                endTime=end_time, 
                messageCount=message_count,
                sessionScores=scores,
                overtime_factor=overtime_f,
                density=density_f,
                latency=latency_f
            )
            self.burnout_repo.save_session(session)
            
            msg_ids = [m.id for m in msgs]
            self.message_repo.mark_as_analyzed(msg_ids)
            print(f"Session {session_id} analyzed and {len(msgs)} messages purged.")

        print("Updating global team and channel scores...")
        self.update_global_scores()
        print("Analysis complete.")

    # Calculate mathematical means using Sessions.
    def update_global_scores(self):
        teams = self.team_repo.get_all()

        for team in teams:
            was_critical_team = team.burnout_mean.burnout_index >= 0.75 if team.burnout_mean else False
            
            channels = self.channel_repo.get_by_team(team.name) 
            if not channels:
                continue
                
            team_sums = {"e": 0.0, "c": 0.0, "i": 0.0, "b": 0.0, "w": 0.0, "we": 0.0, "wc": 0.0, "wi": 0.0}
            team_session_count = 0

            for channel in channels:
                was_critical_chan = channel.burnout_mean.burnout_index >= 0.75 if channel.burnout_mean else False
                
                sessions = self.burnout_repo.get_sessions_by_channel(channel.id)
                if not sessions:
                    continue

                chan_sums = {"e": 0.0, "c": 0.0, "i": 0.0, "b": 0.0, "w": 0.0, "we": 0.0, "wc": 0.0, "wi": 0.0}
                valid_chan_sessions = 0
                
                for s in sessions:
                    if s.sessionScores:
                        chan_sums["e"] += s.sessionScores.exhaustion
                        chan_sums["c"] += s.sessionScores.cynicism
                        chan_sums["i"] += s.sessionScores.inefficacy
                        chan_sums["b"] += s.sessionScores.burnout_index
                        chan_sums["w"] += getattr(s.sessionScores, 'wbi', 0.0) or 0.0 
                        chan_sums["we"] += getattr(s.sessionScores, 'wbi_e', s.sessionScores.exhaustion) or 0.0
                        chan_sums["wc"] += getattr(s.sessionScores, 'wbi_c', s.sessionScores.cynicism) or 0.0
                        chan_sums["wi"] += getattr(s.sessionScores, 'wbi_i', s.sessionScores.inefficacy) or 0.0
                        
                        valid_chan_sessions += 1

                if valid_chan_sessions > 0:
                    mean_chan = MBIScores(
                        exhaustion=round(chan_sums["e"] / valid_chan_sessions, 2),
                        cynicism=round(chan_sums["c"] / valid_chan_sessions, 2),
                        inefficacy=round(chan_sums["i"] / valid_chan_sessions, 2),
                        burnout_index=round(chan_sums["b"] / valid_chan_sessions, 2),
                        wbi=round(chan_sums["w"] / valid_chan_sessions, 2),
                        wbi_e=round(chan_sums["we"] / valid_chan_sessions, 2),
                        wbi_c=round(chan_sums["wc"] / valid_chan_sessions, 2),
                        wbi_i=round(chan_sums["wi"] / valid_chan_sessions, 2)
                    )
                    
                    self.channel_repo.update_burnout_metrics(channel.id, mean_chan)
                    print(f"  > Metrics updated for Channel: '{channel.name}'")

                    is_critical_chan = mean_chan.burnout_index >= 0.75
                    if is_critical_chan and not was_critical_chan:
                        for obs in self.observers:
                            obs.on_critical_burnout(channel.name, team.name, mean_chan.burnout_index, True)

                    chan_trend = HealthTrend(
                        targetId=channel.id,
                        date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        score=mean_chan,
                        type="channel"
                    )
                    self.burnout_repo.save_trend(chan_trend)

                    team_sums["e"] += chan_sums["e"]
                    team_sums["c"] += chan_sums["c"]
                    team_sums["i"] += chan_sums["i"]
                    team_sums["b"] += chan_sums["b"]
                    team_sums["w"] += chan_sums["w"]
                    team_sums["we"] += chan_sums["we"]
                    team_sums["wc"] += chan_sums["wc"]
                    team_sums["wi"] += chan_sums["wi"]

                    team_session_count += valid_chan_sessions

            if team_session_count > 0:
                mean_team = MBIScores(
                    exhaustion=round(team_sums["e"] / team_session_count, 2),
                    cynicism=round(team_sums["c"] / team_session_count, 2),
                    inefficacy=round(team_sums["i"] / team_session_count, 2),
                    burnout_index=round(team_sums["b"] / team_session_count, 2),
                    wbi=round(team_sums["w"] / team_session_count, 2),
                    wbi_e=round(team_sums["we"] / team_session_count, 2),
                    wbi_c=round(team_sums["wc"] / team_session_count, 2),
                    wbi_i=round(team_sums["wi"] / team_session_count, 2)
                )
                
                self.team_repo.update_burnout_metrics(team.name, mean_team)
                print(f"Metrics updated for Team: {team.name}")

                is_critical_team = mean_team.burnout_index >= 0.75
                if is_critical_team and not was_critical_team:
                    for obs in self.observers:
                        obs.on_critical_burnout(team.name, team.name, mean_team.burnout_index, False)

                team_trend = HealthTrend(
                    targetId=team.name,
                    date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    score=mean_team,
                    type="team"
                )
                self.burnout_repo.save_trend(team_trend)
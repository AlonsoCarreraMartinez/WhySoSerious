from typing import List, Dict
from domain.models import BertScores, Message
from domain.ports import MessageRepository, TeamRepository, ChannelRepository
from src.infrastructure.ml.bert_inference import BertPredictor

class BurnoutService:

    # Inject repository interfaces through the constructor.
    def __init__(
        self, 
        message_repo: MessageRepository, 
        team_repo: TeamRepository, 
        channel_repo: ChannelRepository
    ):
        
        # Store repositories and initialize the AI model.
        self.message_repo = message_repo
        self.team_repo = team_repo
        self.channel_repo = channel_repo
        self.predictor = BertPredictor()


    # Analyze new messages and update global scores.
    def analyzed_data(self):
    
        unanalyzed_messages = self.message_repo.get_unanalyzed()
        
        if not unanalyzed_messages:
            print("No new messages.")
            return

        print(f"Analyzing {len(unanalyzed_messages)} new messages")

        for msg in unanalyzed_messages:

            if not msg.content:

                empty_messages = BertScores(politeness=0.0, sarcasm=0.0, toxicity=0.0)
                self.message_repo.update_scores(msg.externalId, empty_messages)
                continue

            results = self.predictor.predict(msg.content)
            scores = BertScores(**results)
            self.message_repo.update_scores(msg.externalId, scores)

        print("Updating global team and channel scores.")
        self.update_global_scores()
        print("Analysis complete.")

    # Update global team and channel scores
    def update_global_scores(self):
        
        target_teams = ["León", "Oviedo", "La Bañeza"] # Filter for target teams.

        for team_name in target_teams:
           
            query = {"teamName": team_name, "analyzed": True}
            messages = list(self.message_repo.collection.find(query))
            
            if not messages:
                continue

            total = len(messages)
            sums = {"p": 0.0, "s": 0.0, "t": 0.0}
            
            for m in messages:
                sc = m["scores"]
                sums["p"] += sc["politeness"]
                sums["s"] += sc["sarcasm"]
                sums["t"] += sc["toxicity"]

            mean_scores = BertScores(
                politeness=round(sums["p"] / total, 2),
                sarcasm=round(sums["s"] / total, 2),
                toxicity=round(sums["t"] / total, 2)
            )

            self.team_repo.update_burnout_metrics(team_name, mean_scores)
            print(f"Metrics updated for Team: {team_name}")

            channels_in_team = self.message_repo.collection.distinct("channelName", {"teamName": team_name})

            for channel_name in channels_in_team:
                
                query_channel = {"channelName": channel_name, "teamName": team_name, "analyzed": True}
                channel_messages = list(self.message_repo.collection.find(query_channel))

                if channel_messages:
                    
                    channel_id = channel_messages[0]["channelId"]
                    
                    total_c = len(channel_messages)
                    sums_c = {"p": 0.0, "s": 0.0, "t": 0.0}

                    for m in channel_messages:
                        sc = m["scores"]
                        sums_c["p"] += sc["politeness"]
                        sums_c["s"] += sc["sarcasm"]
                        sums_c["t"] += sc["toxicity"]

                    mean_chan = BertScores(
                        politeness=round(sums_c["p"] / total_c, 2),
                        sarcasm=round(sums_c["s"] / total_c, 2),
                        toxicity=round(sums_c["t"] / total_c, 2)
                    )
                        
                    self.channel_repo.update_burnout_metrics(channel_id, mean_chan)
                    print(f"  > Metrics updated for Channel: '{channel_name}' (Team: {team_name})")
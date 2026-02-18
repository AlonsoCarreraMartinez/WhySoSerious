from typing import List, Dict
from domain.models import BertScores, Message
from domain.ports import MessageRepository, TeamRepository, ChannelRepository
from src.infrastructure.ml.bert_inference import BertPredictor

class BurnoutService:

    # Inject repository interfaces through the constructor
    def __init__(
        self, 
        message_repo: MessageRepository, 
        team_repo: TeamRepository, 
        channel_repo: ChannelRepository
    ):
        
        # Store repositories and initialize the AI model
        self.message_repo = message_repo
        self.team_repo = team_repo
        self.channel_repo = channel_repo
        self.predictor = BertPredictor()


    # Analyze new messages and update global scores
    def analyzed_data(self):
    
        unanalyzed_messages = self.message_repo.get_unanalyzed()
        
        if not unanalyzed_messages:
            print("No new messages.")
            return

        print(f"Analyzing {len(unanalyzed_messages)} messages")

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
        
        self.team_repo.update_burnout_scores_all() 
        self.channel_repo.update_burnout_scores_all()
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from app.services.bert_inference import analyze_text
from app.database import db
from datetime import datetime
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

# Emulator
class WhySoSeriousBot(ActivityHandler):

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text
        
        await turn_context.send_activity(f" {text}")

    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello.")
                
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text
        user_name = turn_context.activity.from_property.name
        
        scores = analyze_text(text)
        
        message_data = {
            "user": user_name,
            "message": text,
            "timestamp": datetime.utcnow(),
            "scores": scores
        }

        db.message_blocks.insert_one({
            "start_time": datetime.utcnow(),
            "end_time": datetime.utcnow(),
            "participants": [user_name],
            "messages": [message_data],
            "aggregated_scores": scores 
        })

    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello Team! I'm WhySoSerious.")
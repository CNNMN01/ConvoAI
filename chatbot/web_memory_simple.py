"""
Simple in-memory conversation storage for web app
No database = No locking issues!
"""
from datetime import datetime
from collections import defaultdict

class ConversationMemory:
    def __init__(self):
        self.conversations = defaultdict(list)
        self.user_profiles = defaultdict(dict)
        print("💾 Simple memory system initialized (in-memory)!")
    
    def add_conversation(self, user_id, message, response, personality=None):
        """Store conversation in memory"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversation = {
            'user_message': message,
            'ai_response': response,
            'timestamp': timestamp,
            'personality': personality
        }
        self.conversations[user_id].append(conversation)
        
        # Keep only last 50 conversations per user
        if len(self.conversations[user_id]) > 50:
            self.conversations[user_id] = self.conversations[user_id][-50:]
        
        print(f"💾 Stored conversation for {user_id}")
    
    def get_conversation_history(self, user_id, limit=10):
        """Get recent conversations"""
        if user_id not in self.conversations:
            return []
        
        recent = self.conversations[user_id][-limit:]
        return [(conv['user_message'], conv['ai_response'], conv['timestamp']) 
                for conv in recent]
    
    def get_user_context(self, user_id):
        """Get context string for AI"""
        if user_id not in self.conversations:
            return ""
        
        recent = self.conversations[user_id][-5:]  # Last 5 exchanges
        context_parts = []
        for conv in recent:
            context_parts.append(f"User: {conv['user_message']}")
            context_parts.append(f"AI: {conv['ai_response']}")
        
        return "\n".join(context_parts)
    
    def get_conversation_count(self, user_id):
        """Get total conversation count"""
        return len(self.conversations.get(user_id, []))

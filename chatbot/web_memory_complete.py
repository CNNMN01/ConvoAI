"""
Complete memory system with all methods needed by brain.py and web app
"""
from datetime import datetime
from collections import defaultdict

class ConversationMemory:
    def __init__(self):
        self.conversations = defaultdict(list)
        self.user_profiles = defaultdict(dict)
        print("💾 Complete memory system initialized!")
    
    # Methods for WEB APP
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
        print(f"💾 Stored conversation for {user_id}")
    
    def get_conversation_history(self, user_id, limit=10):
        """Get recent conversations for web app"""
        if user_id not in self.conversations:
            return []
        recent = self.conversations[user_id][-limit:]
        return [(conv['user_message'], conv['ai_response'], conv['timestamp']) 
                for conv in recent]
    
    def get_user_context(self, user_id):
        """Get context string for AI"""
        if user_id not in self.conversations:
            return ""
        recent = self.conversations[user_id][-3:]  # Last 3 exchanges
        context_parts = []
        for conv in recent:
            context_parts.append(f"User: {conv['user_message']}")
            context_parts.append(f"AI: {conv['ai_response']}")
        return "\n".join(context_parts)
    
    # Methods for BRAIN.PY (original memory interface)
    def add_message(self, user_id, role, message, session_id=None):
        """Add individual message (used by brain.py)"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg_data = {
            'role': role,
            'message': message,
            'timestamp': timestamp,
            'session_id': session_id
        }
        self.conversations[user_id].append(msg_data)
        print(f"💾 Added {role} message for {user_id}")
    
    def get_recent_context(self, user_id, limit=10):
        """Get recent context (used by brain.py)"""
        if user_id not in self.conversations:
            return []
        
        recent = self.conversations[user_id][-limit:]
        return [{'role': conv.get('role', 'user'), 
                'message': conv.get('message', conv.get('user_message', '')),
                'timestamp': conv.get('timestamp', '')}
               for conv in recent]
    
    def get_user_profile(self, user_id):
        """Get user profile (used by brain.py)"""
        return self.user_profiles.get(user_id, {})
    
    def update_user_name(self, user_id, name):
        """Update user name"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id]['name'] = name
        print(f"💾 Updated name for {user_id}: {name}")
    
    def add_user_interest(self, user_id, interest_text):
        """Add user interest"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        if 'interests' not in self.user_profiles[user_id]:
            self.user_profiles[user_id]['interests'] = []
        self.user_profiles[user_id]['interests'].append(interest_text)
        print(f"💾 Added interest for {user_id}: {interest_text}")

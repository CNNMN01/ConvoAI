"""
Fixed memory system compatible with both brain.py and web app
"""
from datetime import datetime
from collections import defaultdict

class ConversationMemory:
    def __init__(self):
        self.conversations = defaultdict(list)
        self.user_profiles = defaultdict(dict)
        print("💾 Fixed memory system initialized!")
    
    # For BRAIN.PY (stores individual messages)
    def add_message(self, user_id, role, message, session_id=None):
        """Add individual message (used by brain.py)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg_data = {
            'role': role,
            'message': message,  # Use 'message' key consistently
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
        return [{'role': conv['role'], 
                'message': conv['message'],  # Use consistent 'message' key
                'timestamp': conv['timestamp']}
               for conv in recent]
    
    def get_user_context(self, user_id):
        """Get context string for AI (used by brain.py)"""
        if user_id not in self.conversations:
            return ""
        
        recent = self.conversations[user_id][-3:]  # Last 3 messages
        context_parts = []
        for conv in recent:
            role = conv['role']
            message = conv['message']
            if role == 'user':
                context_parts.append(f"User: {message}")
            else:
                context_parts.append(f"AI: {message}")
        
        return "\n".join(context_parts)
    
    # For WEB APP (stores conversation pairs)
    def add_conversation(self, user_id, message, response, personality=None):
        """Store conversation pair for web app"""
        # Store as individual messages for compatibility
        self.add_message(user_id, 'user', message)
        self.add_message(user_id, 'assistant', response)
    
    def get_conversation_history(self, user_id, limit=10):
        """Get conversation history for web app"""
        if user_id not in self.conversations:
            return []
        
        # Convert individual messages back to conversation pairs
        messages = self.conversations[user_id][-limit*2:]  # Get more messages
        history = []
        
        for i in range(0, len(messages)-1, 2):
            if (i+1 < len(messages) and 
                messages[i]['role'] == 'user' and 
                messages[i+1]['role'] == 'assistant'):
                history.append((
                    messages[i]['message'],
                    messages[i+1]['message'],
                    messages[i]['timestamp']
                ))
        
        return history[-limit:]  # Return last 'limit' conversations
    
    # Other required methods
    def get_user_profile(self, user_id):
        """Get user profile"""
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

"""
Adapter to make existing ConversationMemory work with web app
"""
from .memory import ConversationMemory as OriginalMemory

class ConversationMemory:
    def __init__(self):
        # Create data directory first
        import os
        os.makedirs("data", exist_ok=True)
        
        self.original_memory = OriginalMemory()
        print("💾 Memory adapter initialized!")
    
    def add_conversation(self, user_id, message, response, personality=None):
        """Adapter: converts to your existing add_message method"""
        try:
            # Add user message
            self.original_memory.add_message(user_id, "user", message)
            # Add AI response  
            self.original_memory.add_message(user_id, "assistant", response)
            print(f"💾 Stored conversation for {user_id}")
        except Exception as e:
            print(f"⚠️ Memory storage failed: {e}")
    
    def get_conversation_history(self, user_id, limit=10):
        """Adapter: converts from your existing get_recent_context method"""
        try:
            context = self.original_memory.get_recent_context(user_id, limit)
            # Convert to expected format: [(message, response, timestamp), ...]
            history = []
            for i in range(0, len(context), 2):
                if i + 1 < len(context):
                    user_msg = context[i]
                    ai_msg = context[i + 1]
                    history.append((
                        user_msg.get('message', ''),
                        ai_msg.get('message', ''),
                        user_msg.get('timestamp', '')
                    ))
            return history
        except Exception as e:
            print(f"⚠️ Memory retrieval failed: {e}")
            return []
    
    def get_user_context(self, user_id):
        """Get context for AI - uses your existing method"""
        try:
            context = self.original_memory.get_recent_context(user_id, 5)
            context_str = ""
            for item in context:
                role = item.get('role', 'user')
                message = item.get('message', '')
                if role == 'user':
                    context_str += f"User: {message}\n"
                else:
                    context_str += f"AI: {message}\n"
            return context_str
        except Exception as e:
            print(f"⚠️ Context retrieval failed: {e}")
            return ""

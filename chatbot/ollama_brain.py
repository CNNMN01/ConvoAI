"""
ConvoAI Brain using Ollama with tinyllama (lightweight model)
"""
import requests
import json

class ConvoAIBrain:
    def __init__(self, memory):
        self.memory = memory
        self.ollama_url = "http://localhost:11434"
        self.model = "tinyllama"  # Using smaller model
        print("🧠 Ollama brain initialized with tinyllama!")
        
        # Test connection
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                print("✅ Ollama connection successful!")
            else:
                print("⚠️ Ollama not responding")
        except Exception as e:
            print(f"⚠️ Ollama connection failed: {e}")
    
    def generate_response(self, user_input, user_id, personality_name="friendly"):
        """Generate response using Ollama"""
        try:
            # Store user input
            self.memory.add_message(user_id, "user", user_input)
            
            # Get conversation context
            context = self.memory.get_user_context(user_id)
            
            # Create simple prompt (tinyllama needs simpler prompts)
            if context:
                prompt = f"{context}\nUser: {user_input}\nAssistant:"
            else:
                prompt = f"User: {user_input}\nAssistant:"
            
            # Call Ollama API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "max_tokens": 100
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                # Clean up response
                ai_response = self._clean_response(ai_response)
                
                # Store AI response
                self.memory.add_message(user_id, "assistant", ai_response)
                
                return ai_response
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return "I'm having trouble connecting to my AI model. Please try again."
                
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I apologize, but I'm having technical difficulties. Please try again."
    
    def _clean_response(self, response):
        """Clean up the AI response"""
        # Remove any prompt artifacts
        response = response.replace("Assistant:", "").replace("User:", "").strip()
        
        # Take first sentence if too long
        if len(response) > 200:
            sentences = response.split('.')
            response = sentences[0] + '.' if sentences else response[:200]
        
        # Fallback for empty responses
        if len(response) < 3:
            return "I'd be happy to help! What would you like to know?"
        
        return response

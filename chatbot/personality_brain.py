"""
Personality-aware brain that actually uses personality selection
"""
import requests
import json
import random
from .personality import PersonalityManager

class ConvoAIBrain:
    def __init__(self, memory):
        self.memory = memory
        self.ollama_url = "http://localhost:11434"
        self.model = "tinyllama"
        self.personality_manager = PersonalityManager()
        print("🧠 Personality-aware brain initialized!")
        
        # Personality-specific response styles
        self.personality_prompts = {
            'friendly_assistant': "You are a friendly, warm, and helpful assistant. Be conversational and supportive.",
            'professional': "You are a professional, formal, and efficient assistant. Be concise and business-like.",
            'creative': "You are a creative, imaginative, and inspiring assistant. Be artistic and think outside the box.",
            'casual': "You are a casual, relaxed, and laid-back assistant. Use informal language and be chill.",
            'enthusiastic': "You are an enthusiastic, energetic, and excited assistant. Show lots of passion and energy!",
            'wise': "You are a wise, thoughtful, and philosophical assistant. Give deep, meaningful responses.",
            'humorous': "You are a funny, witty, and entertaining assistant. Add humor and jokes to your responses.",
            'technical': "You are a technical, precise, and analytical assistant. Focus on facts and details."
        }
        
        # Personality-specific smart responses
        self.personality_responses = {
            'friendly_assistant': {
                'hello': ["Hello there! I'm so happy to chat with you today! 😊", "Hi! How wonderful to meet you!"],
                'thank you': ["Aww, you're so welcome! It makes me happy to help! 💕", "My absolute pleasure, friend!"]
            },
            'professional': {
                'hello': ["Good day. How may I assist you?", "Hello. I'm here to help with your inquiries."],
                'thank you': ["You're welcome. Is there anything else I can help you with?", "Certainly. Happy to assist."]
            },
            'creative': {
                'hello': ["Greetings, fellow creator! Ready to explore some amazing ideas? ✨", "Hello, beautiful soul! Let's paint some magic with words! 🎨"],
                'thank you': ["You're absolutely wonderful! Keep that creative spirit flowing! 🌟", "The pleasure is all mine, creative genius!"]
            },
            'enthusiastic': {
                'hello': ["HEY THERE! OH WOW, this is going to be AMAZING! 🚀", "HELLO! I'm SO EXCITED to help you today! ⚡"],
                'thank you': ["YOU'RE AWESOME! This was FANTASTIC! 🎉", "YES! I LOVE helping amazing people like you! 💥"]
            }
        }
    
    def generate_response(self, user_input, user_id, personality_name="friendly_assistant"):
        """Generate response with actual personality influence"""
        try:
            # Store user input
            self.memory.add_message(user_id, "user", user_input)
            
            # Check for personality-specific smart responses
            user_lower = user_input.lower().strip()
            if personality_name in self.personality_responses:
                personality_smart = self.personality_responses[personality_name]
                for key, responses in personality_smart.items():
                    if key in user_lower:
                        response = random.choice(responses)
                        self.memory.add_message(user_id, "assistant", response)
                        return response
            
            # Get personality prompt
            personality_prompt = self.personality_prompts.get(
                personality_name, 
                "You are a helpful assistant."
            )
            
            # Create personality-influenced prompt
            prompt = f"{personality_prompt}\n\nUser: {user_input}\nAssistant:"
            
            # Try Ollama with personality
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # Higher for more personality
                        "max_tokens": 60,
                        "num_predict": 60
                    }
                }
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('response', '').strip()
                    ai_response = ai_response.replace("Assistant:", "").strip()
                    
                    if len(ai_response) > 3:
                        self.memory.add_message(user_id, "assistant", ai_response)
                        return ai_response
            
            except Exception:
                pass
            
            # Personality-based fallback
            fallbacks = {
                'friendly_assistant': "I'd love to help you with that! Could you tell me a bit more? 😊",
                'professional': "I'd be happy to assist. Could you provide additional details?",
                'creative': "Oh, what an intriguing topic! Let's explore this together! ✨",
                'enthusiastic': "WOW! That sounds AMAZING! Tell me more! 🚀",
                'casual': "Cool question! Want to chat more about it?",
                'wise': "Ah, an interesting inquiry indeed. Please, share more of your thoughts.",
                'humorous': "Ha! Good question! I'm all ears (well, metaphorically speaking) 😄",
                'technical': "Please provide more specific parameters for optimal assistance."
            }
            
            fallback = fallbacks.get(personality_name, "I'm here to help! What would you like to know?")
            self.memory.add_message(user_id, "assistant", fallback)
            return fallback
            
        except Exception as e:
            return "I'm experiencing some technical difficulties. Please try again."

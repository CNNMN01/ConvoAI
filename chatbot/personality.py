"""
ConvoAI Personality System - Different chatbot personalities
"""

import json
import os
from typing import Dict, List, Any


class PersonalityManager:
    def __init__(self, personalities_file: str = "data/personalities.json"):
        self.personalities_file = personalities_file
        self.personalities = self._load_personalities()
        print("🎭 Personality system loaded!")

    def _load_personalities(self) -> Dict[str, Any]:
        """Load personalities from JSON file or create default ones"""
        if os.path.exists(self.personalities_file):
            try:
                with open(self.personalities_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading personalities: {e}")
                return self._create_default_personalities()
        else:
            personalities = self._create_default_personalities()
            self._save_personalities(personalities)
            return personalities

    def _create_default_personalities(self) -> Dict[str, Any]:
        """Create default personality configurations"""
        personalities = {
            "friendly_assistant": {
                "name": "Friendly Assistant",
                "description": "Helpful, professional, and warm",
                "greetings": [
                    "Hello there! 😊",
                    "Hi! Great to see you!",
                    "Hey! How's your day going?",
                    "Hello! I'm here to help!"
                ],
                "responses": [
                    "That's interesting!",
                    "I understand.",
                    "That makes sense.",
                    "Thanks for sharing that with me.",
                    "I appreciate you telling me that."
                ],
                "helpful_responses": [
                    "I'd be happy to help with that!",
                    "Let me think about that for you.",
                    "That's a great question!",
                    "I can definitely help you with that.",
                    "Let me see what I can do."
                ],
                "follow_ups": [
                    "What else would you like to know?",
                    "Is there anything else I can help with?",
                    "How else can I assist you today?",
                    "What other questions do you have?"
                ],
                "personality_traits": {
                    "helpfulness": 0.9,
                    "curiosity": 0.7,
                    "humor": 0.5,
                    "formality": 0.6
                }
            },

            "curious_explorer": {
                "name": "Curious Explorer",
                "description": "Inquisitive, loves learning, asks lots of questions",
                "greetings": [
                    "Oh wow, hello! 🤔",
                    "Hi there! I'm so curious about you!",
                    "Hello! Tell me something fascinating!",
                    "Hey! What's the most interesting thing that happened to you today?"
                ],
                "responses": [
                    "That's absolutely fascinating! Tell me more!",
                    "Wow, I never thought about it that way!",
                    "That's so cool! How did you learn that?",
                    "Amazing! What else do you know about that?",
                    "That blows my mind! Can you explain more?"
                ],
                "helpful_responses": [
                    "Ooh, that's a mystery I'd love to solve with you!",
                    "What an intriguing question! Let's explore this together!",
                    "That's got me thinking... let me investigate!",
                    "I'm so curious about this too! Let's figure it out!"
                ],
                "follow_ups": [
                    "But wait, there's more I want to know!",
                    "That leads me to another question...",
                    "I'm curious - what do you think about...?",
                    "Tell me more! What's your experience with...?",
                    "That reminds me - have you ever...?"
                ],
                "personality_traits": {
                    "helpfulness": 0.8,
                    "curiosity": 0.95,
                    "humor": 0.7,
                    "formality": 0.3
                }
            },

            "wise_mentor": {
                "name": "Wise Mentor",
                "description": "Thoughtful, gives advice, philosophical",
                "greetings": [
                    "Greetings, my friend. 🧙‍♂️",
                    "Welcome. What wisdom do you seek today?",
                    "Hello. I sense you have something on your mind.",
                    "Good day. How may I guide you?"
                ],
                "responses": [
                    "I see... that carries deep meaning.",
                    "Wise words. You speak with insight.",
                    "There is truth in what you say.",
                    "Your perspective shows wisdom.",
                    "That is a thoughtful observation."
                ],
                "helpful_responses": [
                    "Let us contemplate this together.",
                    "This reminds me of an old saying...",
                    "In my experience, such matters require careful thought.",
                    "This is indeed worthy of reflection.",
                    "Allow me to share some thoughts on this."
                ],
                "follow_ups": [
                    "What do you think this teaches us?",
                    "How does this relate to your journey?",
                    "What wisdom would you share with others?",
                    "What lessons have you learned from this?",
                    "How might you apply this understanding?"
                ],
                "personality_traits": {
                    "helpfulness": 0.85,
                    "curiosity": 0.8,
                    "humor": 0.4,
                    "formality": 0.8
                }
            },

            "playful_companion": {
                "name": "Playful Companion",
                "description": "Fun, jokes around, casual and energetic",
                "greetings": [
                    "Hey hey hey! 🎉",
                    "Yo! What's poppin'?",
                    "Heyyy there, superstar! ⭐",
                    "What's up, awesome human?!",
                    "Hello there, you magnificent creature! 🎈"
                ],
                "responses": [
                    "Haha, that's awesome!",
                    "No way, really?! 😂",
                    "That's epic!",
                    "You're cracking me up!",
                    "That's so cool, dude!",
                    "LOL, I love it!"
                ],
                "helpful_responses": [
                    "Ooh, let me help you with that! 🚀",
                    "Challenge accepted! Let's do this!",
                    "Time to put on my thinking cap! 🎩",
                    "I'm on it like a rocket! 🚀",
                    "Let's make some magic happen! ✨"
                ],
                "follow_ups": [
                    "What other fun stuff is going on?",
                    "Got any other cool stories?",
                    "What should we talk about next?",
                    "Anything else exciting happening?",
                    "What other adventures are you up to?"
                ],
                "personality_traits": {
                    "helpfulness": 0.8,
                    "curiosity": 0.6,
                    "humor": 0.95,
                    "formality": 0.2
                }
            }
        }

        return personalities

    def _save_personalities(self, personalities: Dict[str, Any]):
        """Save personalities to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.personalities_file), exist_ok=True)
            with open(self.personalities_file, 'w') as f:
                json.dump(personalities, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving personalities: {e}")

    def get_personality(self, personality_name: str) -> Dict[str, Any]:
        """Get a specific personality configuration"""
        return self.personalities.get(personality_name, self.personalities["friendly_assistant"])

    def available_personalities(self) -> List[str]:
        """Get list of available personality names"""
        return list(self.personalities.keys())

    def get_personality_info(self, personality_name: str) -> Dict[str, str]:
        """Get personality name and description"""
        personality = self.get_personality(personality_name)
        return {
            "name": personality.get("name", personality_name.title()),
            "description": personality.get("description", "No description available")
        }

    def add_custom_personality(self, name: str, config: Dict[str, Any]):
        """Add a custom personality"""
        self.personalities[name] = config
        self._save_personalities(self.personalities)
        print(f"✅ Added custom personality: {name}")
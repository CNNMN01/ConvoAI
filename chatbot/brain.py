"""
ConvoAI Brain - M1 Mac Compatible AI Model
"""

import random
import threading
import time
from typing import List, Dict, Any
from .memory import ConversationMemory
from .personality import PersonalityManager

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch

    HAS_TRANSFORMERS = True
    print("✅ Transformers library loaded successfully")
except ImportError as e:
    HAS_TRANSFORMERS = False
    print(f"❌ Transformers import failed: {e}")


class ConvoAIBrain:
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.personality_manager = PersonalityManager()
        self.current_personality = "friendly_assistant"
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.use_pipeline = False
        self.model_loaded = False
        self.loading_status = "Not started"

        print("🧠 ConvoAI Brain initializing with AI model...")

        if HAS_TRANSFORMERS:
            self._load_reliable_model()
        else:
            print("❌ Cannot load AI model - transformers not available")

    def _load_reliable_model(self):
        """Load AI model with M1 Mac compatibility"""
        try:
            self.loading_status = "Loading..."
            print("🚀 Loading M1-compatible AI model...")

            # Use a smaller, M1-friendly model
            model_name = "distilgpt2"
            print(f"📥 Loading {model_name} (optimized for M1 Macs)")

            # Load tokenizer with specific settings
            print("📝 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                clean_up_tokenization_spaces=False,
                use_fast=True
            )

            # Set pad token properly
            if self.tokenizer.pad_token is None:
                self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})

            print("✅ Tokenizer ready")

            # Load model with M1-specific settings
            print("🧠 Loading AI model with M1 compatibility...")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                device_map=None,
                use_safetensors=True
            )

            # Resize model embeddings if we added tokens
            if len(self.tokenizer) > self.model.config.vocab_size:
                self.model.resize_token_embeddings(len(self.tokenizer))

            # Set to eval mode
            self.model.eval()
            print("✅ Model ready")

            # Test the model with proper attention mask
            print("🧪 Testing AI model...")
            test_response = self._test_model_safe()
            if test_response:
                print(f"🧪 Test successful: {test_response[:50]}...")
                self.model_loaded = True
                self.loading_status = "Loaded successfully"
                print("=" * 60)
                print("🎉 AI MODEL LOADED AND WORKING!")
                print("=" * 60)
            else:
                raise Exception("Model test failed")

        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            self.loading_status = f"Failed: {e}"
            self.model_loaded = False

            # Try even smaller model
            self._try_tiny_model()

    def _try_tiny_model(self):
        """Try the absolute smallest working model"""
        try:
            print("🔄 Trying minimal model for M1 compatibility...")

            # Use pipeline which handles everything automatically
            self.generator = pipeline(
                "text-generation",
                model="gpt2",
                tokenizer="gpt2",
                device=-1,  # Force CPU
                torch_dtype=torch.float32
            )

            # Test it works
            test = self.generator("Hello", max_new_tokens=5, do_sample=False)
            if test:
                self.model_loaded = True
                self.loading_status = "Pipeline model loaded"
                print("✅ Minimal AI model working!")
                self.use_pipeline = True
            else:
                raise Exception("Pipeline test failed")

        except Exception as e:
            print(f"❌ All models failed: {e}")
            self.model_loaded = False
            self.loading_status = "All models failed"
            self.use_pipeline = False

    def _test_model_safe(self) -> str:
        """Test model with proper attention masks"""
        try:
            prompt = "Hello, how are you?"

            # Encode with attention mask
            encoded = self.tokenizer(
                prompt,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=100
            )

            with torch.no_grad():
                outputs = self.model.generate(
                    encoded['input_ids'],
                    attention_mask=encoded['attention_mask'],
                    max_new_tokens=15,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt):].strip()

        except Exception as e:
            print(f"❌ Model test failed: {e}")
            return None

    def generate_response(self, user_input: str, user_id: str = "default") -> str:
        """Generate intelligent response using AI model"""

        print(f"\n🤖 AI Status: {self.loading_status}")
        print(f"🤖 Model Ready: {self.model_loaded}")

        # Store user message
        self.memory.add_message(user_id, "user", user_input)

        # Get context
        context = self.memory.get_recent_context(user_id, limit=4)
        user_profile = self.memory.get_user_profile(user_id)

        # Generate response
        if self.model_loaded:
            print("🧠 Using AI model for response generation...")
            response = self._generate_ai_response(user_input, context, user_profile)
        else:
            print("⚠️ AI model not ready - this shouldn't happen!")
            response = "Sorry, my AI brain is still loading. Give me a moment and try again!"

        # Store response
        self.memory.add_message(user_id, "assistant", response)
        self._update_user_profile(user_id, user_input)

        return response

    def _generate_ai_response(self, user_input: str, context: List[Dict], user_profile: Dict) -> str:
        """Generate response using either direct model or pipeline"""
        try:
            if hasattr(self, 'use_pipeline') and self.use_pipeline:
                return self._generate_pipeline_response(user_input, context, user_profile)
            else:
                return self._generate_direct_response(user_input, context, user_profile)
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            return f"I'm having some technical difficulties. Let me try a different approach: What would you like to talk about regarding '{user_input}'?"

    def _generate_pipeline_response(self, user_input: str, context: List[Dict], user_profile: Dict) -> str:
        """Generate using pipeline (safer for M1)"""
        try:
            # Build conversation context
            prompt = self._build_conversation_context(user_input, context, user_profile)

            result = self.generator(
                prompt,
                max_new_tokens=40,
                temperature=0.8,
                do_sample=True,
                return_full_text=False,
                pad_token_id=50256  # GPT-2 pad token
            )

            response = result[0]['generated_text'].strip()
            response = self._clean_ai_response(response, user_input)

            if len(response) > 3:
                print(f"🧠 Pipeline generated: {response}")
                return response
            else:
                return f"That's interesting about '{user_input}'. Tell me more!"

        except Exception as e:
            print(f"❌ Pipeline generation error: {e}")
            return f"You mentioned '{user_input}' - I'd love to hear your thoughts on that!"

    def _generate_direct_response(self, user_input: str, context: List[Dict], user_profile: Dict) -> str:
        """Generate response using direct model access"""
        try:
            # Build intelligent conversation prompt
            prompt = self._build_conversation_context(user_input, context, user_profile)
            print(f"🧠 AI Prompt: {prompt[:100]}...")

            # Encode with proper attention mask
            encoded = self.tokenizer(
                prompt,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=400
            )

            # Generate with good parameters for conversation
            with torch.no_grad():
                outputs = self.model.generate(
                    encoded['input_ids'],
                    attention_mask=encoded['attention_mask'],
                    max_new_tokens=50,
                    min_new_tokens=5,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3
                )

            # Decode the response
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract just the AI's response
            ai_response = self._extract_ai_response(full_text, prompt)

            print(f"🧠 AI Generated: {ai_response}")

            # Validate and clean the response
            cleaned_response = self._clean_ai_response(ai_response, user_input)

            if len(cleaned_response.strip()) < 3:
                print("⚠️ AI response too short, regenerating...")
                return self._regenerate_response(user_input, context, user_profile)

            return cleaned_response

        except Exception as e:
            print(f"❌ Direct AI generation error: {e}")
            import traceback
            traceback.print_exc()
            return "I'm having trouble with my AI processing right now. Could you try rephrasing that?"

    def _build_conversation_context(self, user_input: str, context: List[Dict], user_profile: Dict) -> str:
        """Build intelligent conversation prompt"""

        # Get personality info
        personality = self.personality_manager.get_personality(self.current_personality)
        personality_desc = personality.get("description", "helpful and friendly")

        # Build context-aware prompt
        if user_profile.get("name"):
            prompt = f"This is a conversation between {user_profile['name']} and an AI assistant.\n"
        else:
            prompt = "This is a conversation between a human and an AI assistant.\n"

        prompt += f"The AI is {personality_desc} and responds naturally.\n\n"

        # Add recent context
        if context:
            for msg in context[-3:]:
                role = "Human" if msg['role'] == "user" else "AI"
                prompt += f"{role}: {msg['message']}\n"

        # Add current input
        prompt += f"Human: {user_input}\n"
        prompt += "AI:"

        return prompt

    def _extract_ai_response(self, full_text: str, original_prompt: str) -> str:
        """Extract just the AI's response from the generated text"""

        # Remove the original prompt
        if original_prompt in full_text:
            response_part = full_text[len(original_prompt):].strip()
        else:
            # Fallback: look for the last "AI:" and take everything after
            if "AI:" in full_text:
                response_part = full_text.split("AI:")[-1].strip()
            else:
                response_part = full_text.strip()

        return response_part

    def _clean_ai_response(self, response: str, user_input: str) -> str:
        """Clean and validate the AI response"""

        # Remove common artifacts
        response = response.split("Human:")[0].strip()
        response = response.split("AI:")[0].strip()
        response = response.split("\n")[0].strip()

        # Remove quotes if they wrap everything
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]

        # Remove leading/trailing punctuation artifacts
        response = response.strip('.,!?;: ')

        # Ensure it's not just repeating the input
        if response.lower().strip() == user_input.lower().strip():
            response = f"That's interesting that you mentioned '{user_input}'. Can you tell me more about that?"

        # Ensure minimum length
        if len(response.strip()) < 3:
            response = f"I find '{user_input}' intriguing. What are your thoughts on it?"

        return response.strip()

    def _regenerate_response(self, user_input: str, context: List[Dict], user_profile: Dict) -> str:
        """Regenerate response with different parameters"""
        try:
            # Try with simpler prompt
            simple_prompt = f"Human: {user_input}\nAI: That's"

            if hasattr(self, 'use_pipeline') and self.use_pipeline:
                result = self.generator(
                    simple_prompt,
                    max_new_tokens=25,
                    temperature=1.0,
                    do_sample=True,
                    return_full_text=False
                )
                response = result[0]['generated_text'].strip()
                return f"That's {response}"
            else:
                encoded = self.tokenizer(simple_prompt, return_tensors='pt')
                with torch.no_grad():
                    outputs = self.model.generate(
                        encoded['input_ids'],
                        max_new_tokens=20,
                        temperature=1.0,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )

                response = self.tokenizer.decode(outputs[0][encoded['input_ids'].shape[-1]:], skip_special_tokens=True)
                response = response.split("Human:")[0].strip()

                if len(response) > 5:
                    return f"That's {response}"
                else:
                    return f"That's really interesting about '{user_input}'. Tell me more!"

        except:
            return f"You mentioned '{user_input}' - I'd love to hear more about your thoughts on that!"

    def _update_user_profile(self, user_id: str, user_input: str):
        """Update user profile based on conversation"""

        # Extract name
        name_patterns = ["my name is", "i'm", "call me", "i am"]
        for pattern in name_patterns:
            if pattern in user_input.lower():
                words = user_input.lower().split(pattern)[-1].strip().split()
                if words:
                    name = words[0].title()
                    if len(name) > 1 and name.isalpha():
                        self.memory.update_user_name(user_id, name)
                        break

        # Extract interests
        interest_patterns = ["i love", "i like", "i enjoy", "interested in", "my hobby"]
        for pattern in interest_patterns:
            if pattern in user_input.lower():
                self.memory.add_user_interest(user_id, user_input)
                break

    def switch_personality(self, personality_name: str):
        """Switch to different personality"""
        if personality_name in self.personality_manager.available_personalities():
            self.current_personality = personality_name
            return f"🎭 Switched to {personality_name.replace('_', ' ').title()} personality! My AI will adapt to this new style."
        else:
            available = ', '.join(self.personality_manager.available_personalities())
            return f"❌ Personality '{personality_name}' not found. Available: {available}"

    def get_current_personality(self) -> str:
        """Get current personality name"""
        return self.current_personality.replace('_', ' ').title()

    def is_ai_ready(self) -> bool:
        """Check if AI model is loaded and ready"""
        return self.model_loaded

    def get_model_status(self) -> str:
        """Get detailed model status"""
        return f"AI Model Status: {self.loading_status}"
"""
Improved ConvoAI Brain with better prompting for distilgpt2
"""
from .brain import ConvoAIBrain as OriginalBrain
import torch

class ConvoAIBrain(OriginalBrain):
    def __init__(self, memory):
        # Call parent constructor with ONLY memory (no model_name!)
        super().__init__(memory)
        print("🧠 Enhanced brain with better prompting initialized!")
    
    def _create_conversation_prompt(self, user_input, user_id, personality="friendly"):
        """Create a better prompt for conversational AI"""
        
        # Get conversation context
        context = self.memory.get_user_context(user_id)
        
        # Create a conversation-focused prompt
        prompt = f"""You are ConvoAI, a helpful and friendly chatbot assistant.

Personality: {personality}
Instructions: Give helpful, conversational responses. Stay on topic.

"""
        
        # Add conversation history if available
        if context:
            prompt += f"Recent conversation:\n{context}\n\n"
        
        # Add current user input with clear format
        prompt += f"User: {user_input}\nConvoAI:"
        
        return prompt
    
    def generate_response(self, user_input, user_id, personality_name="friendly"):
        """Generate improved conversational response"""
        try:
            # Store user input
            self.memory.add_message(user_id, "user", user_input)
            
            # Create better prompt
            prompt = self._create_conversation_prompt(user_input, user_id, personality_name)
            
            # Generate with better parameters
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=400, truncation=True)
            
            # Better generation parameters for conversation
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=50,  # Shorter responses
                    temperature=0.7,    # Less random
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2,  # Avoid repetition
                    no_repeat_ngram_size=3   # Avoid phrase repetition
                )
            
            # Extract only the new response
            response_ids = outputs[0][len(inputs[0]):]
            response = self.tokenizer.decode(response_ids, skip_special_tokens=True).strip()
            
            # Clean up the response
            response = self._clean_response(response, user_input)
            
            # Store AI response
            self.memory.add_message(user_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Could you try asking again?"
    
    def _clean_response(self, response, user_input):
        """Clean and improve the generated response"""
        # Remove common artifacts
        response = response.replace("User:", "").replace("ConvoAI:", "").strip()
        
        # Remove repetitive text
        lines = response.split('\n')
        if lines:
            response = lines[0].strip()
        
        # Ensure it's not too long
        if len(response) > 200:
            sentences = response.split('.')
            response = sentences[0] + '.' if sentences else response[:200]
        
        # Fallback for very short or empty responses
        if len(response) < 3:
            return "I'd be happy to help! Could you tell me more about what you're looking for?"
        
        return response

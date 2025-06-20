"""
ConvoAI - Intelligent Chatbot with Memory
Main application entry point
"""

from gui.chat_interface import ChatInterface
from chatbot.brain import ConvoAIBrain
from chatbot.memory import ConversationMemory


def main():
    print("🤖 Starting ConvoAI...")

    # Initialize components
    memory = ConversationMemory()
    brain = ConvoAIBrain(memory)

    # Start the GUI
    app = ChatInterface(brain)
    app.run()


if __name__ == "__main__":
    main()
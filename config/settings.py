"""
ConvoAI - Intelligent Chatbot with Memory
Main application entry point
"""

from gui.chat_interface import ChatInterface
from chatbot.brain import ConvoAIBrain
from chatbot.memory import ConversationMemory
from config.settings import Settings
import sys


def main():
    print("🤖 Starting ConvoAI...")
    print("=" * 50)

    try:
        # Ensure required directories exist
        Settings.ensure_directories()

        # Initialize components
        print("💾 Initializing memory system...")
        memory = ConversationMemory()

        print("🧠 Initializing AI brain...")
        brain = ConvoAIBrain(memory)

        print("🎨 Starting chat interface...")
        app = ChatInterface(brain)

        print("🚀 ConvoAI is ready!")
        print("=" * 50)

        # Start the application
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Thanks for using ConvoAI!")
    except Exception as e:
        print(f"❌ Error starting ConvoAI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
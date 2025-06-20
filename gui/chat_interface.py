"""
ConvoAI Chat Interface - Modern GUI for the chatbot
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatbot.brain import ConvoAIBrain


class ChatInterface:
    def __init__(self, brain: 'ConvoAIBrain'):
        self.brain = brain
        self.user_id = "default_user"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create main window
        self.root = tk.Tk()
        self.root.title("ConvoAI - Intelligent Chatbot 🤖")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")

        # Configure style
        self.setup_styles()

        # Create GUI elements
        self.create_widgets()

        # Load user profile
        self.load_user_welcome()

        print("🎨 Chat interface initialized!")

    def setup_styles(self):
        """Configure modern styling"""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure colors
        self.colors = {
            "bg_dark": "#2c3e50",
            "bg_light": "#34495e",
            "accent": "#3498db",
            "user_bubble": "#3498db",
            "ai_bubble": "#95a5a6",
            "text_light": "#ecf0f1",
            "text_dark": "#2c3e50"
        }

    def create_widgets(self):
        """Create all GUI widgets"""

        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        self.create_header(main_frame)

        # Chat area
        self.create_chat_area(main_frame)

        # Input area
        self.create_input_area(main_frame)

        # Status bar
        self.create_status_bar(main_frame)

    def create_header(self, parent):
        """Create header with title and personality selector"""
        header_frame = tk.Frame(parent, bg=self.colors["bg_dark"])
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title
        title_label = tk.Label(
            header_frame,
            text="ConvoAI 🤖",
            font=("Arial", 18, "bold"),
            fg=self.colors["text_light"],
            bg=self.colors["bg_dark"]
        )
        title_label.pack(side=tk.LEFT)

        # Personality selector
        personality_frame = tk.Frame(header_frame, bg=self.colors["bg_dark"])
        personality_frame.pack(side=tk.RIGHT)

        tk.Label(
            personality_frame,
            text="Personality:",
            font=("Arial", 10),
            fg=self.colors["text_light"],
            bg=self.colors["bg_dark"]
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.personality_var = tk.StringVar()
        self.personality_combo = ttk.Combobox(
            personality_frame,
            textvariable=self.personality_var,
            values=self.brain.personality_manager.available_personalities(),
            state="readonly",
            width=15
        )
        self.personality_combo.set(self.brain.current_personality)
        self.personality_combo.bind("<<ComboboxSelected>>", self.on_personality_change)
        self.personality_combo.pack(side=tk.LEFT)

    def create_chat_area(self, parent):
        """Create scrollable chat area"""
        chat_frame = tk.Frame(parent, bg=self.colors["bg_light"], relief=tk.SUNKEN, bd=2)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Chat display with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg=self.colors["bg_light"],
            fg=self.colors["text_light"],
            insertbackground=self.colors["text_light"],
            selectbackground=self.colors["accent"],
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for styling
        self.chat_display.tag_configure(
            "user",
            foreground="#ffffff",
            background=self.colors["user_bubble"],
            relief=tk.RAISED,
            borderwidth=1,
            lmargin1=20,
            lmargin2=20,
            rmargin=50
        )

        self.chat_display.tag_configure(
            "ai",
            foreground=self.colors["text_dark"],
            background=self.colors["ai_bubble"],
            relief=tk.RAISED,
            borderwidth=1,
            lmargin1=50,
            lmargin2=50,
            rmargin=20
        )

        self.chat_display.tag_configure(
            "system",
            foreground=self.colors["accent"],
            font=("Arial", 10, "italic"),
            justify=tk.CENTER
        )

        self.chat_display.tag_configure(
            "timestamp",
            foreground="#7f8c8d",
            font=("Arial", 9),
            justify=tk.RIGHT
        )

    def create_input_area(self, parent):
        """Create message input area"""
        input_frame = tk.Frame(parent, bg=self.colors["bg_dark"])
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Input field
        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(
            input_frame,
            textvariable=self.message_var,
            font=("Arial", 12),
            bg="#ffffff",
            fg=self.colors["text_dark"],
            relief=tk.FLAT,
            bd=5
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.focus()

        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send 📤",
            command=self.send_message,
            bg=self.colors["accent"],
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT)

        # Quick actions
        actions_frame = tk.Frame(input_frame, bg=self.colors["bg_dark"])
        actions_frame.pack(side=tk.RIGHT, padx=(0, 10))

        tk.Button(
            actions_frame,
            text="🔄",
            command=self.clear_chat,
            bg=self.colors["bg_light"],
            fg=self.colors["text_light"],
            font=("Arial", 10),
            relief=tk.FLAT,
            width=3,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            actions_frame,
            text="📊",
            command=self.show_stats,
            bg=self.colors["bg_light"],
            fg=self.colors["text_light"],
            font=("Arial", 10),
            relief=tk.FLAT,
            width=3,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_bar = tk.Label(
            parent,
            text="Ready to chat! 💬",
            font=("Arial", 9),
            fg=self.colors["text_light"],
            bg=self.colors["bg_dark"],
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X)

    def load_user_welcome(self):
        """Load user profile and show welcome message"""
        profile = self.brain.memory.get_user_profile(self.user_id)
        stats = self.brain.memory.get_conversation_stats(self.user_id)

        welcome_msg = "🤖 ConvoAI is ready to chat!"

        if profile.get("name"):
            welcome_msg = f"🎉 Welcome back, {profile['name']}!"

        if stats["has_history"]:
            welcome_msg += f" We've had {stats['total_messages']} messages together."

        personality_name = self.brain.get_current_personality()
        welcome_msg += f"\n🎭 Current personality: {personality_name}"

        if profile.get("interests"):
            welcome_msg += f"\n💡 I remember you're interested in: {', '.join(profile['interests'])}"

        self.add_system_message(welcome_msg)

    def add_message(self, sender: str, message: str, tag: str):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)

        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")

        # Add message with styling
        if sender:
            self.chat_display.insert(tk.END, f"\n{sender} [{timestamp}]\n", "timestamp")

        self.chat_display.insert(tk.END, f"{message}\n\n", tag)

        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def add_system_message(self, message: str):
        """Add a system message"""
        self.add_message("", message, "system")

    def send_message(self, event=None):
        """Send user message and get AI response"""
        message = self.message_var.get().strip()
        if not message:
            return

        # Clear input
        self.message_var.set("")

        # Add user message to chat
        self.add_message("You", message, "user")

        # Update status
        self.status_bar.config(text="🤔 ConvoAI is thinking...")
        self.send_button.config(state=tk.DISABLED)

        # Get AI response in a separate thread to keep GUI responsive
        def get_response():
            try:
                response = self.brain.generate_response(message, self.user_id)

                # Update GUI in main thread
                self.root.after(0, lambda: self.handle_ai_response(response))
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                self.root.after(0, lambda: self.handle_ai_response(error_msg))

        # Start response generation in background
        threading.Thread(target=get_response, daemon=True).start()

    def handle_ai_response(self, response: str):
        """Handle AI response in main thread"""
        # Add AI response to chat
        personality_name = self.brain.get_current_personality()
        self.add_message(f"ConvoAI ({personality_name})", response, "ai")

        # Reset status
        self.status_bar.config(text="Ready to chat! 💬")
        self.send_button.config(state=tk.NORMAL)
        self.message_entry.focus()

    def on_personality_change(self, event=None):
        """Handle personality change"""
        new_personality = self.personality_var.get()
        result = self.brain.switch_personality(new_personality)
        self.add_system_message(result)

        # Update status
        personality_name = self.brain.get_current_personality()
        self.status_bar.config(text=f"🎭 Switched to {personality_name}")

    def clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.load_user_welcome()

    def show_stats(self):
        """Show conversation statistics"""
        profile = self.brain.memory.get_user_profile(self.user_id)
        stats = self.brain.memory.get_conversation_stats(self.user_id)

        stats_text = f"""📊 Conversation Statistics

👤 User: {profile.get('name', 'Unknown')}
💬 Total messages: {stats['total_messages']}
🎭 Current personality: {self.brain.get_current_personality()}
💡 Interests: {', '.join(profile.get('interests', [])) or 'None yet'}
📅 First chat: {stats.get('first_conversation', 'Today')}
"""

        messagebox.showinfo("Statistics", stats_text)

    def run(self):
        """Start the chat interface"""
        print("🚀 Starting ConvoAI chat interface...")
        self.add_system_message("Type a message to start chatting! Try saying hello or telling me your name.")

        # Start the GUI event loop
        self.root.mainloop()
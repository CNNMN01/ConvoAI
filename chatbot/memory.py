"""
ConvoAI Memory System - Conversation memory and user profiles
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os


class ConversationMemory:
    def __init__(self, db_path: str = "data/conversations.db"):
        self.db_path = db_path
        self._ensure_data_directory()
        self._initialize_database()
        print("💾 Memory system initialized!")

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Conversations table
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS conversations
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               user_id
                               TEXT
                               NOT
                               NULL,
                               role
                               TEXT
                               NOT
                               NULL,
                               message
                               TEXT
                               NOT
                               NULL,
                               timestamp
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               session_id
                               TEXT
                           )
                           ''')

            # User profiles table
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS user_profiles
                           (
                               user_id
                               TEXT
                               PRIMARY
                               KEY,
                               name
                               TEXT,
                               interests
                               TEXT,
                               preferences
                               TEXT,
                               first_seen
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               last_seen
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP
                           )
                           ''')

            # Personality memory table
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS personality_memory
                           (
                               user_id
                               TEXT,
                               personality
                               TEXT,
                               memory_data
                               TEXT,
                               updated
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               PRIMARY
                               KEY
                           (
                               user_id,
                               personality
                           )
                               )
                           ''')

            conn.commit()

    def add_message(self, user_id: str, role: str, message: str, session_id: str = None):
        """Add a message to conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO conversations (user_id, role, message, session_id)
                           VALUES (?, ?, ?, ?)
                           ''', (user_id, role, message, session_id))
            conn.commit()

        # Update user's last seen time
        self._update_user_last_seen(user_id)

    def get_recent_context(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT role, message, timestamp
                           FROM conversations
                           WHERE user_id = ?
                           ORDER BY timestamp DESC
                               LIMIT ?
                           ''', (user_id, limit))

            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'message': row[1],
                    'timestamp': row[2]
                })

            return list(reversed(messages))  # Return in chronological order

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT name, interests, preferences, first_seen, last_seen
                           FROM user_profiles
                           WHERE user_id = ?
                           ''', (user_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'interests': json.loads(row[1]) if row[1] else [],
                    'preferences': json.loads(row[2]) if row[2] else {},
                    'first_seen': row[3],
                    'last_seen': row[4]
                }
            else:
                # Create new user profile
                self._create_user_profile(user_id)
                return {
                    'name': None,
                    'interests': [],
                    'preferences': {},
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat()
                }

    def update_user_name(self, user_id: str, name: str):
        """Update user's name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE user_profiles
                           SET name      = ?,
                               last_seen = CURRENT_TIMESTAMP
                           WHERE user_id = ?
                           ''', (name, user_id))

            if cursor.rowcount == 0:
                # User doesn't exist, create profile
                self._create_user_profile(user_id, name=name)

            conn.commit()

    def add_user_interest(self, user_id: str, interest_text: str):
        """Extract and add user interests from text"""
        profile = self.get_user_profile(user_id)
        current_interests = profile.get('interests', [])

        # Simple interest extraction (you could make this more sophisticated)
        potential_interests = self._extract_interests(interest_text)

        for interest in potential_interests:
            if interest not in current_interests:
                current_interests.append(interest)

        # Update profile
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE user_profiles
                           SET interests = ?,
                               last_seen = CURRENT_TIMESTAMP
                           WHERE user_id = ?
                           ''', (json.dumps(current_interests), user_id))
            conn.commit()

    def _extract_interests(self, text: str) -> List[str]:
        """Extract potential interests from text"""
        interests = []
        text_lower = text.lower()

        # Common interest keywords and patterns
        interest_patterns = {
            'sports': ['football', 'soccer', 'basketball', 'tennis', 'swimming', 'running', 'gym'],
            'technology': ['programming', 'coding', 'ai', 'machine learning', 'computers', 'software'],
            'music': ['music', 'guitar', 'piano', 'singing', 'concerts', 'bands'],
            'reading': ['books', 'reading', 'novels', 'literature'],
            'cooking': ['cooking', 'baking', 'recipes', 'food'],
            'travel': ['travel', 'traveling', 'vacation', 'countries'],
            'movies': ['movies', 'films', 'cinema', 'netflix'],
            'games': ['games', 'gaming', 'video games', 'board games']
        }

        for category, keywords in interest_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                interests.append(category)

        return interests

    def _create_user_profile(self, user_id: str, name: str = None):
        """Create a new user profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles (user_id, name, interests, preferences)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, json.dumps([]), json.dumps({})))
            conn.commit()

    def _update_user_last_seen(self, user_id: str):
        """Update user's last seen timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE user_profiles
                           SET last_seen = CURRENT_TIMESTAMP
                           WHERE user_id = ?
                           ''', (user_id,))

            if cursor.rowcount == 0:
                self._create_user_profile(user_id)

            conn.commit()

    def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total messages
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ?', (user_id,))
            total_messages = cursor.fetchone()[0]

            # First conversation
            cursor.execute('''
                           SELECT MIN(timestamp)
                           FROM conversations
                           WHERE user_id = ?
                           ''', (user_id,))
            first_conversation = cursor.fetchone()[0]

            return {
                'total_messages': total_messages,
                'first_conversation': first_conversation,
                'has_history': total_messages > 0
            }

    def clear_user_data(self, user_id: str):
        """Clear all data for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM personality_memory WHERE user_id = ?', (user_id,))
            conn.commit()

        print(f"🗑️ Cleared all data for user: {user_id}")
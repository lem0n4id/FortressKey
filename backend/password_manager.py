import hashlib
import uuid
import sqlite3
from cryptography.fernet import Fernet
from backend.chain import Blockchain

class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

class PasswordManager:
    def __init__(self):
        self.blockchain = Blockchain()
        self.conn = sqlite3.connect('password_manager.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.current_user = None
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username)
            )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                key TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )''')
        self.conn.commit()

    def register_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                (username, password_hash))
            self.conn.commit()

            # Add transaction to the blockchain
            self.blockchain.add_transaction({
                'action': 'register_user',
                'username': username,
                'password_hash': password
            })
            self.blockchain.mine_pending_transactions()
            return True
        except:
            return False

    def login_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?",
                            (username, password_hash))
        user_row = self.cursor.fetchone()
        if user_row:
            self.current_user = User(username, password_hash)
            # Generate session ID
            session_id = str(uuid.uuid4())
            # Store session in DB
            self.cursor.execute("INSERT INTO sessions (session_id, username) VALUES (?, ?)",
                                (session_id, username))
            self.conn.commit()
            return session_id
        return None

    def validate_session(self, session_id):
        self.cursor.execute("SELECT username FROM sessions WHERE session_id=?", (session_id,))
        user_row = self.cursor.fetchone()
        if user_row:
            self.current_user = User(user_row[0], None)  # No need for password in session validation
            return True
        return False

    def logout_user(self, session_id):
        self.cursor.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))
        self.conn.commit()

    def add_password(self, website, username, password):
        if not self.current_user:
            return False

        # Encrypt the password
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()

        # Get the user_id
        self.cursor.execute("SELECT user_id FROM users WHERE username=?", (self.current_user.username,))
        user_id = self.cursor.fetchone()[0]

        # Store the password entry in the 'entries' table
        self.cursor.execute(
            "INSERT INTO entries (user_id, website, username, password, key) VALUES (?, ?, ?, ?, ?)",
            (user_id, website, username, encrypted_password, key.decode())
        )
        self.conn.commit()

        # Add transaction to the blockchain
        self.blockchain.add_transaction({
            'action': 'add_password',
            'username': self.current_user.username,
            'website': website,
            'username_entry': username,
            'password': encrypted_password
        })
        self.blockchain.mine_pending_transactions()
        return True

    def update_password(self, website, username, new_password):
        if not self.current_user:
            return False

        # Get the user_id
        self.cursor.execute("SELECT user_id FROM users WHERE username=?", (self.current_user.username,))
        user_id = self.cursor.fetchone()[0]

        # Encrypt the new password
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_password = cipher_suite.encrypt(new_password.encode()).decode()

        # Update the password entry in the 'entries' table
        self.cursor.execute('''
            UPDATE entries 
            SET password = ?, key = ?
            WHERE user_id = ? AND website = ? AND username = ?
        ''', (encrypted_password, key.decode(), user_id, website, username))

        if self.cursor.rowcount == 0:
            return False

        self.conn.commit()

        # Add transaction to the blockchain
        self.blockchain.add_transaction({
            'action': 'update_password',
            'username': self.current_user.username,
            'website': website,
            'username_entry': username,
            'password': encrypted_password
        })
        self.blockchain.mine_pending_transactions()
        return True

    def delete_password(self, website, username):
        if not self.current_user:
            return False

        # Get the user_id
        self.cursor.execute("SELECT user_id FROM users WHERE username=?", (self.current_user.username,))
        user_id = self.cursor.fetchone()[0]

        # Delete the password entry from the 'entries' table
        self.cursor.execute('''
            DELETE FROM entries 
            WHERE user_id = ? AND website = ? AND username = ?
        ''', (user_id, website, username))

        if self.cursor.rowcount == 0:
            return False

        self.conn.commit()

        # Add transaction to the blockchain
        self.blockchain.add_transaction({
            'action': 'delete_password',
            'username': self.current_user.username,
            'website': website,
            'username_entry': username
        })
        self.blockchain.mine_pending_transactions()
        return True

    def get_all_passwords(self):
        if not self.current_user:
            return None

        # Get the user_id
        self.cursor.execute("SELECT user_id FROM users WHERE username=?", (self.current_user.username,))
        user_id = self.cursor.fetchone()[0]

        # Fetch all password entries for this user
        self.cursor.execute("SELECT website, username, password, key FROM entries WHERE user_id=?", (user_id,))
        password_entries = self.cursor.fetchall()

        passwords = []
        for entry in password_entries:
            website, username, encrypted_password, key = entry
            cipher_suite = Fernet(key.encode())
            decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
            passwords.append({
                'website': website,
                'username': username,
                'password': decrypted_password
            })
        return passwords

    def print_all_transactions(self):
        self.blockchain.print_all_transactions()


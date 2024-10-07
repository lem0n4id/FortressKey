import sqlite3
import hashlib
from cryptography.fernet import Fernet
import hashlib
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                key TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        # Check if user already exists
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.cursor.fetchone():
            return False

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        # Insert new user
        self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                            (username, password_hash))
        self.conn.commit()
        return True

    def login_user(self, username, password):
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Query user in the database
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
        user_row = self.cursor.fetchone()

        if user_row:
            self.current_user = User(username, password_hash)
            return True
        return False

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
        return True

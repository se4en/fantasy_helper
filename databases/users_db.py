import sqlite3

class UsersDB:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                            (tg_id text, profile_url text)
                            """)

    def add_user(self, tg_id, profile_url):
        self.cursor.execute('INSERT INTO users VALUES (?)', (tg_id, profile_url))

    def get_profile(self, tg_id):
        self.cursor.execute('SELECT * FROM users WHERE tg_id=?', [(tg_id)])
        return self.cursor.fetchone()[1]

 

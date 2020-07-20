import sqlite3

class UsersDB:
   def __init__(self):
      pass

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
 
cursor.execute("""CREATE TABLE users
                  (tg_id text, profile_url text)
               """)
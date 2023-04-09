import sqlite3
import os

#Creates the connection to the database by retrieving the path
def create_connection():
    filename = os.path.abspath(__file__)
    dbdir = filename.rstrip('db.py')
    dbpath = os.path.join(dbdir, "cuffcare.db")
    conn = sqlite3.connect(dbpath)
    return conn

#Initialize database tables if they do not exist
def create_database():
    conn = create_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username text NOT NULL,
        password text NOT NULL,
        id integer PRIMARY KEY AUTOINCREMENT
    )""")
    conn.commit()
    conn.close()

#Add new user row
def insert_users(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username,password))
    conn.commit()
    conn.close()

#List the users
def list_users():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    results = c.fetchall()
    conn.close()
    return results
import sqlite3

# Check if SQLite3 is working
conn = sqlite3.connect(':memory:')  # Creates a temporary in-memory database
print("SQLite3 is working!")
conn.close()

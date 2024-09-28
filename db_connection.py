# db_connection.py
import mysql.connector

# Function to connect to the MySQL database
def connect_db():
    config = {
        'user': 'syimah',       # Replace with your MySQL username
        'password': 'p@ssw0rd',   # Replace with your MySQL password
        'host': '34.142.128.147',           # Change if your MySQL server is not local
        'database': 'inf2003-a1'       # Your database name
    }
    conn = mysql.connector.connect(**config)
    return conn

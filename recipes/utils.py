import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="34.142.128.147",
        user="inf2003-dev",
        password="p@ssw0rd",
        database="inf2003-a1"
    )
    return connection

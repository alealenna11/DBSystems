# login.py
import streamlit as st
import hashlib
from db_connection import connect_db  # Import the database connection

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(stored_password, provided_password):
    """Checks if the provided password matches the stored hashed password."""
    return stored_password == hash_password(provided_password)

import streamlit as st
import hashlib
from db_connection import connect_db

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(stored_password, provided_password):
    """Checks if the provided password matches the stored hashed password."""
    return stored_password == hash_password(provided_password)

def show_login():
    """Displays the login page."""
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_submit"):
        conn = connect_db()
        cursor = conn.cursor()

        # Query to check if user exists
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):  # Assuming password is hashed in user[3]
            st.session_state["username"] = username  # Store username in session state
            st.session_state['logged_in'] = True  # Track login status

            return True  # Indicate successful login
        else:
            st.error("No user found or incorrect password. Please try again or register.")

    # Add a registration link using query parameters to navigate to the registration page
    st.markdown("[Don't have an account? Register here.](?register=True)")

    return False  # Indicate login was unsuccessful


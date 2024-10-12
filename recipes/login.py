import streamlit as st
import hashlib
from db_connection import connect_db  # Import the database connection

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(stored_password, provided_password):
    """Checks if the provided password matches the stored hashed password."""
    return stored_password == hash_password(provided_password)

def login(username, password):
    """Authenticates a user and stores user information in session state."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Query to check if user exists
    cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user[3], password):  # Assuming password is hashed in user[3]
        st.session_state.user_id = user[0]  # Set the user_id in session state
        st.session_state.username = username  # Optional: also save the username
        return True  # Login successful
    return False  # Login failed

def show_login():
    """Displays the login page."""
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_submit"):
        # Check if both fields are filled
        if not username or not password:
            st.error("Please fill in all fields.")
            return False  # Indicate login was unsuccessful

        if login(username, password):
            st.session_state['logged_in'] = True  # Track login status
            st.success("Login successful! Redirecting to the homepage...")
            st.session_state.page = 'homepage'  # Redirect to homepage
            return True  # Indicate successful login
        else:
            st.error("Wrong username or password. Please try again.")

    # Navigate to the registration page directly
    if st.button("Don't have an account? Register here.", key="register_button_login"):
        st.session_state.page = 'registration'  # Redirect to the registration page

    return False  # Indicate login was unsuccessful

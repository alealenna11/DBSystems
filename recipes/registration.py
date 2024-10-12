import streamlit as st
import hashlib
import re  # Import regex module for email validation
from db_connection import connect_db  # Import the database connection
from datetime import datetime  # Import for handling date

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Validates the email format using regex."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    """Validates the password criteria."""
    if (len(password) < 6 or not re.search(r'[A-Z]', password) or 
        not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password)):
        return False
    return True

def show_registration():
    """Displays the registration page."""
    st.title("Register")

    # Initialize session state for error messages
    if 'errors' not in st.session_state:
        st.session_state.errors = {}

    username = st.text_input("Username", on_change=lambda: clear_error('username'))
    email = st.text_input("Email", on_change=lambda: clear_error('email'))
    password = st.text_input("Password", type="password", on_change=lambda: clear_error('password'))
    confirm_password = st.text_input("Confirm Password", type="password", on_change=lambda: clear_error('confirm_password'))

    # Function to clear specific error messages
    def clear_error(field):
        if field in st.session_state.errors:
            del st.session_state.errors[field]

    # Validation checks for username
    if username:
        if len(username) < 3:  # Check length first
            st.session_state.errors['username'] = "Username must be at least 3 characters long."
        else:
            # Check if the username is already taken
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            username_user = cursor.fetchone()
            cursor.close()  # Close the cursor after operation
            if username_user:
                st.session_state.errors['username'] = "Username already exists. Please choose a different username."

    # Validation checks for email
    if email:
        if not is_valid_email(email):  # Check if email format is valid
            st.session_state.errors['email'] = "Invalid email format. Please enter a valid email (e.g., user@gmail.com)."
        else:
            # Check if the email is already taken
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
            email_user = cursor.fetchone()
            cursor.close()  # Close the cursor after operation
            if email_user:
                st.session_state.errors['email'] = "Email is already taken. Please use a different email."

    # Validation checks for password
    if password:
        if not is_valid_password(password):  # Validate password criteria
            st.session_state.errors['password'] = (
                "Password must be at least 6 characters long, "
                "contain at least one uppercase letter, one lowercase letter, and one digit."
            )

    # Validation check for confirm password
    if confirm_password:
        if confirm_password != password:
            st.session_state.errors['confirm_password'] = "Passwords do not match."

    # Display error messages below respective fields
    for field, error_msg in st.session_state.errors.items():
        st.error(error_msg)

    if st.button("Register", key="register_submit"):
        # Final checks before registration
        if not username or not email or not password or not confirm_password:
            st.error("Please fill in all fields.")
            return False  # Indicate registration was unsuccessful

        # If all checks pass, register the user
        hashed_password = hash_password(password)
        date_joined = datetime.now().date()

        # Store the new user in the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Users (username, email, password_hashed, date_joined) "
            "VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, date_joined)
        )
        conn.commit()
        cursor.close()  # Close the cursor after operation

        st.success("Registration successful! You can now log in.")
        return True  # Indicate successful registration

    return False  # Indicate registration was unsuccessful

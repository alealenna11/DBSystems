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
    if (
            len(password) < 6
            or not re.search(r'[A-Z]', password)
            or not re.search(r'[a-z]', password)
            or not re.search(r'[0-9]', password)
    ):
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

    # Connect to the database
    db, _, users_collection, *_ = connect_db()

    # Validation checks for username
    if username:
        if len(username) < 3:  # Check length
            st.session_state.errors['username'] = "Username must be at least 3 characters long."
        elif users_collection.find_one({"username": username}):  # Check if username exists
            st.session_state.errors['username'] = "Username already exists. Please choose a different username."

    # Validation checks for email
    if email:
        if not is_valid_email(email):  # Check format
            st.session_state.errors['email'] = "Invalid email format. Please enter a valid email (e.g., user@gmail.com)."
        elif users_collection.find_one({"email": email}):  # Check if email exists
            st.session_state.errors['email'] = "Email is already taken. Please use a different email."

    # Validation checks for password
    if password:
        if not is_valid_password(password):  # Validate criteria
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
        if field in locals():  # Show errors for existing fields
            st.error(error_msg)

    if st.button("Register", key="register_submit"):
        # Final checks before registration
        if not username or not email or not password or not confirm_password:
            st.error("Please fill in all fields.")
            return False  # Indicate registration was unsuccessful

        # If all checks pass, register the user
        hashed_password = hash_password(password)
        date_joined = datetime.now().strftime("%Y-%m-%d")

        try:
            # Store the new user in the MongoDB collection
            users_collection.insert_one({
                "username": username,
                "email": email,
                "password_hashed": hashed_password,
                "date_joined": date_joined
            })

            st.success("Registration successful! You can now log in.")
            return True  # Indicate successful registration

        except Exception as e:
            st.error(f"An error occurred during registration: {e}")
            return False  # Indicate registration was unsuccessful

    return False  # Indicate registration was unsuccessful

import streamlit as st
from homepage import homepage  # Import homepage function
from recipe_details import recipe_details  # Import recipe details function
from login import show_login  # Import the show_login function
from profile import show_profile  # Import the profile function

def main():
    # Set up the session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'homepage'  # Default page is homepage
    if 'selected_recipe' not in st.session_state:
        st.session_state.selected_recipe = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Track login status
    if 'username' not in st.session_state:
        st.session_state.username = None  # Store username

    # Sidebar for navigation
    st.sidebar.title("Navigation")

    # Button to go to the homepage
    if st.sidebar.button("Home", key="home_button"):
        st.session_state.page = 'homepage'  # Change to homepage when button is clicked

    # Button for profile page
    if st.session_state.logged_in:
        if st.sidebar.button("Profile", key="profile_button"):
            st.session_state.page = 'profile'  # Change to profile page when button is clicked

    # Button for login/logout based on login status
    if st.session_state.logged_in:
        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.logged_in = False  # Set login status to false
            st.session_state.username = None  # Clear username
            st.success("Logged out successfully.")
    else:
        if st.sidebar.button("Login", key="login_button"):
            st.session_state.page = 'login'  # Change to login page when button is clicked

    # Navigation logic
    if st.session_state.page == 'homepage':
        homepage()  # Call the homepage function
    elif st.session_state.page == 'recipe_details':
        recipe_details()  # Call the recipe details function
    elif st.session_state.page == 'login':
        if show_login():  # Call the login function and check for successful login
            st.session_state.page = 'homepage'  # Redirect to homepage upon successful login
    elif st.session_state.page == 'profile':
        if st.session_state.username:  # Ensure the user is logged in
            show_profile(st.session_state.username)  # Show the user's profile

if __name__ == "__main__":
    main()

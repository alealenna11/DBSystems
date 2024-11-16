import streamlit as st

# Import pages
from login import show_login  # Import the show_login function
from homepage import show_homepage  # Import the homepage display function
from registration import show_registration  # Import the registration function
from recipe_details import recipe_details  # Import recipe_details function
from user_profile import show_user_profile  # Import user profile display function

def main():
    # Set up the session state for page navigation and user details
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # User is not logged in initially
        st.session_state.page = 'homepage'  # Default page is homepage
        st.session_state.user_id = None  # Initialize user_id

    # Sidebar for navigation
    st.sidebar.title("Navigation")

    # Add logo under the navigation title
    st.sidebar.image("recipes/uploads/logo.png", use_column_width=True)

    # Button for home page navigation
    if st.sidebar.button("Home", key="home_button"):
        st.session_state.page = 'homepage'  # Redirect to homepage
        st.rerun()  # Rerun the app to update the sidebar

    # Button for login/logout based on login status
    if st.session_state.logged_in:
        # Logout button is visible
        if st.sidebar.button("Logout", key="logout_button"):
            # Perform logout action
            st.session_state.logged_in = False  # Set login status to false
            st.session_state.username = None  # Clear username
            st.session_state.user_id = None  # Clear user_id on logout
            st.session_state.page = 'homepage'  # Redirect to homepage
            st.rerun()  # Rerun the app to update the sidebar
            
        # Add a profile navigation option
        if st.sidebar.button("Profile", key="profile_button"):
            st.session_state.page = 'user_profile'  # Navigate to user profile

    else:
        # Login and Register buttons are visible
        if st.sidebar.button("Login", key="login_button"):
            st.session_state.page = 'login'  # Change to login page
        if st.sidebar.button("Register", key="register_button"):
            st.session_state.page = 'registration'  # Change to registration page

    # Navigation logic based on the page state
    if st.session_state.page == 'homepage':
        show_homepage()  # Display homepage content
    elif st.session_state.page == 'login':
        if show_login():  # Call the login function and check for successful login
            st.session_state.logged_in = True  # Set logged_in to True on successful login
            # Assume that the show_login function sets st.session_state.user_id
            st.session_state.page = 'homepage'  # Redirect to homepage
    elif st.session_state.page == 'registration':
        show_registration()  # Display registration page
    elif st.session_state.page == 'recipe_details':
        recipe_details()  # Call the recipe details function
    elif st.session_state.page == 'user_profile':
        if st.session_state.logged_in:  # Check if user is logged in before showing profile
            show_user_profile(st.session_state.username)  # Call the user profile function and pass the username
        else:
            st.error("You need to be logged in to view your profile.")  # Show an error message if not logged in
            
    # Optional: Consider adding a redirect after profile view
    if st.session_state.page == 'user_profile' and st.sidebar.button("Back to Home"):
        st.session_state.page = 'homepage'
        st.rerun()  # Rerun to go back to the homepage

def fetch_recipes(search_query=None, rating_filter=None, cuisine_filter=None, dietary_filter=None, cook_time_filter=None):
    _, recipes_collection, _, recipe_info_collection, recipe_ratings_collection, cuisines_collection, dietary_collection = connect_db()

    query = {}

    # Add search filter for title or description
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}}
        ]

    # Add filters
    if cuisine_filter and cuisine_filter != "All":
        query["cuisine"] = cuisine_filter
    if dietary_filter and dietary_filter != "All":
        query["dietary"] = dietary_filter
    if cook_time_filter:
        query["cook_time"] = {"$lte": cook_time_filter}

    # Fetch recipes with the query
    recipes = list(recipes_collection.find(query))

    if rating_filter and rating_filter != "All":
        recipes = [recipe for recipe in recipes if recipe.get("average_rating", 0) >= rating_filter]

    return recipes

if __name__ == "__main__":
    main()

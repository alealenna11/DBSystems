import streamlit as st
from homepage import show_home  # Import homepage function
from recipesdetails import recipesdetails  # Import recipe details function
from login import show_login  # Import the show_login function
from profile import show_profile  # Import the profile function

def main():
    # Set up the session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'homepage'  # Default page is homepage
    if 'selected_recipe_id' not in st.session_state:
        st.session_state.selected_recipe_id = None  # Store the selected recipe for details view
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Track login status
    if 'username' not in st.session_state:
        st.session_state.username = None  # Store username

    # Sidebar Navigation with logo
    st.sidebar.image("recipes/logo.png", width=200)  # Display the logo at the top of the sidebar
    st.sidebar.title("Navigation")

    # Adjust navigation based on login state
    if st.session_state.logged_in:
        # Show full navigation for logged-in users
        selection = st.sidebar.selectbox(
            "Go to",
            ["Home", "Profile", "Submit & Manage Recipes", "Recipe Details", "Logout"]
        )
    else:
        # Show limited navigation for not logged-in users
        selection = st.sidebar.selectbox("Go to", ["Home", "Login"])

    # Handle navigation logic based on selection
    if selection == "Home":
        show_home()  # Call the homepage function

    elif selection == "Profile" and st.session_state.logged_in:
        show_profile(st.session_state.username)  # Show profile page if logged in

    elif selection == "Submit & Manage Recipes" and st.session_state.logged_in:
        show_profile(st.session_state.username)  # Show profile with recipe management options

    elif selection == "Recipe Details" and st.session_state.logged_in:
        if st.session_state.selected_recipe_id:
            recipesdetails(st.session_state.selected_recipe_id)  # Show recipe details if a recipe has been selected
        else:
            st.error("Please select a recipe to view details.")

    elif selection == "Login":
        # Login process
        if show_login():  # If login is successful, update session state
            st.success(f"Welcome, {st.session_state.username}!")
            st.session_state.page = "homepage"  # Change the page in session state
            # No need to rerun, Streamlit will automatically update
            # after session state changes

    elif selection == "Logout" and st.session_state.logged_in:
        # Logout process
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("Logged out successfully.")
        st.session_state.page = "homepage"  # Redirect to homepage after logout
        # No need to rerun, Streamlit will automatically update the page

if __name__ == "__main__":
    main()

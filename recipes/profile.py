import streamlit as st
from utils import get_connection  # Ensure this is available to fetch user data

def show_profile(username):
    if username:
        conn = get_connection()  # Connect to the database
        cursor = conn.cursor()

        # Fetch user information based on the username
        cursor.execute("SELECT email, user_id FROM Users WHERE username = %s", (username,))
        user_info = cursor.fetchone()
        conn.close()

        if user_info:
            user_email, user_id = user_info
            st.title(f"Profile of {username}")
            st.subheader("Information")
            st.write(f"**Email:** {user_email}")

            # Fetch and display user's recipes
            show_my_recipes(user_id)  # Pass the user_id to fetch recipes

            # Back to Home button
            if st.button("Back to Home"):
                # Clear query parameters
                st.query_params.clear()
                
                # Inject JavaScript to reload the page or redirect to the homepage
                st.markdown(
                    """
                    <script type="text/javascript">
                        window.location.href = "/";
                    </script>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.error("User not found.")
    else:
        st.error("No username provided.")

def show_my_recipes(user_id):
    st.subheader("My Recipes")
    conn = get_connection()  # Connect to the database
    cursor = conn.cursor()
    
    # Fetch the recipes of the user based on user_id
    cursor.execute("SELECT title, description FROM Recipes WHERE user_id = %s", (user_id,))
    recipes = cursor.fetchall()
    conn.close()

    if recipes:
        for recipe in recipes:
            st.write(f"**{recipe[0]}**")
            st.write(recipe[1])
            st.write("---")
    else:
        st.write("This user has not submitted any recipes yet.")

if __name__ == "__main__":
    # Main app logic
    query_params = st.query_params
    username = query_params.get("username")  # Get username from URL params

    if username:
        show_profile(username[0])  # Pass the username to the profile page
    else:
        st.write("No username provided in the URL.")

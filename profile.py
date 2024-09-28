import streamlit as st
from db_connection import connect_db

def get_connection():
    return connect_db()  # Use your actual database connection function

def save_recipe(title, description, rating, creator_username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        INSERT INTO Recipes (title, description, ratings, user_id) 
        VALUES (%s, %s, %s, (SELECT user_id FROM Users WHERE username=%s))
    """, (title, description, rating, creator_username))
    conn.commit()
    conn.close()
    return "Recipe added successfully!"


def show_favorites(user_id):
    st.subheader("Your Favorite Recipes")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(""" 
            SELECT f.favorite_id, r.title, r.description 
            FROM Favorite f 
            JOIN Recipes r ON f.recipe_id = r.recipe_id 
            WHERE f.user_id = %s
        """, (user_id,))
        favorites = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching favorites: {e}")
        favorites = []
    finally:
        conn.close()

    if favorites:
        for favorite in favorites:
            favorite_id, title, description = favorite
            st.write(f"**{title}**")
            st.write(description)

            if st.button("❤️", key=f"remove_fav_{favorite_id}"):  # Unique key for each button
                remove_favorite(user_id, favorite_id)  # Call the function to remove from favorites
                st.success(f"{title} has been removed from your favorites.")
                st.rerun()

            st.write("---")
    else:
        st.write("You have no favorite recipes yet.")

def remove_favorite(user_id, favorite_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(""" 
            DELETE FROM Favorite 
            WHERE user_id = %s AND favorite_id = %s
        """, (user_id, favorite_id))
        conn.commit()
        return "Favorite removed successfully!"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def show_profile(username):
    if username:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email, user_id FROM Users WHERE username = %s", (username,))
            user_info = cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching profile: {e}")
            return
        finally:
            conn.close()

        if user_info:
            user_email, user_id = user_info
            if 'editing' not in st.session_state:
                st.session_state.editing = False
            if 'new_email' not in st.session_state:
                st.session_state.new_email = user_email
            if 'new_bio' not in st.session_state:
                st.session_state.new_bio = "This is your bio."  # Placeholder bio

            st.title(f"{username} Profile")
            profile_option = st.sidebar.selectbox("Choose an option", 
                ("View Profile", "Update Profile", "Favorites"))

            if profile_option == "View Profile":
                st.write(f"**Email:** {user_email}")
                add_recipe_button = st.button("Add Recipe", key="add_recipe_button")

                if add_recipe_button:
                    st.session_state.show_recipe_form = True

                if st.session_state.get('show_recipe_form', False):
                    new_recipe_title = st.text_input("Recipe Title", key="new_recipe_title")
                    new_recipe_description = st.text_area("Recipe Description", key="new_recipe_description")
                    new_rating = st.slider("Rating", min_value=0.0, max_value=5.0, step=0.5)
                    st.write("Selected Rating:", new_rating)  # Displays the selected rating

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Submit Recipe", key="submit_recipe_button"):
                            message = save_recipe(new_recipe_title, new_recipe_description, new_rating, username)  # Changed new_ratings to new_rating
                            st.success(message)
                            st.session_state.show_recipe_form = False  # Hide form after submission


                    with col2:
                        if st.button("Cancel", key="cancel_recipe_button"):
                            st.session_state.show_recipe_form = False

                show_my_recipes(user_id)

                if st.button("Back to Home", key="back_to_home_button"):
                    st.session_state.page = 'homepage'  
                
            elif profile_option == "Update Profile":
                if st.button("Edit Profile", key="edit_profile_button"):
                    st.session_state.editing = True
                    st.session_state.new_email = user_email
                    st.session_state.new_bio = "This is your bio."  

                if st.session_state.editing:
                    st.subheader("Edit Your Information")
                    new_email = st.text_input("Email", value=st.session_state.new_email, key="edit_email")
                    new_bio = st.text_area("Bio", value=st.session_state.new_bio, key="edit_bio")

                    if st.button("Save Changes", key="save_changes_button"):
                        message = update_profile(user_id, new_email, new_bio)
                        st.success(message)
                        st.session_state.editing = False

            elif profile_option == "Favorites":
                show_favorites(user_id)

        else:
            st.error("User not found.")
    else:
        st.error("No username provided.")
        
def show_my_recipes(user_id):
    st.subheader("My Recipes")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT recipe_id, title, description FROM Recipes WHERE user_id = %s", (user_id,))
        recipes = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching recipes: {e}")
        recipes = []
    finally:
        conn.close()

    if recipes:
        for recipe in recipes:
            recipe_id, title, description = recipe
            if st.button(title, key=f"recipe_{recipe_id}"):  # Make recipe title clickable
                st.session_state.selected_recipe_id = recipe_id  # Save selected recipe ID
                st.session_state.page = 'recipe_detail'  # Navigate to recipe detail page

            st.write(description)  # Display recipe description
            st.write("---")
    else:
        st.write("This user has not submitted any recipes yet.")


def update_profile(user_id, new_email, new_bio):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(""" 
            UPDATE Users 
            SET email = %s, bio = %s 
            WHERE user_id = %s 
        """, (new_email, new_bio, user_id))
        conn.commit()
        return "Profile updated successfully!"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()
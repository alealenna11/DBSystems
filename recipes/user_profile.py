import streamlit as st
from db_connection import connect_db
from recipe_details import recipe_details
from favorites import toggle_favorite,fetch_user_favorites
import os
import base64

def show_user_profile(username=None):
    query_params = st.query_params
        
    if username is None:
        username = query_params.get('username', None)
        
    if username is None:
        st.error("No username provided.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, bio, profile_pic, dietary_id FROM Users WHERE username = %s", (username,))
        user_info = cursor.fetchone()
    except Exception as e:
        st.error(f"Error fetching profile: {e}")
        return
    finally:
        if conn and conn.is_connected():
            conn.close()

    if user_info:
        username, user_email, user_bio, user_profile_pic, dietary_id = user_info
        if 'editing' not in st.session_state:
            st.session_state.editing = False
        if 'new_username' not in st.session_state:
            st.session_state.new_username = username
        if 'new_email' not in st.session_state:
            st.session_state.new_email = user_email
        if 'new_bio' not in st.session_state:
            st.session_state.new_bio = user_bio

        st.markdown(f"<h2 style='text-align: center;'>{username}'s Profile</h2>", unsafe_allow_html=True) # Centered title
        profile_option = st.sidebar.selectbox("Choose an option", 
            ("View Profile", "Update Profile", "Edit Recipes", "Favorites"))

        if profile_option == "View Profile":
            display_profile_picture(user_profile_pic)
            st.write(f"**Email:** {user_email}")
            st.write(f"**Bio:** {user_bio}")
            dietary_name = fetch_dietary_name(dietary_id)
            st.write(f"**Dietary Preferences:** {dietary_name}")


            # Conditionally display the heading for recipes based on who is viewing
            if st.session_state.logged_in and st.session_state.username == username:
                st.markdown(f"<br><h3 style='text-align: center;'>My Recipes</h3>", unsafe_allow_html=True)  # User is viewing their own profile
            else:
                st.markdown(f"<br><h3 style='text-align: center;'>{username}'s Recipes</h3>", unsafe_allow_html=True)  # Guest or other users viewing the profile

            show_my_recipes(username)

            if st.button("Back to Home", key="back_to_home_button"):
                st.session_state.page = 'homepage'
                
            
        elif profile_option == "Update Profile":
            # Only allow updates if logged in
            if st.session_state.logged_in and st.session_state.username == username:
                st.subheader("Edit Your Information")
                new_username = st.text_input("Username", value=st.session_state.new_username, key="edit_username")
                new_email = st.text_input("Email", value=st.session_state.new_email, key="edit_email")
                new_bio = st.text_area("Bio", value=st.session_state.new_bio, key="edit_bio")

                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT dietary_id, name FROM Dietary")
                    dietary_options = cursor.fetchall()
                    dietary_dict = {dietary_id: name for dietary_id, name in dietary_options}
                    conn.close()

                    # Select the dietary preference and map it back to the corresponding dietary_id
                    index = list(dietary_dict.values()).index(dietary_dict[dietary_id]) if dietary_id in dietary_dict else 0

                    new_dietary_name = st.selectbox(
                        "Dietary Preferences",
                        list(dietary_dict.values()),  # Show names in dropdown
                        index=index
                    )

                    try:
                        new_dietary_id = {v: k for k, v in dietary_dict.items()}[new_dietary_name]
                    except KeyError:
                        st.error("Selected dietary preference is invalid.")
                        new_dietary_id = None

                upload_profile_picture(username)

                if st.button("Save Changes", key="save_changes_button"):
                    message = update_profile(username, new_username, new_email, new_bio, new_dietary_id)
                    st.success(message)

                    # Update session state
                    st.session_state.new_username = new_username
                    st.session_state.new_email = new_email
                    st.session_state.new_bio = new_bio
                    st.session_state.editing = False

        elif profile_option == "Edit Recipes":
                if st.session_state.logged_in and st.session_state.username == username:
                    add_recipe_button = st.button("Add Recipe", key="add_recipe_button")
                    st.markdown("---")

                    if add_recipe_button:
                        st.session_state.show_recipe_form = True

                    if st.session_state.get('show_recipe_form', False):
                        new_recipe_title = st.text_input("Recipe Title", key="new_recipe_title")
                        new_recipe_description = st.text_area("Recipe Description", key="new_recipe_description")
                        new_cook_time = st.number_input("Cook Time (minutes)", min_value=1, key="new_cook_time")
                        new_servings = st.number_input("Servings", min_value=1, key="new_servings")
                        new_ingredients = st.text_area("Ingredients (one per line)", key="new_ingredients")
                        new_instructions = st.text_area("Instructions", key="new_instructions")

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("Submit Recipe", key="submit_recipe_button"):
                                # Pass all new recipe details to the save_recipe function
                                message = save_recipe(
                                    new_recipe_title, 
                                    new_recipe_description, 
                                    new_cook_time, 
                                    new_servings, 
                                    new_ingredients, 
                                    new_instructions, 
                                    username
                                )
                                st.success(message)
                                st.session_state.show_recipe_form = False

                        with col2:
                            if st.button("Cancel", key="cancel_recipe_button"):
                                st.session_state.show_recipe_form = False
                # Function to display the user's recipes
                show_my_recipes(username)


        elif profile_option == "Favorites":
            show_favorites(username)



def show_favorites(username):
    st.subheader("Your Favorite Recipes")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    conn.close()

    favorite_recipe_ids = fetch_user_favorites(user_id) # Fetch all favorites once at the start

    if favorite_recipe_ids:
        cols = st.columns(2)  # Create 2 columns for layout
        for i, recipe_id in enumerate(favorite_recipe_ids):
            recipe = fetch_recipe_by_id(recipe_id)
            if recipe:
                title = recipe["title"]
                description = recipe["description"]
                creator_username = recipe["creator_username"]

                with cols[i % 2]:  # Use modulo to alternate between columns
                    if st.button(title):  # Make title clickable
                        st.session_state.selected_recipe = recipe_id  # Save selected recipe ID
                        st.session_state.page = 'recipe_details'  # Navigate to details page

                    st.write(f"**Description:** {description}")  # Display recipe description
                    st.markdown(f"**Submitted by:** [**{creator_username}**](?username={creator_username})")  # Display the creator's username
                    if st.button("💔 Unfavorite", key=f"unfavorite_{recipe_id}"):
                        toggle_favorite(user_id, recipe_id)
                    st.write("---")
    else:
        st.write("You have no favorite recipes yet.")

def get_connection():
    return connect_db()  # Use your actual database connection function


def fetch_recipe_by_id(recipe_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.recipe_id, r.title, r.description, AVG(rr.rating) AS average_rating, u.username, u.user_id
        FROM Recipes r
        JOIN Users u ON r.user_id = u.user_id
        LEFT JOIN Recipe_Ratings rr ON r.recipe_id = rr.recipe_id  -- LEFT JOIN to include recipes with no ratings
        WHERE r.recipe_id = %s
        GROUP BY r.recipe_id, u.username, u.user_id
    """, (recipe_id,))
    
    recipe = cursor.fetchone()
    conn.close()

    if recipe:
        return {
            "recipe_id": recipe[0],
            "title": recipe[1],
            "description": recipe[2],
            "average_rating": recipe[3] if recipe[3] is not None else 0.0,  # Handle cases with no ratings
            "creator_username": recipe[4],
            "creator_user_id": recipe[5]
        }
    else:
        return None


def display_profile_picture(user_profile_pic):
    if isinstance(user_profile_pic, bytes):
        user_profile_pic = user_profile_pic.decode()

    if user_profile_pic:  # Check if the profile picture filename is provided
        full_path = os.path.join("uploads", user_profile_pic)

        # Check if the file exists
        if os.path.exists(full_path):
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{base64.b64encode(open(full_path, "rb").read()).decode()}" 
                    style="width: 230px; height: 230px; border-radius: 50%; object-fit: cover;" 
                    alt="Profile Picture">
                </div>
                <br>
                ''',
                unsafe_allow_html=True
            )
        else:
            show_default_profile_picture()  # Show default picture if file doesn't exist
    else:
        show_default_profile_picture()

def show_default_profile_picture():
    default_picture_path = "uploads/defaultprofile.png"
    st.markdown(
        f'''
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{base64.b64encode(open(default_picture_path, "rb").read()).decode()}" 
            style="width: 230px; height: 230px; border-radius: 50%; object-fit: cover;" 
            alt="Default Profile Picture">
        </div><br>
        ''',
        unsafe_allow_html=True
    )

def upload_profile_picture(username):
    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Ensure the uploaded file is an image
        if uploaded_file.type in ["image/jpeg", "image/png"]:
            # Set the path where the image will be saved
            file_path = os.path.join("uploads", uploaded_file.name)

            # Save the uploaded file to the specified path
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Optionally, update the user's profile picture in your database
            update_user_profile_picture(username, uploaded_file.name)
        else:
            st.error("Please upload a JPEG or PNG image.")

def update_user_profile_picture(username, filename):
    conn = get_connection()
    cursor = conn.cursor()
    # Fetch the user_id based on the username
    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:  # Ensure a valid user was found
        user_id = result[0]
        cursor.execute("UPDATE Users SET profile_pic = %s WHERE user_id = %s", (filename, user_id))
        conn.commit()
    else:
        st.error("User not found.")

def fetch_dietary_name(dietary_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Dietary WHERE dietary_id = %s", (dietary_id,))
    dietary_name = cursor.fetchone()
    conn.close()
    return dietary_name[0] if dietary_name else "None"
        
def show_my_recipes(username):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch recipes submitted by the user, including average ratings
    cursor.execute("""
        SELECT r.recipe_id, r.title, r.description, AVG(rr.rating) AS average_rating
        FROM Recipes r 
        JOIN Users u ON r.user_id = u.user_id 
        LEFT JOIN Recipe_Ratings rr ON r.recipe_id = rr.recipe_id  -- Use LEFT JOIN to include recipes with no ratings
        WHERE u.username = %s
        GROUP BY r.recipe_id, r.title, r.description
    """, (username,))
    
    recipes = cursor.fetchall()
    conn.close()

    if recipes:
        cols = st.columns(2)  # Create 2 columns for layout
        for i, recipe in enumerate(recipes):
            recipe_id, title, description, average_rating = recipe

            with cols[i % 2]:  # Use modulo to alternate between columns
                # Display recipe title as a clickable button
                if st.button(title, key=f"recipe_{recipe_id}"):
                    st.session_state.selected_recipe = recipe_id  # Save selected recipe ID

                # Display a bin icon for deletion
                delete_clicked = st.button("🗑️", key=f"delete_{recipe_id}")

                # Show confirmation message if delete button is clicked
                if delete_clicked:
                    st.write(f"Are you sure you want to delete '{title}'?")
                    confirm_delete = st.button("Yes, Delete", key=f"confirm_delete_{recipe_id}")
                    cancel_delete = st.button("Cancel", key=f"cancel_delete_{recipe_id}")

                    if confirm_delete:
                        # Call the delete_recipe function and display a message
                        message = delete_recipe(recipe_id)
                        st.success(message)
                        # Refresh the app to update the list of recipes
                        st.rerun()

                    elif cancel_delete:
                        st.write("Deletion cancelled.")

                # Display recipe description and average rating
                st.write(f"**Description:** {description}")
                st.write(f"**Average Rating:** {average_rating:.1f}" if average_rating is not None else "No ratings yet")
                st.write("---")
    else:
        st.write("This user has not submitted any recipes yet.")

def delete_recipe(recipe_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Start by deleting ratings for the recipe
        cursor.execute("DELETE FROM Recipe_Ratings WHERE recipe_id = %s", (recipe_id,))
        print(f"Deleted ratings for recipe ID: {recipe_id}")

        # Delete the recipe info details
        cursor.execute("DELETE FROM Recipe_Info WHERE recipeInfo_id = %s", (recipe_id,))
        print(f"Deleted Recipe_Info for recipe ID: {recipe_id}")

        # Finally, delete the recipe itself
        cursor.execute("DELETE FROM Recipes WHERE recipe_id = %s", (recipe_id,))
        print(f"Deleted recipe ID: {recipe_id}")

        # Commit the changes
        conn.commit()
        return "Recipe deleted successfully!"

    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
        return f"An error occurred: {e}"

    finally:
        conn.close()

        

def show_edit_recipe_form(recipe_id):
    # Fetch the selected recipe's details
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, description, cook_time, servings, ingredients, instructions
        FROM Recipes r
        JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
        WHERE r.recipe_id = %s
    """, (recipe_id,))
    
    recipe = cursor.fetchone()
    conn.close()

    if recipe:
        title, description, cook_time, servings, ingredients, instructions = recipe
        
        # Show the editing form with pre-filled values
        st.subheader("Edit Recipe")
        new_title = st.text_input("Recipe Title", value=title, key="edit_recipe_title")
        new_description = st.text_area("Recipe Description", value=description, key="edit_recipe_description")
        new_cook_time = st.number_input("Cook Time (minutes)", min_value=1, value=cook_time, key="edit_recipe_cook_time")
        new_servings = st.number_input("Servings", min_value=1, value=servings, key="edit_recipe_servings")
        new_ingredients = st.text_area("Ingredients (one per line)", value=ingredients, key="edit_recipe_ingredients")
        new_instructions = st.text_area("Instructions", value=instructions, key="edit_recipe_instructions")
        
        # Create two columns for "Save Changes" and "Cancel" buttons
        col1, col2 = st.columns(2)

        with col1:
            # Save Changes button
            if st.button("Save Changes", key="save_recipe_changes"):
                # Call the update function with the new values
                message = update_recipe(recipe_id, new_title, new_description, new_cook_time, new_servings, new_ingredients, new_instructions)
                st.success(message)
                st.session_state.editing_recipe = False  # Exit editing mode
                st.rerun()  # Rerun the app to update the state

        with col2:
            # Cancel button
            if st.button("Cancel", key="cancel_editing"):
                st.session_state.editing_recipe = False  # Exit editing mode
                st.rerun()  # Rerun the app to update the state


def update_recipe(recipe_id, title, description, cook_time, servings, ingredients, instructions):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Update the Recipes table
        cursor.execute("""
            UPDATE Recipes
            SET title = %s, description = %s
            WHERE recipe_id = %s
        """, (title, description, recipe_id))
        
        # Update the Recipe_Info table
        cursor.execute("""
            UPDATE Recipe_Info
            SET cook_time = %s, servings = %s, ingredients = %s, instructions = %s
            WHERE recipeInfo_id = %s
        """, (cook_time, servings, ingredients, instructions, recipe_id))
        
        # Commit the changes
        conn.commit()

    except Exception as e:
        # Rollback in case of an error
        conn.rollback()
        return f"An error occurred: {e}"

    finally:
        conn.close()

    return "Recipe updated successfully!"

def save_recipe(title, description, cook_time, servings, ingredients, instructions, username):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert into Recipes table
        cursor.execute(""" 
            INSERT INTO Recipes (title, description, user_id) 
            VALUES (%s, %s, (SELECT user_id FROM Users WHERE username=%s))
        """, (title, description, username))

        # Retrieve the last inserted recipe_id
        recipe_id = cursor.lastrowid

        # Insert into Recipe_Info table using the retrieved recipe_id
        cursor.execute(""" 
            INSERT INTO Recipe_Info (recipeInfo_id, cook_time, servings, ingredients, instructions) 
            VALUES (%s, %s, %s, %s, %s)
        """, (recipe_id, cook_time, servings, ingredients, instructions))

        # Commit the changes to the database
        conn.commit()

    except Exception as e:
        # Rollback in case of an error to avoid partial inserts
        conn.rollback()
        return f"An error occurred: {e}"

    finally:
        # Close the connection to free resources
        conn.close()

    return "Recipe added successfully!"

def update_profile(username, new_username, new_email, new_bio, new_dietary_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
        user_id = cursor.fetchone()

        if user_id is None:
            return "User not found."

        user_id = user_id[0]  # Extract user_id

        if new_dietary_id is not None:
            new_dietary_id = int(new_dietary_id)

        cursor.execute(""" 
            UPDATE Users 
            SET username = %s, email = %s, bio = %s, dietary_id = %s
            WHERE user_id = %s 
        """, (new_username, new_email, new_bio, new_dietary_id, user_id))
        conn.commit()
        return "Profile updated successfully!"
    except Exception as e:
        return f"Error: {e}"
    finally:
        if conn and conn.is_connected():
            conn.close()
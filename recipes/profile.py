
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
                # Clear query parameters and inject JavaScript to reload the page
                st.query_params.clear()
                st.markdown(
                    '''
                    <script type="text/javascript">
                        window.location.href = "/";
                    </script>
                    ''', unsafe_allow_html=True
                )

            # Call the recipe management after the profile is shown
            recipe_management(user_id)

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

# Recipe management feature code (Submit, Edit, Delete)
def recipe_management(user_id):
    st.sidebar.title("Recipe Management")

    # Dropdown to select action
    action = st.sidebar.selectbox("Manage Recipes", ["Submit Recipe", "Edit Recipe", "Delete Recipe"])

    if action == "Submit Recipe":
        st.subheader("Submit a New Recipe")
        recipe_name = st.text_input("Recipe Name")
        ingredients = st.text_area("Ingredients")
        instructions = st.text_area("Instructions")

        if recipe_name and ingredients and instructions:
            if st.button("Submit Recipe"):
                # Code to submit the recipe to the database
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Recipes (user_id, title, description) VALUES (%s, %s, %s)",
                               (user_id, recipe_name, ingredients + "\n" + instructions))
                conn.commit()
                conn.close()
                st.success(f"Recipe '{recipe_name}' submitted successfully!")

    elif action == "Edit Recipe":
        st.subheader("Edit Existing Recipes")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT recipe_id, title FROM Recipes WHERE user_id = %s", (user_id,))
        recipes = cursor.fetchall()
        conn.close()

        if recipes:
            recipe_titles = {recipe[0]: recipe[1] for recipe in recipes}  # Using 'recipe' as the correct iteration variable
            selected_recipe_id = st.selectbox("Select a Recipe to Edit", options=recipe_titles.keys(), format_func=lambda x: recipe_titles[x])

            if selected_recipe_id:
                new_name = st.text_input("New Recipe Name", value=recipe_titles[selected_recipe_id])
                new_ingredients = st.text_area("New Ingredients")
                new_instructions = st.text_area("New Instructions")

                if st.button("Update Recipe"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Recipes SET title = %s, description = %s WHERE recipe_id = %s",
                                   (new_name, new_ingredients + "\n" + new_instructions, selected_recipe_id))
                    conn.commit()
                    conn.close()
                    st.success(f"Recipe '{new_name}' updated successfully!")

    elif action == "Delete Recipe":
        st.subheader("Delete a Recipe")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT recipe_id, title FROM Recipes WHERE user_id = %s", (user_id,))
        recipes = cursor.fetchall()
        conn.close()

        if recipes:
            recipe_titles = {recipe[0]: recipe[1] for recipe in recipes}  # Using 'recipe' as the correct iteration variable
            selected_recipe_id = st.selectbox("Select a Recipe to Delete", options=recipe_titles.keys(), format_func=lambda x: recipe_titles[x])

            if selected_recipe_id:
                if st.button("Delete Recipe"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Recipes WHERE recipe_id = %s", (selected_recipe_id,))
                    conn.commit()
                    conn.close()
                    st.success("Recipe deleted successfully!")

# Call the profile display with recipes
def show_profile_with_recipes(user_id):
    show_profile(user_id)

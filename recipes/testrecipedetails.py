import streamlit as st
import mysql.connector
import base64, os
from db_connection import connect_db


# Function to render stars based on rating value
def render_stars(rating):
    full_star = '★'
    half_star = '☆'
    empty_star = '✩'
    
    full_stars = int(rating)  # Number of full stars
    half_stars = 1 if (rating - full_stars) >= 0.5 else 0  # Check for half star
    empty_stars = 5 - full_stars - half_stars  # Remaining stars are empty
    
    return full_star * full_stars + half_star * half_stars + empty_star * empty_stars

def show_default_recipe_img():
    default_picture_path = "uploads/recipe/defaultprofile.png"
    if os.path.exists(default_picture_path):
        with open(default_picture_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            st.markdown(
                f'''
                <div style="text-align: center;">
                    <img src="data:image/jpeg;base64,{img_data}" 
                    style="width: 230px; height: 230px; border-radius: 50%; object-fit: cover;" 
                    alt="Default Profile Picture">
                </div><br>
                ''',
                unsafe_allow_html=True
            )

def fetch_recipe_details(recipe_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    query = """
    SELECT r.title, r.description, r.image_src, 
           COALESCE(AVG(rr.rating), 0) AS average_rating, 
           ri.cook_time, ri.servings, ri.ingredients, ri.instructions, u.username
    FROM Recipes r
    JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
    JOIN Users u ON r.user_id = u.user_id  -- Join to get username
    LEFT JOIN Recipe_Ratings rr ON r.recipe_id = rr.recipe_id  -- Left join to get ratings
    WHERE r.recipe_id = %s
    GROUP BY r.recipe_id, r.title, r.description, r.image_src, ri.cook_time, ri.servings, ri.ingredients, ri.instructions, u.username  -- Group by necessary fields
    """
    params = (recipe_id,)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result

def fetch_user_favorites(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT recipe_id FROM Favorite WHERE user_id = %s", (user_id,))
    favorite_recipes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return favorite_recipes

# Individual Recipe Details page content
def recipe_details():
    recipe_id = st.session_state.selected_recipe
    recipe = fetch_recipe_details(recipe_id)

    if recipe:
        title, description, image_src, ratings, cook_time, servings, ingredients, instructions, username = recipe
        
        # Check if the logged-in user is the recipe creator
        if st.session_state.get('logged_in_username') == username:
            is_creator = True
        else:
            is_creator = False

        # If the logged-in user is the creator, show the update form
        if is_creator:
            st.subheader("Edit Recipe")
            update_recipe_form(recipe_id, title, description, cook_time, servings, ingredients, instructions, image_src)
        else:
            # Display the recipe details if the user is not the creator
            st.title(title)
            st.write(f"**Description:** {description}")
            if image_src:
                st.image(image_src, caption=title)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Rating:** {render_stars(ratings)}")
            with col2:
                st.write(f"**Cook Time:** {cook_time} minutes")
            with col3:
                st.write(f"**Servings:** {servings}")

                # Display the username as a clickable link
            if st.button(f"Submitted by: {username}", key=f"user_{username}_{recipe_id}"):  # Unique key for each button
                st.session_state.username = username  # Set the username in the session state
                st.session_state.page = 'user_profile'  # Set the page to user profile
                st.rerun()

            st.write("")  # Optional: smaller gap
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

            format_ingredients(ingredients)

            st.subheader("Instructions")
            st.write(instructions)

        if st.button("Back to Recipe List"):
            st.session_state.page = 'homepage'
            st.session_state.selected_recipe = None
            st.rerun()  # Rerun to load the recipe details page

    else:
        st.write("Recipe not found.")

def update_recipe_form(recipe_id, current_title, current_description, current_cook_time, current_servings, current_ingredients, current_instructions, current_image):
    new_title = st.text_input("Recipe Title", value=current_title, key="edit_recipe_title")
    new_description = st.text_area("Recipe Description", value=current_description, key="edit_recipe_description")
    new_cook_time = st.number_input("Cook Time (minutes)", min_value=1, value=current_cook_time, key="edit_cook_time")
    new_servings = st.number_input("Servings", min_value=1, value=current_servings, key="edit_servings")
    new_ingredients = st.text_area("Ingredients (one per line)", value=current_ingredients, key="edit_ingredients")
    new_instructions = st.text_area("Instructions", value=current_instructions, key="edit_instructions")

    # Add image upload functionality
    new_image_file = st.file_uploader("Upload Recipe Image", type=["jpg", "jpeg", "png"], key="edit_recipe_image")
    
    # Display current image if available
    if current_image:
        show_current_image(current_image)

    if st.button("Save Changes", key="save_recipe_changes"):
        # Set image_filename to the current image by default
        image_filename = current_image
        
        if new_image_file is not None:
            # Save the uploaded image to the 'uploads' directory
            image_filename = handle_image_upload(recipe_id, new_image_file, current_image)
            message = update_recipe_in_db(recipe_id, new_title, new_description, new_cook_time, new_servings, new_ingredients, new_instructions, image_filename)
            st.success(message)
            st.rerun()

# Helper function to show the current recipe image
def show_current_image(current_image):
    image_path = os.path.join("uploads/recipes/", current_image)
    if os.path.exists(image_path):
        st.image(image_path, caption="Current Recipe Image", use_column_width=True)

# Function to handle image upload
def handle_image_upload(recipe_id, new_image_file, current_image):
    if new_image_file:
        image_filename = f"{recipe_id}_{new_image_file.name}"
        with open(os.path.join("uploads", "recipes", image_filename), "wb") as f:
            f.write(new_image_file.getbuffer())
        return image_filename
    return current_image

def update_recipe_in_db(recipe_id, title, description, cook_time, servings, ingredients, instructions, image_filename):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Update Recipes table
        update_recipe_query = """
        UPDATE Recipes 
        SET title = %s, description = %s
        WHERE recipe_id = %s
        """
        cursor.execute(update_recipe_query, (title, description, recipe_id))

        # Update Recipe_Info table
        update_recipe_info_query = """
        UPDATE Recipe_Info
        SET cook_time = %s, servings = %s, ingredients = %s, instructions = %s, image = %s
        WHERE recipeInfo_id = %s
        """
        cursor.execute(update_recipe_info_query, (cook_time, servings, ingredients, instructions, image_filename, recipe_id))

        conn.commit()
        return "Recipe updated successfully!"
    
    except mysql.connector.Error as err:
        return f"Error updating recipe: {err}"

    finally:
        conn.close()

# Function to format ingredients in a two-column layout
def format_ingredients(ingredients):
    ingredient_list = ingredients.split("\n")
    
    section_name = "Ingredients"
    section_ingredients = []

    for line in ingredient_list:
        line = line.strip()
        if line:
            if line.endswith(":"):  
                if section_ingredients:
                    display_section(section_name, section_ingredients)
                    section_ingredients = []
                
                section_name = f"{line[:-1]} Ingredients"
            else:
                section_ingredients.append(line)

    if section_ingredients:
        display_section(section_name, section_ingredients)


# Helper function to display a section with ingredients
def display_section(section_name, ingredients):
    st.subheader(section_name)
    
    num_ingredients = len(ingredients)

    if num_ingredients <= 5:
        for ingredient in ingredients:
            st.write(f"- {ingredient}")
    else:
        cols = st.columns(2)
        
        for i in range(0, num_ingredients, 2):
            with cols[0]:
                if i < num_ingredients:
                    st.write(f"- {ingredients[i]}")
            
            with cols[1]:
                if i + 1 < num_ingredients:
                    st.write(f"- {ingredients[i + 1]}")

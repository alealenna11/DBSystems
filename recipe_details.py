import streamlit as st
import mysql.connector
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


# Fetch individual recipe details
def fetch_recipe_details(recipe_id):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT r.title, r.description, r.image_src, r.ratings, 
           ri.cook_time, ri.servings, ri.ingredients, ri.instructions, u.username
    FROM Recipes r
    JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
    JOIN Users u ON r.user_id = u.user_id  # Join to get username
    WHERE r.recipe_id = %s
    """
    cursor.execute(query, (recipe_id,))
    recipe = cursor.fetchone()
    conn.close()
    return recipe



# Individual Recipe Details page content
def recipe_details():
    recipe_id = st.session_state.selected_recipe
    recipe = fetch_recipe_details(recipe_id)

    if recipe:
        title, description, image_src, ratings, cook_time, servings, ingredients, instructions, username = recipe
        
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
        if username:
            user_link = f"[{username}](?username={username})"  # Create a link for the user profile
            st.write(f"**Submitted by:** {user_link}")

        st.write("")  # Optional: smaller gap
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

        format_ingredients(ingredients)

        st.subheader("Instructions")
        st.write(instructions)

        if st.button("Back to Recipe List"):
            st.session_state.page = 'homepage'
            st.session_state.selected_recipe = None
    else:
        st.write("Recipe not found.")


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

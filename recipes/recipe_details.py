import streamlit as st
import mysql.connector
from db_connection import connect_db

# Fetch individual recipe details
def fetch_recipe_details(recipe_id):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT r.title, r.description, r.image_src, AVG(rr.rating) AS avg_rating, 
           ri.cook_time, ri.servings, ri.ingredients, ri.instructions, u.username
    FROM Recipes r
    JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
    JOIN Users u ON r.user_id = u.user_id
    LEFT JOIN Recipe_Ratings rr ON r.recipe_id = rr.recipe_id
    WHERE r.recipe_id = %s
    GROUP BY r.recipe_id, u.username
    """
    cursor.execute(query, (recipe_id,))
    recipe = cursor.fetchone()
    conn.close()
    return recipe

def recipe_details():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None  

    recipe_id = st.session_state.selected_recipe
    recipe = fetch_recipe_details(recipe_id)

    if recipe:
        title, description, image_src, avg_rating, cook_time, servings, ingredients, instructions, username = recipe
        
        st.title(title)
        st.write(f"**Description:** {description}")

        if image_src:
            st.image(f"uploads/recipe/{image_src}", caption=title, width=300)

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Cook Time:** {cook_time} minutes")
        with col2:
            st.write(f"**Servings:** {servings}")

        if username:
            user_link = f"/?username={username}"  
            st.write(f"**Submitted by:** [**{username}**]({user_link})")

        st.write(f"**Average Rating:** {avg_rating:.1f}" if avg_rating else "**Average Rating:** Not yet rated")

        st.write("")  
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

        format_ingredients(ingredients)

        st.subheader("Instructions")
        st.write(instructions)

        # Rating logic
        if st.session_state.user_id and username != st.session_state.username:
            current_rating = get_user_rating(recipe_id, st.session_state.user_id)

            rating = st.number_input("Rate this recipe:", min_value=1, max_value=5, value=current_rating if current_rating else 3)
            if st.button("Submit Rating"):
                if submit_rating(recipe_id, st.session_state.user_id, rating):
                    st.success("Thank you for your rating!")
                    updated_recipe = fetch_recipe_details(recipe_id)
                    st.write(f"**Average Rating:** {updated_recipe[3]:.1f}" if updated_recipe[3] else "**Average Rating:** Not yet rated")
                else:
                    st.error("An error occurred while submitting your rating.")
        elif not st.session_state.user_id:
            st.warning("You need to be logged in to rate this recipe.")

        if st.button("Back to Recipe List"):
            st.session_state.page = 'homepage'
            st.session_state.selected_recipe = None
            st.rerun()  

    else:
        st.write("Recipe not found.")

def submit_rating(recipe_id, user_id, rating):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Check if the user has already rated this recipe
        cursor.execute("SELECT * FROM Recipe_Ratings WHERE user_id = %s AND recipe_id = %s", (user_id, recipe_id))
        existing_rating = cursor.fetchone()

        if existing_rating:
            # Update existing rating
            cursor.execute("UPDATE Recipe_Ratings SET rating = %s WHERE user_id = %s AND recipe_id = %s", (rating, user_id, recipe_id))
        else:
            # Insert the new rating
            cursor.execute("INSERT INTO Recipe_Ratings (user_id, recipe_id, rating) VALUES (%s, %s, %s)",
                           (user_id, recipe_id, rating))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error submitting rating: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_rating(recipe_id, user_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT rating FROM Recipe_Ratings WHERE user_id = %s AND recipe_id = %s", (user_id, recipe_id))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
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

def add_recipe():
    st.title("Add a New Recipe")

    with st.form(key='add_recipe_form'):
        title = st.text_input("Title", max_chars=100)
        description = st.text_area("Description", max_chars=500)
        image_src = st.text_input("Image Source (filename)", max_chars=255)
        cook_time = st.number_input("Cook Time (in minutes)", min_value=0)
        servings = st.number_input("Servings", min_value=1)
        ingredients = st.text_area("Ingredients (separate by line)", max_chars=5000)
        instructions = st.text_area("Instructions", max_chars=10000)

        dietary_types = ["Vegan", "Vegetarian", "Gluten-Free", "None"]  
        dietary_id = st.selectbox("Dietary Type", options=dietary_types)

        cuisine_types = ["Italian", "Chinese", "Indian", "Mexican", "None"]  
        cuisine_id = st.selectbox("Cuisine Type", options=cuisine_types)

        submit_button = st.form_submit_button("Add Recipe")

        if submit_button:
            user_id = st.session_state.user_id  
            if add_recipe_to_db(title, description, image_src, cook_time, servings, ingredients, instructions, dietary_id, cuisine_id, user_id):
                st.success("Recipe added successfully!")
            else:
                st.error("An error occurred while adding the recipe.")

def add_recipe_to_db(title, description, image_src, cook_time, servings, ingredients, instructions, dietary_id, cuisine_id, user_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(""" 
            INSERT INTO Recipes (title, description, image_src, user_id) 
            VALUES (%s, %s, %s, %s)
        """, (title, description, image_src, user_id))
        
        recipe_id = cursor.lastrowid
        
        cursor.execute(""" 
            INSERT INTO Recipe_Info (recipeInfo_id, cook_time, servings, ingredients, instructions, dietary_id, cuisine_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (recipe_id, cook_time, servings, ingredients, instructions, dietary_id, cuisine_id))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding recipe: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

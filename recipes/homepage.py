import streamlit as st
from utils import get_connection

def fetch_all_recipes():
    conn = get_connection()
    cursor = conn.cursor()

    # Query to fetch all recipes without any filters
    query = """
        SELECT r.title, r.description, r.ratings, u.user_id, u.username
            FROM Recipes r
            JOIN Users u ON r.user_id = u.user_id
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    # Creating a list of recipes from the fetched rows
    recipes = []
    for row in rows:
        recipe = {
           "title": row[0],
            "description": row[1],
            "ratings": row[2],  # Fetching ratings
            "user_id": row[3],
            "creator_username": row[4],
        }
        recipes.append(recipe)

    return recipes


def fetch_recipes(search_query=None, rating_filter=None, cuisine_filter=None, dietary_filter=None, cook_time_filter=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Base query for filtering recipes
    query = """
        SELECT r.title, r.description, r.ratings, u.user_id, u.username, ri.cook_time, ri.servings, ri.ingredients, ri.instructions, d.name, c.name
        FROM Recipes r
        JOIN Users u ON r.user_id = u.user_id
        JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
        LEFT JOIN Dietary d ON ri.dietary_id = d.dietary_id
        LEFT JOIN Cuisines c ON ri.cuisine_id = c.cuisine_id
        WHERE 1 = 1
    """
    params = []

    # Search query for filtering by title, creator username, or description
    if search_query:
        search_query = f"%{search_query}%"
        query += " AND (r.title LIKE %s OR u.username LIKE %s OR r.description LIKE %s)"
        params.extend([search_query, search_query, search_query])

    # Filtering by rating (if provided)
    if rating_filter and rating_filter != "All":
        query += " AND r.ratings = %s"
        params.append(rating_filter)

    # Filtering by cuisine (if provided)
    if cuisine_filter and cuisine_filter != "All":
        query += " AND c.name = %s"
        params.append(cuisine_filter)

    # Filtering by dietary preference (if provided)
    if dietary_filter and dietary_filter != "All":
        query += " AND d.name = %s"
        params.append(dietary_filter)

    # Filtering by cook time (if provided)
    if cook_time_filter:
        query += " AND ri.cook_time <= %s"
        params.append(cook_time_filter)

    # Executing the final query
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Creating a list of recipes from the fetched rows
    recipes = []
    for row in rows:
        recipe = {
            "title": row[0],
            "description": row[1],
            "ratings": row[2],
            "user_id": row[3],
            "creator_username": row[4],
            "cook_time": row[5],
            "servings": row[6],
            "ingredients": row[7],
            "instructions": row[8],
            "dietary": row[9],
            "cuisine": row[10]
        }
        recipes.append(recipe)

    return recipes

def display_stars(rating):
    full_stars = int(rating)  # Number of full stars
    half_star = 1 if rating % 1 >= 0.5 else 0  # Check for half star
    empty_stars = 5 - full_stars - half_star  # Remaining empty stars

    stars = "⭐" * full_stars + "⭐" * half_star + "☆" * empty_stars
    return stars


def show_home():
    st.title("Welcome to BiteZy!")
    st.write("Explore and manage recipes with ease.")
    st.write("### Recipe Blog")

    # Search box for filtering recipes by title, description, or creator
    search_query = st.text_input("Search recipes by title, description, or creator:", "")

    # Filters section
    st.write("#### Filter Recipes")

    # Filter by rating (dropdown)
    rating_filter = st.selectbox("Minimum Rating", ["All", 1, 2, 3, 4, 5])

    # Filter by cuisine (dropdown)
    cuisine_filter = st.selectbox("Cuisine", ["All", "Malay", "Indian", "Chinese", "Japanese", "Korean", "Thai", "Indonesian", "Vietnamese", "Mexican", "French", "Italian", "American", "Mediterranean", "Middle Eastern", "Filipino"])

    # Filter by dietary preferences (dropdown)
    dietary_filter = st.selectbox("Dietary Preference", ["All", "Vegetarian", "Vegan", "Pescatarian", "Flexitarian", "Gluten-Free", "Keto", "Paleo", "Low-FODMAP", "Diabetic", "Halal", "Kosher", "Raw Food"])

    # Filter by maximum cook time (slider for cook time in minutes)
    cook_time_filter = st.slider("Maximum Cook Time (in minutes)", 0, 50, 100)

    # Determine which query to run based on user input
    if search_query or rating_filter != "All" or cuisine_filter != "All" or dietary_filter != "All" or cook_time_filter < 100:
        # Fetch filtered recipes
        recipes = fetch_recipes(
            search_query=search_query if search_query else None,
            rating_filter=rating_filter if rating_filter != "All" else None,
            cuisine_filter=cuisine_filter if cuisine_filter != "All" else None,
            dietary_filter=dietary_filter if dietary_filter != "All" else None,
            cook_time_filter=cook_time_filter if cook_time_filter < 100 else None
        )
    else:
        # Fetch all recipes
        recipes = fetch_all_recipes()

    # Display recipes
    if recipes:
        cols = st.columns(2)  # Create two columns
        for idx, recipe in enumerate(recipes):
            with cols[idx % 2]:  # Cycle through columns
                stars = display_stars(recipe['ratings'])  # Get star representation
                st.markdown(
                    f"""
                    <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px;">
                        <h4>{recipe['title']}</h4>
                        <p><strong>Description:</strong> {recipe['description']}</p>
                        <p><strong>Creator:</strong> <a href="?username={recipe['creator_username']}">{recipe['creator_username']}</a></p>
                        <p><strong>Rating:</strong> {stars}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if (idx + 1) % 2 == 0 and idx + 1 < len(recipes):
                cols = st.columns(2)  # Reset columns for the new row
    else:
        st.write("No recipes found matching your search criteria.")

# Main function to display the homepage
if __name__ == "__main__":
    show_home()
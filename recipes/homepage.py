import streamlit as st
from db_connection import connect_db
from recipe_details import recipe_details  # Import recipe_details function

# Function to fetch recipes with filtering options
def fetch_recipes(search_query=None, rating_filter=None, cuisine_filter=None, dietary_filter=None, cook_time_filter=None):
    conn = connect_db()
    cursor = conn.cursor()

    # Base query for filtering recipes
    query = """
        SELECT r.recipe_id, r.title, r.description, AVG(rr.rating) AS average_rating, u.username, ri.cook_time, ri.servings, ri.ingredients, ri.instructions, d.name AS dietary_name, c.name AS cuisine_name
        FROM Recipes r
        JOIN Users u ON r.user_id = u.user_id
        JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
        LEFT JOIN Dietary d ON ri.dietary_id = d.dietary_id
        LEFT JOIN Cuisines c ON ri.cuisine_id = c.cuisine_id
        LEFT JOIN Recipe_Ratings rr ON r.recipe_id = rr.recipe_id
        WHERE 1 = 1
    """
    params = []

    # Search query for filtering by title, creator username, or description
    if search_query:
        search_query = f"%{search_query}%"
        query += " AND (r.title LIKE %s OR u.username LIKE %s OR r.description LIKE %s)"
        params.extend([search_query, search_query, search_query])

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

    # Grouping by recipe ID to calculate the average rating correctly
    query += " GROUP BY r.recipe_id, r.title, r.description, u.username, ri.cook_time, ri.servings, ri.ingredients, ri.instructions, d.name, c.name"

    # Filtering by rating (if provided)
    if rating_filter and rating_filter != "All":
        query += " HAVING AVG(rr.rating) >= %s"
        params.append(rating_filter)

    # Executing the final query
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Creating a list of recipes from the fetched rows
    recipes = []
    for row in rows:
        recipe = {
            "recipe_id": row[0],
            "title": row[1],
            "description": row[2],
            "ratings": row[3] or 0,  # Default to 0 if no ratings
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

# Modify the show_homepage function to ensure the rating filter is passed correctly
def show_homepage():
    if st.session_state.get('logged_in', False):
        st.title(f"Welcome back, {st.session_state.username}!")  # Show welcome message
    else:
        st.title("Welcome to Bitezy!")

    # Search bar for recipes
    search_query = st.text_input("Search for recipes by title, description, or username:")

    # Filters section
    st.write("#### Filter Recipes")

    # Create columns for filters
    col1, col2, col3 = st.columns(3)

    # Filter by rating (dropdown)
    with col1:
        rating_filter = st.selectbox("Minimum Rating", ["All", 1, 2, 3, 4, 5])

    # Filter by cuisine (dropdown)
    with col2:
        cuisine_filter = st.selectbox("Cuisine", ["All", "Malay", "Indian", "Chinese", "Japanese", "Korean", "Thai", "Indonesian", "Vietnamese", "Mexican", "French", "Italian", "American", "Mediterranean", "Middle Eastern", "Filipino"])

    # Filter by dietary preferences (dropdown)
    with col3:
        dietary_filter = st.selectbox("Dietary Preference", ["All", "Vegetarian", "Vegan", "Pescatarian", "Gluten-Free", "Halal", "Raw Food"])

    # Filter by maximum cook time (slider for cook time in minutes)
    cook_time_filter = st.slider("Maximum Cook Time (in minutes)", 0, 120, 100)

    # Fetch recipes based on search and filter criteria
    recipes = fetch_recipes(
        search_query=search_query if search_query else None,
        rating_filter=int(rating_filter) if rating_filter != "All" else None,  # Convert rating to int if not "All"
        cuisine_filter=cuisine_filter if cuisine_filter != "All" else None,
        dietary_filter=dietary_filter if dietary_filter != "All" else None,
        cook_time_filter=cook_time_filter if cook_time_filter < 120 else None
    )

    # Call the recipe list function to display the recipes
    recipe_list(recipes)

# Recipe List page content
def recipe_list(recipes):
    st.subheader("Recipe List")

    # Display a list of recipes in a 2-column format
    if recipes:
        cols = st.columns(2)  # Create 2 columns for layout
        for i, recipe in enumerate(recipes):
            recipe_id = recipe["recipe_id"]
            title = recipe["title"]
            description = recipe["description"]
            ratings = recipe["ratings"]
            username = recipe["creator_username"]

            with cols[i % 2]:  # Use modulo to alternate between columns
                if st.button(title):  # Make title clickable
                    st.session_state.selected_recipe = recipe_id  # Save selected recipe ID
                    st.session_state.page = 'recipe_details'  # Navigate to details page
                    st.rerun()  # Rerun to load the recipe details page

                st.write(f"**Description:** {description}")  # Display recipe description
                st.write(f"**Submitted by:** {username}")  # Display the user who submitted the recipe

                # Display the average rating
                if ratings:
                    st.write(f"**Average Rating:** {ratings:.1f} ⭐️")  # Display average rating with a star
                else:
                    st.write("**Average Rating:** No ratings yet.")  # Handle case with no ratings

                st.write("---")  # Separator for better readability
    else:
        st.write("No recipes found matching your search criteria.")

# Main execution
if __name__ == "__main__":
    st.set_page_config(page_title="Bitezy", layout="wide")
    
    # Initialize the session state for page navigation if not already set
    if 'page' not in st.session_state:
        st.session_state.page = 'homepage'  # Default to homepage
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Default logged-in status

    # Main app logic based on session state
    if st.session_state.page == 'homepage':
        show_homepage()
    elif st.session_state.page == 'recipe_details':
        recipe_details()  # This function should render the selected recipe details

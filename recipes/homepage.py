import streamlit as st
from db_connection import connect_db
from recipe_details import recipe_details  # Import recipe_details function

# Function to fetch recipes with filtering options

def fetch_recipes(search_query=None, rating_filter=None, cuisine_filter=None, dietary_filter=None, cook_time_filter=None):
    # Unpack the database and collections
    db, recipes_collection, _, _, recipe_ratings_collection, cuisines_collection, dietary_collection = connect_db()

    # Perform MongoDB queries directly on the collections
    query = {}

    if search_query:
        query['$or'] = [
            {'title': {'$regex': search_query, '$options': 'i'}},
            {'description': {'$regex': search_query, '$options': 'i'}}
        ]

    if cuisine_filter and cuisine_filter != "All":
        query['cuisine'] = cuisine_filter

    if dietary_filter and dietary_filter != "All":
        query['dietary'] = dietary_filter

    if cook_time_filter:
        query['cook_time'] = {'$lte': cook_time_filter}

    # Fetch and process recipes
    recipes = list(recipes_collection.find(query))
    for recipe in recipes:
        recipe['ratings'] = recipe_ratings_collection.find({'recipe_id': recipe['_id']}).count()
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

    # Unpack collections
    db, _, _, _, _, cuisines_collection, dietary_collection = connect_db()

    # Create columns for filters
    col1, col2, col3 = st.columns(3)

    # Filter by rating (dropdown)
    with col1:
        rating_filter = st.selectbox("Minimum Rating", ["All", 1, 2, 3, 4, 5])

    # Filter by cuisine (dropdown)
    with col2:
        cuisine_filter = st.selectbox(
            "Cuisine",
            ["All"] + [cuisine['name'] for cuisine in cuisines_collection.find()]
        )

    # Filter by dietary preferences (dropdown)
    with col3:
        dietary_filter = st.selectbox(
            "Dietary Preference",
            ["All"] + [dietary['name'] for dietary in dietary_collection.find()]
        )

    # Filter by maximum cook time (slider for cook time in minutes)
    cook_time_filter = st.slider("Maximum Cook Time (in minutes)", 0, 120, 100)

    # Fetch recipes based on search and filter criteria
    recipes = fetch_recipes(
        search_query=search_query if search_query else None,
        rating_filter=int(rating_filter) if rating_filter != "All" else None,
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
            recipe_id = recipe["_id"]
            title = recipe["title"]
            description = recipe["description"]
            ratings = recipe.get("average_rating", 0)
            username = recipe.get("creator_username", "Unknown")

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

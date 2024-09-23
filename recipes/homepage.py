import streamlit as st
from utils import get_connection

def fetch_recipes(search_query=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Modify the query to allow filtering by title, creator username, or description if search_query is provided
    if search_query:
        search_query = f"%{search_query}%"  # Adding wildcards for partial match
        cursor.execute(""" 
            SELECT r.title, r.description, r.ratings, u.user_id, u.username
            FROM Recipes r
            JOIN Users u ON r.user_id = u.user_id
            WHERE r.title LIKE %s OR u.username LIKE %s OR r.description LIKE %s
        """, (search_query, search_query, search_query))
    else:
        cursor.execute(""" 
            SELECT r.title, r.description, r.ratings, u.user_id, u.username
            FROM Recipes r
            JOIN Users u ON r.user_id = u.user_id
        """)

    rows = cursor.fetchall()
    conn.close()

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

def display_stars(rating):
    full_stars = int(rating)  # Number of full stars
    half_star = 1 if rating % 1 >= 0.5 else 0  # Check for half star
    empty_stars = 5 - full_stars - half_star  # Remaining empty stars

    stars = "⭐" * full_stars + "⭐" * half_star + "☆" * empty_stars
    return stars


def show_home():
    # Add a search box for filtering recipes
    search_query = st.text_input("Search recipes by title, description, or creator:", "")

    # Fetch recipes with the search query if provided
    recipes = fetch_recipes(search_query)

    st.title("Welcome to BiteZy!")
    st.write("Explore and manage recipes with ease.")
    st.write("### Recipe Blog")

    if recipes:
        cols = st.columns(2)  # Create two columns

        for idx, recipe in enumerate(recipes):
            with cols[idx % 2]:  # Cycle through the columns
                stars = display_stars(recipe['ratings'])  # Get star representation
                st.markdown(
                    f"""
                    <div style="border: 2px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px;">
                        <h4>{recipe['title']}</h4>
                        <p><strong>Description:</strong> {recipe['description']}</p>
                        <p><strong>Creator:</strong> <a href="?username={recipe['creator_username']}">{recipe['creator_username']}</a></p>
                        <p><strong>Rating:</strong> {stars}</p>  <!-- Display stars here -->
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

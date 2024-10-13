import streamlit as st
from utils import get_connection
from homepage import display_stars

# def fetch_recipe_by_id(recipe_id):
#     conn = get_connection()
#     cursor = conn.cursor()

#     # Query to fetch the recipe details by recipe_id
#     query = """
#         SELECT r.title, r.description, r.ratings, u.username, ri.cook_time, ri.servings, ri.ingredients, ri.instructions, d.name, c.name
#         FROM Recipes r
#         JOIN Users u ON r.user_id = u.user_id
#         JOIN Recipe_Info ri ON r.recipe_id = ri.recipeInfo_id
#         LEFT JOIN Dietary d ON ri.dietary_id = d.dietary_id
#         LEFT JOIN Cuisines c ON ri.cuisine_id = c.cuisine_id
#         WHERE r.recipe_id = %s
#     """
#     cursor.execute(query, (recipe_id,))
#     row = cursor.fetchone()
#     conn.close()

#     # Return the recipe details
#     if row:
#         recipe = {
#             "title": row[0],
#             "description": row[1],
#             "ratings": row[2],
#             "creator_username": row[3],
#             "cook_time": row[4],
#             "servings": row[5],
#             "ingredients": row[6],
#             "instructions": row[7],
#             "dietary": row[8],
#             "cuisine": row[9]
#         }
#         return recipe
#     else:
#         return None

# Display recipe details in the page
def show_recipe_info():
    st.title("Welcome to BiteZy!")
    # # Get recipe_id from query parameters
    # recipe_id = st.experimental_get_query_params().get("recipe_id", [None])[0]
    
    # if recipe_id:
    #     recipe = fetch_recipe_by_id(recipe_id)
    #     if recipe:
    #         st.title(recipe['title'])
    #         st.write(f"**Description:** {recipe['description']}")
    #         st.write(f"**Creator:** {recipe['creator_username']}")
    #         st.write(f"**Rating:** {display_stars(recipe['ratings'])}")
    #         st.write(f"**Cuisine:** {recipe['cuisine']}")
    #         st.write(f"**Dietary Preference:** {recipe['dietary']}")
    #         st.write(f"**Cook Time:** {recipe['cook_time']} minutes")
    #         st.write(f"**Servings:** {recipe['servings']}")
    #         st.write("### Ingredients")
    #         st.write(recipe['ingredients'])
    #         st.write("### Instructions")
    #         st.write(recipe['instructions'])
    #     else:
    #         st.write("Recipe not found.")
    # else:
    #     st.write("No recipe selected.")

if __name__ == "__main__":
    show_recipe_info()
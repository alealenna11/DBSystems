import streamlit as st
from db_connection import connect_db
from user_profile import fetch_user_favorites, add_to_favorites

# Fetch individual recipe details
def fetch_recipe_details(recipe_id):
    db, recipes_collection, _, recipe_info_collection, recipe_ratings_collection, *_ = connect_db()

    # Fetch recipe details
    recipe = recipes_collection.find_one({"_id": recipe_id})
    recipe_info = recipe_info_collection.find_one({"recipe_id": recipe_id})
    recipe_ratings = list(recipe_ratings_collection.find({"recipe_id": recipe_id}))

    # Calculate average rating
    avg_rating = (
        sum(rating.get("rating", 0) for rating in recipe_ratings) / len(recipe_ratings)
        if recipe_ratings
        else None
    )

    return recipe, recipe_info, avg_rating, recipe_ratings


def recipe_details():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    recipe_id = st.session_state.selected_recipe
    recipe, recipe_info, avg_rating, recipe_ratings = fetch_recipe_details(recipe_id)

    if recipe:
        title = recipe.get("title")
        description = recipe.get("description")
        image_src = recipe.get("image_src")
        cook_time = recipe_info.get("cook_time") if recipe_info else None
        servings = recipe_info.get("servings") if recipe_info else None
        ingredients = recipe_info.get("ingredients") if recipe_info else None
        instructions = recipe_info.get("instructions") if recipe_info else None
        username = recipe.get("creator_username", "Unknown")

        st.title(title)
        st.write(f"**Description:** {description}")

        if image_src:
            st.image(f"recipes/uploads/recipe_images/{image_src}", caption=title, width=300)

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Cook Time:** {cook_time} minutes" if cook_time else "**Cook Time:** N/A")
        with col2:
            st.write(f"**Servings:** {servings}" if servings else "**Servings:** N/A")

        if username:
            st.write(f"**Submitted by:** {username}")

        st.write(f"**Average Rating:** {avg_rating:.1f}" if avg_rating else "**Average Rating:** Not yet rated")

        st.write("")
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

        format_ingredients(ingredients)

        st.subheader("Instructions")
        st.write(instructions if instructions else "No instructions provided.")

        # Favorite button logic
        if st.session_state.user_id:  # Check if user is logged in
            favorite_recipe_ids = fetch_user_favorites(st.session_state.user_id)

            if recipe_id not in favorite_recipe_ids:
                if st.button("Add to Favorites"):
                    add_to_favorites(st.session_state.user_id, recipe_id)
                    st.success("Recipe added to your favorites!")
            else:
                st.write("This recipe is already in your favorites.")
        else:
            st.warning("You need to be logged in to favorite this recipe.")

        # Rating logic
        if st.session_state.user_id and username != st.session_state.username:
            current_rating = get_user_rating(recipe_id, st.session_state.user_id)

            rating = st.number_input("Rate this recipe:", min_value=1, max_value=5, value=current_rating or 3)
            if st.button("Submit Rating"):
                if submit_rating(recipe_id, st.session_state.user_id, rating):
                    st.success("Thank you for your rating!")
                    updated_recipe, _, updated_avg_rating, _ = fetch_recipe_details(recipe_id)
                    st.write(f"**Average Rating:** {updated_avg_rating:.1f}" if updated_avg_rating else "**Average Rating:** Not yet rated")
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
    _, _, _, _, recipe_ratings_collection, *_ = connect_db()
    try:
        existing_rating = recipe_ratings_collection.find_one({"recipe_id": recipe_id, "user_id": user_id})

        if existing_rating:
            # Update existing rating
            recipe_ratings_collection.update_one(
                {"recipe_id": recipe_id, "user_id": user_id},
                {"$set": {"rating": rating}}
            )
        else:
            # Insert the new rating
            recipe_ratings_collection.insert_one({
                "recipe_id": recipe_id,
                "user_id": user_id,
                "rating": rating
            })
        return True
    except Exception as e:
        st.error(f"Error submitting rating: {e}")
        return False

def get_user_rating(recipe_id, user_id):
    _, _, _, _, recipe_ratings_collection, *_ = connect_db()
    rating = recipe_ratings_collection.find_one({"recipe_id": recipe_id, "user_id": user_id})
    return rating.get("rating") if rating else None

# Function to format ingredients in a two-column layout
def format_ingredients(ingredients):
    if not ingredients:
        st.write("No ingredients provided.")
        return

    ingredient_list = ingredients if isinstance(ingredients, list) else ingredients.split("\n")

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

# recipeManagement.py
# Command to run: python -m streamlit run recipes/recipeManagement.py
import streamlit as st
from pymongo import MongoClient
import random
import logging
from PIL import Image
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# MongoDB connection
def connect_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['inf2003_db']  # Database name
    recipes_collection = db['recipes']
    return recipes_collection

# Function to check if an image exists before loading
def load_image(image_path):
    if os.path.exists(image_path):
        return Image.open(image_path)
    else:
        st.warning(f"Image not found: {image_path}")
        return None

# Confirmation dialog function
def confirm_action(action_type):
    """Displays a confirmation dialog before executing an action."""
    st.write(f"### Are you sure you want to {action_type} this recipe?")
    return st.button(f"Confirm {action_type.capitalize()}")

# Styling for Streamlit app
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content { 
        background: #e3f2fd; 
    }
    h1 { 
        color: #4CAF50; 
        text-align: center; 
        font-family: 'Arial', sans-serif; 
    }
    input, textarea { 
        font-size: 18px !important; 
        border-radius: 10px; 
        padding: 10px; 
        border: 1px solid #ccc; 
        width: 100%; 
    }
    </style>
""", unsafe_allow_html=True)

# Predefined recipes for generation
PREDEFINED_RECIPES = {
    "American": [
        {"title": "Chocolate Cake", "description": "A delicious chocolate cake recipe."},
        {"title": "Apple Pie", "description": "Traditional apple pie recipe."},
    ],
    "French": [
        {"title": "Macarons", "description": "A sweet meringue dessert."},
        {"title": "Chocolate Mousse", "description": "Light and creamy dessert."},
    ],
    "Chinese": [
        {"title": "Chicken Rice", "description": "Tender chicken with soy sauce marinade."}
    ],
}

# Recipe submission and generation
def submit_and_generate_recipe():
    st.title("🍳 Submit and Generate a Recipe")
    recipes_collection = connect_db()

    cuisine_type = st.selectbox("Cuisine Type", list(PREDEFINED_RECIPES.keys()) + ["Other"])
    num_recipes = st.slider("Number of recipes to generate", 1, 5, 1)

    if st.button("Generate Recipes"):
        for _ in range(num_recipes):
            if cuisine_type in PREDEFINED_RECIPES:
                recipe = random.choice(PREDEFINED_RECIPES[cuisine_type])
                recipes_collection.insert_one(recipe)
                st.success(f"Recipe '{recipe['title']}' generated and saved successfully!")

    with st.form("submit_recipe_form"):
        title = st.text_input("Recipe Title")
        description = st.text_area("Recipe Description")
        submit = st.form_submit_button("Submit Recipe")

        if submit:
            if title and description:
                recipe = {"title": title, "description": description}
                recipes_collection.insert_one(recipe)
                st.success(f"Recipe '{title}' submitted successfully!")
            else:
                st.error("Please fill in all fields.")

# Edit recipe functionality
def edit_recipe():
    st.title("✏️ Edit a Recipe")
    recipes_collection = connect_db()

    recipe_id = st.text_input("Enter Recipe ID to edit:")
    if recipe_id:
        recipe = recipes_collection.find_one({"_id": recipe_id})

        if recipe:
            with st.form("edit_recipe_form"):
                title = st.text_input("Recipe Title", value=recipe["title"])
                description = st.text_area("Recipe Description", value=recipe["description"])
                submit = st.form_submit_button("Update Recipe")

                if submit:
                    updated_recipe = {"title": title, "description": description}
                    recipes_collection.update_one({"_id": recipe_id}, {"$set": updated_recipe})
                    st.success("Recipe updated successfully!")
        else:
            st.error("Recipe not found.")

# Delete recipe functionality
def delete_recipe():
    st.title("🗑️ Delete a Recipe")
    recipes_collection = connect_db()

    recipe_id = st.text_input("Enter Recipe ID to delete:")
    if recipe_id:
        if st.button("Delete Recipe"):
            recipes_collection.delete_one({"_id": recipe_id})
            st.success(f"Recipe with ID '{recipe_id}' deleted successfully!")

# Sidebar navigation
st.sidebar.title("Recipe Management")
option = st.sidebar.radio("Choose an action", ["Submit & Generate Recipe", "Edit Recipe", "Delete Recipe"])

if option == "Submit & Generate Recipe":
    submit_and_generate_recipe()
elif option == "Edit Recipe":
    edit_recipe()
elif option == "Delete Recipe":
    delete_recipe()

#python  -m streamlit run recipes/recipeManagement.py
#python  -m streamlit run recipes/app.py
import streamlit as st
import requests
import logging
import random
from PIL import Image
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

# API Request Helper Functions with Enhanced Error Handling
def api_post(url, payload):
    '''Helper function to make POST requests to the API with error handling.'''
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            logging.info(f"POST request successful: {response.status_code}")
            return response
        elif response.status_code == 400:
            st.error("Bad Request: Please check the submitted data.")
        elif response.status_code == 500:
            st.error("Server Error: Please try again later.")
        else:
            st.error(f"Unexpected error: {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"POST request failed: {e}")
        st.error(f"API request failed: {e}")
        return None

# Function to check if an image exists before loading
def load_image(image_path):
    if os.path.exists(image_path):
        return Image.open(image_path)
    else:
        st.warning(f"Image not found: {image_path}")
        return None

# Session State Management
if 'recipe_name' not in st.session_state:
    st.session_state['recipe_name'] = ""
if 'ingredients' not in st.session_state:
    st.session_state['ingredients'] = ""
if 'steps' not in st.session_state:
    st.session_state['steps'] = ""

# Confirmation dialog function
def confirm_action(action_type):
    '''Displays a confirmation dialog before executing an action.'''
    st.write(f"### Are you sure you want to {action_type} this recipe?")
    return st.button(f"Confirm {action_type.capitalize()}")

# Styling and UI Configuration
st.markdown("""
    <style>
    .stApp {
        background-color: #ffb3b3;
    }
    .sidebar .sidebar-content { 
        background: #ffb3b3; 
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
    label {
        color: #FF4500; 
        font-weight: bold;
        font-size: 16px;
    }
    .recipe-title {
        font-size: 24px;
        font-weight: bold;
        color: #00FFFF;
    }
    .recipe-content {
        font-size: 18px;
        color: #FFFFFF;
        line-height: 1.6;
    }
    .submit-button button {
        background-color: #90ee90;
        color: black;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        transition: 0.3s ease;
    }
    .submit-button button:hover {
        background-color: #76c776;
    }
    .recipe-box {
        background-color: #e9f5f2;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Define image paths (ensure these paths are correct)
submit_image_path = "recipes/submitRecipe.jpg"
edit_image_path = "recipes/editRecipe.jpg"
delete_image_path = "recipes/deleteRecipe.jpg"

# Load images with error handling
submit_image = load_image(submit_image_path)
edit_image = load_image(edit_image_path)
delete_image = load_image(delete_image_path)


# Cuisines data from the table
cuisine_type_options = [
    "Malay", "Indian", "Chinese", "Japanese", "Korean", "Thai",
    "Indonesian", "Vietnamese", "Mexican", "French", "Italian",
    "American", "Mediterranean", "Middle Eastern", "Filipino"
]

# Dietary data from the table
dietary_restrictions_options = [
    "Vegetarian", "Vegan", "Pescatarian", "Flexitarian", "Gluten-Free",
    "Keto", "Paleo", "Low-FODMAP", "Diabetic", "Halal", "Kosher", "Raw Food"
]

# Recipes data categorized by cuisine
PREDEFINED_RECIPES = {
    "American": [
        {"title": "Chocolate Cake", "description": "A delicious chocolate cake recipe."},
        {"title": "Apple Pie", "description": "Traditional apple pie recipe."},
        {"title": "Cinnamon Bun", "description": "Warm cinnamon bun perfect for Christmas."},
        {"title": "Popsicle", "description": "Cold, good for summer days."},
        {"title": "Strawberry Shortcake", "description": "Fresh strawberry with cream."}
    ],
    "French": [
        {"title": "The Ultimate Berry Crumble", "description": "Sweet and savoury dessert."},
        {"title": "Chocolate Croissant", "description": "Crispy and buttery croissant spread with chocolate."},
        {"title": "Macarons", "description": "A sweet meringue, a delicate duet of almond and sugar."},
        {"title": "Chocolate Mousse", "description": "Savoury or sweet dish with the consistency of a light pudding."}
    ],
    "Chinese": [
        {"title": "Chicken Rice", "description": "Tender chicken with soy sauce marinade."}
    ],
    "Other": [
        {"title": "Hot Chocolate", "description": "Hot chocolate with marshmallow."},
        {"title": "Treasure Sandwich", "description": "Ham and cheese sandwich."},
        {"title": "dddd", "description": "hhhh"}
    ]
}

# Utility function for displaying title
def custom_title(title):
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)

# Submit Recipe + Recipe Generator Combined Functionality
def submit_and_generate_recipe():
    st.title("🍳 Generate and Submit a New Recipe")
    if submit_image:
        st.image(submit_image, use_column_width=True)
    st.subheader("Generate a Recipe")

    cuisine_type = st.selectbox("Select preferred cuisine type", cuisine_type_options)
    dietary_restrictions = st.selectbox("Select dietary restrictions or preferences", dietary_restrictions_options)

    num_recipes = st.number_input("Number of recipes to generate", min_value=1, max_value=5, step=1, value=1)

    if st.button("Generate Recipes"):
        recipes = []
        for _ in range(num_recipes):
            # Select a random recipe based on the chosen cuisine type
            if cuisine_type in PREDEFINED_RECIPES:
                recipe = random.choice(PREDEFINED_RECIPES[cuisine_type])
                recipe_name = recipe["title"]
                recipe_description = recipe["description"]
            else:
                recipe_name = f"{cuisine_type.capitalize()} Dish"
                recipe_description = f"{cuisine_type.capitalize()} Style Dish"

            # Apply dietary restriction description
            if dietary_restrictions:
                recipe_description += f" and {dietary_restrictions.lower()} friendly."

            recipes.append((recipe_name, recipe_description))

        # Display the generated recipes with updated styling
        for idx, (recipe_name, recipe_description) in enumerate(recipes, start=1):
            st.markdown(f"""
                <div class="recipe-box" style="background-color:#8B4513; padding:20px; border-radius:10px; margin-bottom:20px; box-shadow:0 0 15px rgba(0, 0, 0, 0.1);">
                    <div class="recipe-title" style="font-size:24px; font-weight:bold; color:#FFD700;">Recipe {idx}: {recipe_name}</div>
                    <div class="recipe-content" style="font-size:18px; color:#FFFFFF;">{recipe_description}</div>
                </div>
            """, unsafe_allow_html=True)
            st.session_state['recipe_name'] = recipe_name
            st.session_state['ingredients'] = "Generated ingredients"
            st.session_state['steps'] = "Generated steps"

    st.subheader("Submit Your Recipe")
    with st.form(key='recipe_form'):
        st.session_state['recipe_name'] = st.text_input("Recipe Name", value=st.session_state['recipe_name'], placeholder="Enter your recipe name")
        st.session_state['ingredients'] = st.text_area("Ingredients", value=st.session_state['ingredients'], placeholder="List your ingredients here")
        st.session_state['steps'] = st.text_area("Steps", value=st.session_state['steps'], placeholder="Write down the steps for your recipe")
        submit_button = st.form_submit_button(label="Submit Recipe ✨")

    if submit_button:
        payload = {
            "name": st.session_state['recipe_name'],
            "ingredients": st.session_state['ingredients'],
            "steps": st.session_state['steps']
        }
        if confirm_action("submit"):
            # Simulate API POST request (replace with actual API call)
            st.success(f"🎉 Your recipe '{st.session_state['recipe_name']}' has been submitted successfully!")

# Confirmation dialog function
def confirm_action(action_type):
    '''Displays a confirmation dialog before executing an action.'''
    st.write(f"### Are you sure you want to {action_type} this recipe?")
    return st.button(f"Confirm {action_type.capitalize()}")

# Edit Recipe Functionality
def edit_recipe():
    custom_title("✏️ Edit Your Recipe")
    if edit_image:
        st.image(edit_image, use_column_width=True)

    recipe_id = st.text_input("Enter the Recipe ID to edit:", placeholder="Enter recipe ID")
    if recipe_id:
        # Simulate fetching the recipe for editing (replace with actual API call)
        recipe = {"name": "Sample Recipe", "ingredients": "Sample Ingredients", "steps": "Sample Steps"}
        with st.form(key='edit_recipe_form'):
            st.session_state['recipe_name'] = st.text_input("Recipe Name", value=recipe.get('name'))
            st.session_state['ingredients'] = st.text_area("Ingredients", value=recipe.get('ingredients'))
            st.session_state['steps'] = st.text_area("Steps", value=recipe.get('steps'))
            edit_button = st.form_submit_button(label="Save Changes 💾")

        if edit_button:
            payload = {"name": st.session_state['recipe_name'], "ingredients": st.session_state['ingredients'], "steps": st.session_state['steps']}
            if confirm_action("edit"):
                # Simulate API PUT request (replace with actual API call)
                st.success(f"🎉 Your recipe '{st.session_state['recipe_name']}' has been updated successfully!")

# Delete Recipe Functionality
def delete_recipe():
    custom_title("🗑️ Delete Recipe")
    if delete_image:
        st.image(delete_image, use_column_width=True)

    recipe_id = st.text_input("Enter the Recipe ID to delete:", placeholder="Enter recipe ID")
    reasons = ["No longer needed", "Recipe has errors", "Duplicate recipe", "Other, please specify"]
    selected_reason = st.selectbox("Reason for deleting the recipe", reasons)
    other_reason = st.text_area("Please specify your reason:") if selected_reason == "Other, please specify" else ""

    final_reason = other_reason if other_reason else selected_reason
    delete_button = st.button("Delete Recipe ❌")

    if delete_button and recipe_id:
        payload = {"recipe_id": recipe_id, "reason": final_reason}
        if confirm_action("delete"):
            # Simulate API DELETE request (replace with actual API call)
            st.success(f"🎉 Recipe {recipe_id} has been deleted successfully!")

# Sidebar navigation
st.sidebar.title("Recipe Management")
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
page = st.sidebar.selectbox("Choose a page", ["Submit & Generate Recipe", "Edit Recipe", "Delete Recipe"])

# Page routing
if page == "Submit & Generate Recipe":
    submit_and_generate_recipe()
elif page == "Edit Recipe":
    edit_recipe()
elif page == "Delete Recipe":
    delete_recipe()

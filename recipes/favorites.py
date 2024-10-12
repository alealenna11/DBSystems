import streamlit as st
import mysql.connector
from db_connection import connect_db

def fetch_user_favorites(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT recipe_id FROM Favorite WHERE user_id = %s", (user_id,))
    favorite_recipes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return favorite_recipes

def toggle_favorite(user_id, recipe_id):
    conn = connect_db()
    cursor = conn.cursor()

    # First, check if the favorite already exists
    cursor.execute("SELECT * FROM Favorite WHERE user_id = %s AND recipe_id = %s", (user_id, recipe_id))
    favorite = cursor.fetchone()
    
    # Check if the recipe is already in favorites
    if favorite:
        # Remove from favorites
        cursor.execute("DELETE FROM Favorite WHERE user_id = %s AND recipe_id = %s", (user_id, recipe_id))
        st.success("Recipe removed from favorites!")
    else:
        # Add to favorites
        cursor.execute("INSERT INTO Favorite (user_id, recipe_id) VALUES (%s, %s)", (user_id, recipe_id))
        st.success("Recipe added to favorites!")

    conn.commit()
    cursor.close()
    conn.close()
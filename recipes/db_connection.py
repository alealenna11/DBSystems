from pymongo import MongoClient

def connect_db():
    """Connect to MongoDB and return database and collections."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['inf2003_db']  # Your database name

    # Collections
    recipes_collection = db['recipes']
    users_collection = db['users']
    recipe_info_collection = db['recipe_info']
    recipe_ratings_collection = db['recipe_ratings']
    cuisines_collection = db['cuisines']
    dietary_collection = db['dietary']

    return db, recipes_collection, users_collection, recipe_info_collection, recipe_ratings_collection, cuisines_collection, dietary_collection

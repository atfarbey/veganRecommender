# Recipe Recommender: Streamlit App for Vegan Recipes

import streamlit as st
import json
from difflib import get_close_matches

# Load pre-saved recipe data (should be replaced with actual data or scraping logic)
@st.cache_data
def load_recipes():
    with open('vegan_recipes.json', 'r') as file:
        return json.load(file)

recipes = load_recipes()

# Title
st.title("Vegan Recipe Recommender 🍽️")

# User input
user_input = st.text_input("Enter the ingredients you have at home (comma-separated):")

# Function to check ingredient overlap
def match_ingredients(user_ingredients, recipe_ingredients):
    matches = 0
    for item in user_ingredients:
        item = item.strip().lower()
        if any(item in ingr.lower() for ingr in recipe_ingredients):
            matches += 1
    return matches

# Recommend button
if st.button("Recommend Recipes"):
    if not user_input:
        st.warning("Please enter some ingredients.")
    else:
        user_ingredients = user_input.split(',')
        scored_recipes = []

        for recipe in recipes:
            score = match_ingredients(user_ingredients, recipe.get("ingredients", []))
            if score > 0:
                scored_recipes.append((score, recipe))

        scored_recipes.sort(reverse=True, key=lambda x: x[0])

        if scored_recipes:
            st.subheader("Top Matching Recipes")
            for score, recipe in scored_recipes[:5]:
                st.markdown(f"**[{recipe['title']}]({recipe['url']})**")
                st.markdown(f"Matching Ingredients: {score}")
                st.markdown("---")
        else:
            st.info("No matching recipes found. Try different or more ingredients.")

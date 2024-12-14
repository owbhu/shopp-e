import streamlit as st
import pandas as pd
from io import StringIO
from openai import OpenAI
from dotenv import load_dotenv
import os


api_key = st.secrets["default"]["OPENAI_API_KEY"]


client = OpenAI(api_key=api_key)

# Predefined ingredient prices (mock data for budget tracking)
PRICE_DATA = """
ingredient,price
chicken,5.0
rice,1.0
broccoli,2.5
cheese,3.0
milk,2.0
bread,1.5
eggs,2.5
pasta,2.0
tomato,1.0
carrot,1.0
"""

# Convert price data to DataFrame
prices_df = pd.read_csv(StringIO(PRICE_DATA))

# Function to calculate the total cost of a shopping list
def calculate_costs(shopping_list):
    total_cost = 0
    for item in shopping_list:
        item_price = prices_df.loc[prices_df['ingredient'] == item, 'price']
        if not item_price.empty:
            total_cost += item_price.values[0]
        else:
            st.warning(f"Price for '{item}' not found, skipping...")
    return total_cost

# AI Function to generate a meal plan using the new OpenAI API
def generate_meal_plan(preferences, restrictions, ingredients, budget):
    prompt = f"""
    Create a 7-day meal plan for breakfast, lunch, and dinner. 
    Preferences: {preferences}
    Restrictions: {restrictions}
    Ingredients on hand: {ingredients}
    Stay within a budget of ${budget}. Include estimated costs for each meal and a shopping list.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates meal plans and budgets."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content  # Access Pydantic model attributes

# Streamlit UI
st.title("Shopp-E: Your AI Meal Planner & Budget Tracker 🛒")
st.image("https://upload.wikimedia.org/wikipedia/commons/a/a1/Wall-E.png", width=150)  # Placeholder image

# Collect user inputs
preferences = st.text_input("What kind of meals do you like?", "Italian, quick, healthy")
restrictions = st.text_input("Any dietary restrictions?", "No seafood")
ingredients = st.text_area("List ingredients you already have (comma-separated):", "chicken, rice, tomato")
budget = st.number_input("What's your weekly grocery budget?", min_value=0, value=50, step=1)

# Generate meal plan when button is clicked
if st.button("Plan My Week"):
    if preferences and restrictions and ingredients:
        with st.spinner("Shopp-E is cooking up your plan..."):
            try:
                meal_plan = generate_meal_plan(preferences, restrictions, ingredients, budget)
                st.success("Here's your meal plan!")
                st.text_area("Meal Plan", value=meal_plan, height=300)
                
                # Extract a simple shopping list (mock data for now)
                shopping_list = ["chicken", "rice", "broccoli", "cheese"]
                total_cost = calculate_costs(shopping_list)
                
                st.write("### Shopping List")
                for item in shopping_list:
                    st.write(f"- {item}")
                st.write(f"**Estimated Total Cost:** ${total_cost:.2f}")
                
                if total_cost > budget:
                    st.error("⚠️ This meal plan exceeds your budget!")
                else:
                    st.success("🎉 This meal plan is within your budget!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in all the fields before generating your meal plan!")

# Footer
st.write("---")
st.caption("Shopp-E: Designed by [Your Name]. AI-powered meal planning made fun!")

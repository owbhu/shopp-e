import streamlit as st
import pandas as pd
import json
from io import StringIO
from openai import OpenAI

# API Key from Streamlit Secrets
api_key = st.secrets["default"]["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Function to generate meal plan
def generate_meal_plan(preferences, restrictions, ingredients, budget):
    prompt = f"""
    Create a 7-day meal plan for breakfast, lunch, and dinner.
    Preferences: {preferences}
    Restrictions: {restrictions}
    Ingredients on hand: {ingredients}
    Stay within a budget of ${budget}.
    
    Provide the response in this JSON format:
    {{
        "meal_plan": "description of the 7-day meal plan",
        "shopping_list": ["list of ingredients"],
        "estimated_cost": "total estimated cost of all ingredients"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates structured meal plans and budgets."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return json.loads(response.choices[0].message.content)

# Streamlit UI
st.title("Shopp-E: Your AI Meal Planner & Budget Tracker 🛒")
st.image("https://via.placeholder.com/300x150.png?text=Shopp-E", use_column_width=True)

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
                output = generate_meal_plan(preferences, restrictions, ingredients, budget)
                meal_plan = output.get("meal_plan", "No meal plan found.")
                shopping_list = output.get("shopping_list", [])
                estimated_cost = float(output.get("estimated_cost", "0"))

                # Display meal plan
                st.success("Here's your meal plan!")
                st.text_area("Meal Plan", value=meal_plan, height=300)

                # Display shopping list
                st.write("### Shopping List")
                for item in shopping_list:
                    st.write(f"- {item}")
                st.write(f"**Estimated Total Cost:** ${estimated_cost:.2f}")

                # Budget analysis
                remaining_budget = budget - estimated_cost
                if remaining_budget < 0:
                    st.error(f"⚠️ You're ${-remaining_budget:.2f} over budget!")
                else:
                    st.success(f"🎉 You have ${remaining_budget:.2f} left in your budget!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in all the fields before generating your meal plan!")

# Footer
st.write("---")
st.caption("Shopp-E: Designed by Owen Hughes. AI-powered meal planning")

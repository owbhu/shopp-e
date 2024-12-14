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
        "day_1": {{
            "breakfast": "description",
            "lunch": "description",
            "dinner": "description"
        }},
        "day_2": {{
            "breakfast": "description",
            "lunch": "description",
            "dinner": "description"
        }},
        ...
        "day_7": {{
            "breakfast": "description",
            "lunch": "description",
            "dinner": "description"
        }}
    }}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 Turbo
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates structured meal plans and budgets."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return json.loads(response.choices[0].message.content)

# Streamlit UI
st.title("Shopp-E: Your AI Meal Planner & Budget Tracker 🛒")
st.image("https://via.placeholder.com/300x150.png?text=Shopp-E", use_container_width=True)

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
                estimated_cost = output.get("estimated_cost", "0")
                estimated_cost = float(estimated_cost.replace("$", "").strip())  # Clean and convert to float

                # Display meal plan
                st.success("Here's your meal plan!")
                st.write("### 7-Day Meal Plan")
                for day, meals in output.items():
                    st.write(f"**{day.capitalize()}**")
                    st.write(f"- 🥞 **Breakfast**: {meals['breakfast']}")
                    st.write(f"- 🍴 **Lunch**: {meals['lunch']}")
                    st.write(f"- 🍽️ **Dinner**: {meals['dinner']}")
                    st.write("---")

                # Display shopping list
                shopping_list = output.get("shopping_list", [])
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

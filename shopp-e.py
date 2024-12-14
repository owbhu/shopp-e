import streamlit as st
import pandas as pd
import json
from io import StringIO
from openai import OpenAI

# API Key from Streamlit Secrets
api_key = st.secrets["default"]["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Predefined ingredient prices (mock data)
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
spinach,2.0
avocado,2.5
tofu,3.0
quinoa,4.0
beef,6.0
salmon,7.0
"""
prices_df = pd.read_csv(StringIO(PRICE_DATA))

# Function to calculate costs for new ingredients
def calculate_costs(shopping_list, prices_df):
    total_cost = 0
    for item in shopping_list:
        item_price = prices_df.loc[prices_df['ingredient'].str.lower() == item.lower(), 'price']
        if not item_price.empty:
            total_cost += item_price.values[0]
        else:
            st.warning(f"Price for '{item}' not found. Skipping...")
    return total_cost

# Function to clean and extract numeric cost
def parse_cost(cost_string):
    import re
    # Extract numbers and decimal points from the string
    cleaned_cost = re.sub(r"[^\d.]", "", cost_string)
    return float(cleaned_cost) if cleaned_cost else 0.0

# AI Function to generate meal plan
def generate_meal_plan(preferences, restrictions, ingredients, budget):
    prompt = f"""
    Create a 7-day meal plan for breakfast, lunch, and dinner.
    - Base meals on preferences: {preferences}.
    - Avoid the following restrictions: {restrictions}.
    - You can include the ingredients on hand: {ingredients}.
    - Feel free to suggest new complementary ingredients to make creative and interesting meals.
    - Make sure the meals are well-structured and the recipe's are thorough
    - For each meal, provide a recipe with detailed instructions.
    - Provide the response in this structured JSON format:
    {{
        "meal_plan": {{
            "day_1": {{
                "breakfast": {{
                    "name": "name of the dish",
                    "recipe": "recipe instructions"
                }},
                "lunch": {{
                    "name": "name of the dish",
                    "recipe": "recipe instructions"
                }},
                "dinner": {{
                    "name": "name of the dish",
                    "recipe": "recipe instructions"
                }}
            }},
            ...
            "day_7": {{
                "breakfast": {{
                    "name": "name of the dish",
                    "recipe": "recipe instructions"
                }},
                "lunch": {{
                    "name": "name of the dish",
                    "recipe": "recipe instructions"
                }},
                "dinner": {{
                    "name": "name of the dish",
                    "recipe": "recipe instructions"
                }}
            }}
        }},
        "shopping_list": ["new ingredients required for the meal plan"],
        "total_estimated_cost": "estimated total cost for new ingredients"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant and chef that generates structured meal plans and budgets."},
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
    if preferences and restrictions:
        with st.spinner("Shopp-E is cooking up your plan..."):
            try:
                # Generate meal plan and parse JSON response
                output = generate_meal_plan(preferences, restrictions, ingredients, budget)
                meal_plan = output.get("meal_plan", {})
                shopping_list = output.get("shopping_list", [])
                estimated_cost = output.get("total_estimated_cost", "0")
                estimated_cost = parse_cost(estimated_cost)  # Clean and convert to float

                # Display meal plan day by day
                st.success("Here's your 7-day meal plan!")
                for day, meals in meal_plan.items():
                    st.write(f"**{day.capitalize()}**")
                    for meal_type, details in meals.items():
                        with st.expander(f"🍴 {meal_type.capitalize()}: {details['name']}"):
                            st.write(details['recipe'])
                    st.write("---")

                # Calculate costs for new ingredients only
                total_cost = calculate_costs(shopping_list, prices_df)

                # Display shopping list
                st.write("### Shopping List (New Ingredients)")
                for item in shopping_list:
                    st.write(f"- {item}")
                st.write(f"**Total Estimated Cost for New Ingredients:** ${total_cost:.2f}")

                # Budget analysis
                remaining_budget = budget - total_cost
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

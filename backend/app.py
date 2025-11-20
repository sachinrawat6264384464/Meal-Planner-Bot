# app.py
from flask import Flask, request, jsonify
from google import genai
import os

app = Flask(__name__)

# MealPlannerBot Class (Purana code, bas __init__ mein thoda change)
class MealPlannerBot:
    def __init__(self):
        try:
            # Check for API Key or throw error
            if 'GEMINI_API_KEY' not in os.environ:
                 raise ValueError("GEMINI_API_KEY environment variable not set.")
                 
            self.client = genai.Client()
            self.model = "gemini-2.5-flash"
        except Exception as e:
            # Production mein yahan error log karna behtar hota hai
            print(f"Error initializing client: {e}")
            self.client = None

    # Feature 1: Ingredients se Recipe
    def find_recipe_by_ingredients(self, ingredients):
        if not self.client: return "API error."
        prompt = (
            f"Mujhe in ingredients (samagri) ka istemaal karke ek acchi recipe chahie: {ingredients}. "
            f"Recipe ka naam, zaruri samagri, banane ki vidhi (steps) aur samay (time) Hindi mein vistrit roop se batao."
        )
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text

    # Feature 2: Weekly Meal Plan
    def create_weekly_plan(self, constraints):
        if not self.client: return "API error."
        prompt = (
            f"Mujhe 7 dino ka meal plan chahie. Niyam: {constraints}. "
            f"Ek table ya saaf list ke roop mein, har din ka plan Hindi mein batao. Dishes repeat nahi honi chahiye."
        )
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text
    
    # Feature 3: Recipe Conversion (Vegetarian/Vegan)
    def convert_recipe(self, original_recipe_name, conversion_type):
        if not self.client: return "API error."
        prompt = (
            f" '{original_recipe_name}' recipe ko puri tarah se **{conversion_type}** version mein badal do. "
            f"Badle hue ingredients aur naye steps ke saath puri recipe Hindi mein do."
        )
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text

# Bot instance globally initialize karein
bot = MealPlannerBot()

# --- Flask Routes ---

@app.route('/api/get_recipe', methods=['POST'])
def get_recipe_api():
    data = request.json
    ingredients = data.get('ingredients', '')
    if not ingredients:
        return jsonify({'error': 'Ingredients missing'}), 400
    
    result = bot.find_recipe_by_ingredients(ingredients)
    return jsonify({'result': result})

@app.route('/api/get_plan', methods=['POST'])
def get_plan_api():
    data = request.json
    constraints = data.get('constraints', '')
    if not constraints:
        return jsonify({'error': 'Constraints missing'}), 400
    
    result = bot.create_weekly_plan(constraints)
    return jsonify({'result': result})

# Aap ismein baaki routes bhi isi tarah add kar sakte hain (e.g., /api/convert_recipe)

if __name__ == '__main__':
    # Yeh app default port 5000 par chalega
    app.run(debug=True)
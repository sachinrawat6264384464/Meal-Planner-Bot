# app.py
from flask import Flask, request, jsonify
from google import genai
from flask import render_template
app = Flask(__name__)

class MealPlannerBot:
    def __init__(self):
        try:
            # Direct API key (bina .env ke)
            api_key = "AIzaSyBMjxBfPOhCixZQhRas17BmlIZQ2dUqNNQ"  # <-- Replace with your Gemini API key
            
            if not api_key:
                raise ValueError("API key not set.")
            
            # Pass API key to client
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.5-flash"

        except Exception as e:
            print(f"Error initializing client: {e}")
            self.client = None

    def find_recipe_by_ingredients(self, ingredients):
        if not self.client:
            return "API error."
        
        prompt = (
            f"Mujhe in ingredients (samagri) ka istemaal karke ek acchi recipe chahie: {ingredients}. "
            f"Recipe ka naam, zaruri samagri, banane ki vidhi (steps) aur samay (time) Hindi mein vistrit roop se batao."
        )
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text

    def create_weekly_plan(self, constraints):
        if not self.client:
            return "API error."
        
        prompt = (
            f"Mujhe 7 dino ka meal plan chahie. Niyam: {constraints}. "
            f"Ek table ya list ke roop mein, har din ka plan Hindi mein batao. Dishes repeat nahi honi chahiye."
        )
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text

    def convert_recipe(self, original_recipe_name, conversion_type):
        if not self.client:
            return "API error."
        
        prompt = (
            f"'{original_recipe_name}' recipe ko puri tarah se {conversion_type} version mein badal do. "
            f"Badle hue ingredients aur naye steps ke saath puri recipe Hindi mein do."
        )
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text

# Global bot instance
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

# Optional: simple GET route to test server

    


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

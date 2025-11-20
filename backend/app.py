# app.py
from flask import Flask, request, jsonify, render_template
from google import genai
# --- NAYE IMPORTS ---
from PIL import Image # Image processing ke liye
import io # Image data ko handle karne ke liye
# --------------------

app = Flask(__name__)

# NOTE: Replace with your actual Gemini API Key
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=PORT)
 

class MealPlannerBot:
    def __init__(self):
        try:
            if not GEMINI_API_KEY :
                raise ValueError("API key not set.")
            
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model = "gemini-2.5-flash" # Default model for text generation
            print("MealPlannerBot initialized successfully.")
        except Exception as e:
            print(f"Error initializing client: {e}")
            self.client = None

    # --- Feature 1: Find Recipe by Ingredients (English Prompt) ---
    def find_recipe_by_ingredients(self, ingredients, language):
        if not self.client:
            return "API error: Client not initialized."
        
        prompt = (
            f"Generate a detailed recipe using the following ingredients: {ingredients}. "
            f"Provide the recipe name, required ingredients, step-by-step instructions, and total cooking time. "
            f"The entire output must be in **{language}**."
        )
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text

    # --- Feature 2: Create Weekly Plan (English Prompt) ---
    def create_weekly_plan(self, constraints, language):
        if not self.client:
            return "API error: Client not initialized."
        
        prompt = (
            f"Generate a 7-day meal plan (Breakfast, Lunch, Dinner). Follow these constraints: {constraints}. "
            f"The plan should be in the form of a table or list. Ensure no dishes are repeated during the week. "
            f"The entire plan must be provided in **{language}**."
        )
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text

    # --- Feature 3: Recipe Conversion (English Prompt) ---
    def convert_recipe(self, original_recipe_name, conversion_type, language):
        if not self.client:
            return "API error: Client not initialized."
        
        prompt = (
            f"Completely convert the recipe for '{original_recipe_name}' into a **{conversion_type}** version. "
            f"Provide the full modified recipe including substitute ingredients (e.g., replace meat with tofu/lentils) and new cooking steps. "
            f"The entire modified recipe must be in **{language}**."
        )
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text
    
    # --- Feature 4: Analyze Image for Ingredients (VISION FEATURE) ---
    def analyze_image_for_ingredients(self, image_data):
        if not self.client:
            return "API error: Client not initialized."
        
        try:
            # Image data (bytes) ko PIL Image object mein load karein
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            # Agar image load nahi ho payi to error
            return f"Error processing image file: {e}"

        prompt = (
            "Analyze the objects in this image. List all recognizable raw food ingredients, "
            "vegetables, and raw meats (if present). Provide only a comma-separated list of ingredients, without any introductory text."
        )
        
        # Gemini Vision Model ko prompt aur image dono bhejein
        response = self.client.models.generate_content(
            model='gemini-2.5-flash', # Vision ke liye sahi model
            contents=[prompt, image] 
        )
        
        # Ingredients ki list return karein
        return response.text.strip()
    
    # --- Feature 5: Recipe/Plan based on Vision Output ---
    def generate_plan_from_vision(self, ingredients, language):
        if not self.client:
            return "API error: Client not initialized."
            
        prompt = (
            f"Generate 3-4 quick and simple meal ideas using ONLY the following ingredients: {ingredients}. "
            f"Provide the recipe names and basic steps in **{language}**. Focus on using the listed ingredients."
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text


# Global bot instance
bot = MealPlannerBot()

# --- Flask Routes ---

@app.route('/')
def about():
    return render_template('index.html')


@app.route('/about/')
def home():
    return render_template('about.html')

@app.route('/api/get_recipe', methods=['POST'])
def get_recipe_api():
    data = request.json
    ingredients = data.get('ingredients', '')
    language = data.get('language', 'English') # Default English kar diya
    if not ingredients:
        return jsonify({'error': 'Ingredients missing'}), 400
    
    result = bot.find_recipe_by_ingredients(ingredients, language) 
    return jsonify({'result': result})

@app.route('/api/get_plan', methods=['POST'])
def get_plan_api():
    data = request.json
    constraints = data.get('constraints', '')
    language = data.get('language', 'English') # Default English kar diya
    if not constraints:
        return jsonify({'error': 'Constraints missing'}), 400
        
    result = bot.create_weekly_plan(constraints, language)
    return jsonify({'result': result})

@app.route('/api/convert_recipe', methods=['POST'])
def convert_recipe_api():
    data = request.json
    original_recipe = data.get('original_recipe', '')
    conversion_type = data.get('conversion_type', 'vegetarian')
    language = data.get('language', 'English') # Default English kar diya
    
    if not original_recipe:
        return jsonify({'error': 'Original recipe name missing'}), 400
    
    result = bot.convert_recipe(original_recipe, conversion_type, language)
    return jsonify({'result': result})

# --- NAYA VISION ROUTE ---
@app.route('/api/vision_recipe', methods=['POST'])
def vision_recipe_api():
    # File aur language dono check karein
    if 'image' not in request.files or 'language' not in request.form:
        return jsonify({'error': 'Image file or language missing'}), 400

    image_file = request.files['image']
    language = request.form.get('language', 'English') # Language form data se aayega

    try:
        image_data = image_file.read()
        
        # 1. Image se ingredients extract karein
        ingredients_list = bot.analyze_image_for_ingredients(image_data)
        
        if "Error" in ingredients_list:
             return jsonify({'error': f'Image analysis failed. Please try a clearer image.'}), 500

        # 2. Un ingredients se recipe generate karein
        plan_result = bot.generate_plan_from_vision(ingredients_list, language)

        return jsonify({
            'ingredients_found': ingredients_list,
            'result': plan_result
        })

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred during processing: {str(e)}'}), 500
# -------------------------

if __name__ == '__main__':
    app.run(debug=True)
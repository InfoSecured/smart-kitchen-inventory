import requests

API_KEY = "your_spoonacular_api_key"

def get_recipe_suggestions(inventory):
    ingredients = ",".join([item['name'] for item in inventory])
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=5&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 
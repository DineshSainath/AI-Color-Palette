import openai
import json
from flask import Flask, render_template, request
from dotenv import dotenv_values

# Load API key from .env file
dot_env = dotenv_values(".env")
openai.api_key = dot_env["OPENAI_API_KEY"]

app = Flask(__name__, template_folder='templates')

def getPalette(msg):
    response = openai.chat.completions.create(
    model="gpt-4o-mini", 
    messages=[
        {"role": "system", "content": "You are a color palette generating assistant. You should generate color palettes that fir the theme, mood or instructions in the prompt. The palettes shold be between 3 and 5 colors."},
        {"role": "user", "content": f""" Input:{msg}. The output should be in a json array format. Dont say its json, just give the array in a single line."""}
    ],
    max_tokens = 100
)

    colors = json.loads(response.choices[0].message.content)
    return colors

@app.route("/palette", methods=['POST'])
def promptForPalette():
    app.logger.info("HIT THE POST REQUEST ROUTE!")
    query = request.form.get("query")
    colors = getPalette(query)  # Generate color palette
    app.logger.info(f"Generated colors: {colors}")
    
    # Returning colors as a plain string
    return {"colors": colors}

   

@app.route("/")
def index():
    try:
        
        return render_template("index.html")
    
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error with the OpenAI API request."

if __name__ == "__main__":
    app.run(debug=True)

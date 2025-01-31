import openai
from flask import Flask, render_template, request
from dotenv import dotenv_values

# Load API key from .env file
dot_env = dotenv_values(".env")
openai.api_key = dot_env["OPENAI_API_KEY"]

app = Flask(__name__, template_folder='templates')

@app.route("/palette", methods=['POST'])
def promptForPalette():
    return render_template('palette.html')

@app.route("/")
def index():
    try:
        # Send request to OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Define rag?"}
            ]
        )
    

        # Access the content correctly
        message_content = response.choices[0].message.content
        
        return message_content
    
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error with the OpenAI API request."

if __name__ == "__main__":
    app.run(debug=True)

import logging
from flask import Flask, render_template, request, jsonify
from langchain_ollama import OllamaLLM

# Set up logging
logging.basicConfig(level=logging.INFO)  # You can change the level to DEBUG if you want more detailed logs
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Ollama model once globally
ollama = OllamaLLM(model='gemma2:2b')

# Log model initialization (instead of print)
logger.info("Ollama model initialized successfully")

# Helper function to get response from Ollama API
context = ""

def get_response(query):
    global context  # Use global to modify the context variable
    try:
        # Get the result from the model
        result = ollama.invoke({"context": context, "question": query})
        context += f"User: {query} \n"
        context += f"Ai: {result} \n"
        logger.info(f"Received response: {result}")
        return result
    except Exception as e:
        # Log the error
        logger.error(f"Error while getting response: {e}")
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response_api():
    user_input = request.form.get('query')
    logger.info(f"User input: {user_input}")
    response = get_response(user_input)
    return jsonify({'response': response, 'history': context})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)

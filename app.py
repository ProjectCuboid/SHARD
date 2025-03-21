from flask import Flask, render_template, request, jsonify
from langchain_ollama import Ollama

app = Flask(__name__)

# Initialize Ollama
ollama = Ollama()
history = []

# Helper function to get response from Ollama API
def get_response(query):
    try:
        # Make the request to the Ollama API
        response = ollama.chat(
            model="gemma2:2b",
            messages=[{"role": "user", "content": query}],
        )
        # Update conversation history
        history.append(f"USER: {query}")
        history.append(f"AI: {response['content']}")
        return response['content']
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response_api():
    user_input = request.form.get('query')
    response = get_response(user_input)
    return jsonify({'response': response, 'history': '\n'.join(history)})

if __name__ == '__main__':
    app.run(debug=True)

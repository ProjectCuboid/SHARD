from flask import Flask, render_template, request, jsonify
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate  # Import the required prompt template class

app = Flask(__name__)

# Initialize Ollama
ollama = OllamaLLM(model='codellama')

# Adjusted template and prompt
t = """
Here is the conversation history: {context}

Prompt: {question}

You are a funny chatbot.
"""
prompt = ChatPromptTemplate.from_template(t)

# Create a chain from the prompt and Ollama
chain = prompt | ollama

# Helper function to get response from Ollama API
context = ""

def get_response(query):
    global context  # Use global so you can modify the context variable
    try:
        result = chain.invoke({"context": context, "question": query})
        context += f"User: {query} \n"
        context += f"Ai: {result} \n"
        return result
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response_api():
    user_input = request.form.get('query')
    response = get_response(user_input)
    return jsonify({'response': response, 'history': context})

if __name__ == '__main__':
    app.run(debug=True)

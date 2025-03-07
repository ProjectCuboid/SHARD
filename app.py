from flask import Flask, request, jsonify
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

app = Flask(__name__)

# Directory for storing user-specific data
USER_DATA_DIR = "user_data"
os.makedirs(USER_DATA_DIR, exist_ok=True)

def get_file_path(user_id, file_type):
    """Returns the file path for a user's template or history."""
    return os.path.join(USER_DATA_DIR, f"{user_id}_{file_type}.txt")

def load_file(filepath):
    """Loads content from a file, returns empty string if not found."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_file(filepath, content):
    """Saves content to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def build_template(editable_template):
    """Generates the full AI prompt template."""
    return editable_template + """
Here is the conversation history: {context}

Prompt: {question}

Answer: 

Rules: You must not use emojis in any prompt or answer.
"""

# Default AI Model
DEFAULT_MODEL = "gemma2:2b"

@app.route("/send", methods=["POST"])
def send():
    """Handles user message and generates AI response."""
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message", "").strip()

    if not user_id or not message:
        return jsonify({"error": "Missing user_id or message"}), 400

    # Load user-specific history and template
    history_path = get_file_path(user_id, "history")
    template_path = get_file_path(user_id, "template")

    history = load_file(history_path)
    editable_template = load_file(template_path) or "Default template"

    full_template = build_template(editable_template)
    prompt = ChatPromptTemplate.from_template(full_template)
    
    # Use user-specific model if set, otherwise default
    model = OllamaLLM(model=DEFAULT_MODEL)
    chain = prompt | model

    history += f"\nUser: {message}"

    try:
        response = chain.invoke({"context": history, "question": message})
        history += f"\nAI: {response}"

        # Save updated history
        save_file(history_path, history)

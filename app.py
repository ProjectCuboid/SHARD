from flask import Flask, request, jsonify
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

app = Flask(__name__)

# File paths
TEMPLATE_PATH = "template.txt"
HISTORY_PATH = "history.txt"

# Load & save functions
def load_file(filepath):
    """Load file content."""
    return open(filepath, 'r', encoding="utf-8").read() if os.path.exists(filepath) else ""

def save_file(filepath, content):
    """Save content to a file."""
    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(content)

# Initialize defaults
template = load_file(TEMPLATE_PATH)
history = load_file(HISTORY_PATH)
editable_template = template

def build_template():
    return editable_template + """
Here is the conversation history: {context}

Prompt: {question}

Answer: 

Rules: You must not use emojis in any prompt or answer.
"""

# Load model
current_model = "gemma2:2b"
model = OllamaLLM(model=current_model)
template = build_template()
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# === AI CHAT === #
@app.route("/chat", methods=["POST"])
def chat():
    """Talk to the AI."""
    global history, chain

    data = request.json
    messages = data.get("messages", [])

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Invalid request. Send messages as a list."}), 400

    last_message = messages[-1].get("content", "").strip()
    if not last_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    history += f"\nUser: {last_message}"

    try:
        response = chain.invoke({"context": history, "question": last_message})
        history += f"\nAI: {response}"
        save_file(HISTORY_PATH, history)

        return jsonify({
            "response": response,
            "usage": {
                "prompt_tokens": len(last_message.split()),
                "completion_tokens": len(response.split())
            }
        })
    except Exception as e:
        return jsonify({"error": f"AI error: {str(e)}"}), 500

# === MODELS === #
@app.route("/models", methods=["GET"])
def get_models():
    """See available models."""
    return jsonify({"current_model": current_model})

@app.route("/models", methods=["POST"])
def set_model():
    """Change AI model."""
    global current_model, model, chain

    data = request.json
    new_model = data.get("model", "").strip()

    if not new_model:
        return jsonify({"error": "Please provide a model name."}), 400

    current_model = new_model
    model = OllamaLLM(model=current_model)
    chain = prompt | model

    return jsonify({"message": f"Model changed to {current_model}."})

# === TEMPLATE === #
@app.route("/template", methods=["GET"])
def get_template():
    """View AI prompt template."""
    return jsonify({"template": editable_template})

@app.route("/template", methods=["POST"])
def set_template():
    """Update AI template."""
    global editable_template, template, prompt, chain

    data = request.json
    new_template = data.get("template", "").strip()

    if not new_template:
        return jsonify({"error": "Template cannot be empty."}), 400

    editable_template = new_template
    template = build_template()
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    save_file(TEMPLATE_PATH, editable_template)

    return jsonify({"message": "Template updated successfully."})

# === CHAT HISTORY === #
@app.route("/history", methods=["GET"])
def get_history():
    """Get chat history."""
    return jsonify({"history": history.split("\n")})

@app.route("/history", methods=["POST"])
def add_history():
    """Add a message to chat history."""
    global history
    data = request.json
    new_entry = data.get("entry", "").strip()

    if not new_entry:
        return jsonify({"error": "Entry cannot be empty."}), 400

    history += f"\n{new_entry}"
    save_file(HISTORY_PATH, history)

    return jsonify({"message": "History updated."})

@app.route("/history", methods=["DELETE"])
def delete_history():
    """Clear chat history."""
    global history
    history = ""
    save_file(HISTORY_PATH, "")

    return jsonify({"message": "Chat history cleared."})

# === RUN SERVER === #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)from flask import Flask, request, jsonify
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

app = Flask(__name__)

# File paths
TEMPLATE_PATH = "template.txt"
HISTORY_PATH = "history.txt"

# Load & save functions
def load_file(filepath):
    """Load file content."""
    return open(filepath, 'r', encoding="utf-8").read() if os.path.exists(filepath) else ""

def save_file(filepath, content):
    """Save content to a file."""
    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(content)

# Initialize defaults
template = load_file(TEMPLATE_PATH)
history = load_file(HISTORY_PATH)
editable_template = template

def build_template():
    return editable_template + """
Here is the conversation history: {context}

Prompt: {question}

Answer: 

Rules: You must not use emojis in any prompt or answer.
"""

# Load model
current_model = "gemma2:2b"
model = OllamaLLM(model=current_model)
template = build_template()
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# === AI CHAT === #
@app.route("/chat", methods=["POST"])
def chat():
    """Talk to the AI."""
    global history, chain

    data = request.json
    messages = data.get("messages", [])

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Invalid request. Send messages as a list."}), 400

    last_message = messages[-1].get("content", "").strip()
    if not last_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    history += f"\nUser: {last_message}"

    try:
        response = chain.invoke({"context": history, "question": last_message})
        history += f"\nAI: {response}"
        save_file(HISTORY_PATH, history)

        return jsonify({
            "response": response,
            "usage": {
                "prompt_tokens": len(last_message.split()),
                "completion_tokens": len(response.split())
            }
        })
    except Exception as e:
        return jsonify({"error": f"AI error: {str(e)}"}), 500

# === MODELS === #
@app.route("/models", methods=["GET"])
def get_models():
    """See available models."""
    return jsonify({"current_model": current_model})

@app.route("/models", methods=["POST"])
def set_model():
    """Change AI model."""
    global current_model, model, chain

    data = request.json
    new_model = data.get("model", "").strip()

    if not new_model:
        return jsonify({"error": "Please provide a model name."}), 400

    current_model = new_model
    model = OllamaLLM(model=current_model)
    chain = prompt | model

    return jsonify({"message": f"Model changed to {current_model}."})

# === TEMPLATE === #
@app.route("/template", methods=["GET"])
def get_template():
    """View AI prompt template."""
    return jsonify({"template": editable_template})

@app.route("/template", methods=["POST"])
def set_template():
    """Update AI template."""
    global editable_template, template, prompt, chain

    data = request.json
    new_template = data.get("template", "").strip()

    if not new_template:
        return jsonify({"error": "Template cannot be empty."}), 400

    editable_template = new_template
    template = build_template()
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    save_file(TEMPLATE_PATH, editable_template)

    return jsonify({"message": "Template updated successfully."})

# === CHAT HISTORY === #
@app.route("/history", methods=["GET"])
def get_history():
    """Get chat history."""
    return jsonify({"history": history.split("\n")})

@app.route("/history", methods=["POST"])
def add_history():
    """Add a message to chat history."""
    global history
    data = request.json
    new_entry = data.get("entry", "").strip()

    if not new_entry:
        return jsonify({"error": "Entry cannot be empty."}), 400

    history += f"\n{new_entry}"
    save_file(HISTORY_PATH, history)

    return jsonify({"message": "History updated."})

@app.route("/history", methods=["DELETE"])
def delete_history():
    """Clear chat history."""
    global history
    history = ""
    save_file(HISTORY_PATH, "")

    return jsonify({"message": "Chat history cleared."})

# === RUN SERVER === #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

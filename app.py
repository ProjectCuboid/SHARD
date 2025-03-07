from flask import Flask, request, jsonify, send_from_directory, render_template_string
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

app = Flask(__name__)

# Directory for user-specific data
USER_DATA_DIR = "user_data"
os.makedirs(USER_DATA_DIR, exist_ok=True)  # Create folder if it doesn't exist

def get_file_path(user_id, file_type):
    """Returns file path for a user's template or history."""
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

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ui", methods=["GET"])
def chat_ui():
    """Serve a simple chat UI."""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat with AI</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            #chat-box { width: 80%; height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin: auto; }
            input, button { padding: 10px; margin: 5px; }
        </style>
    </head>
    <body>
        <h2>Chat with AI</h2>
        <label>User ID:</label>
        <input type="text" id="user_id" placeholder="Enter your ID">
        <div id="chat-box"></div>
        <input type="text" id="user-input" placeholder="Type a message..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>

        <script>
            function handleKeyPress(event) {
                if (event.key === "Enter") sendMessage();
            }

            async function sendMessage() {
                const userInput = document.getElementById("user-input").value.trim();
                const userId = document.getElementById("user_id").value.trim();
                if (!userInput || !userId) return alert("User ID and message cannot be empty.");

                const chatBox = document.getElementById("chat-box");
                chatBox.innerHTML += `<p><b>You:</b> ${userInput}</p>`;
                document.getElementById("user-input").value = "";

                try {
                    const response = await fetch("/send", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ user_id: userId, message: userInput })
                    });

                    const data = await response.json();
                    if (data.response) {
                        chatBox.innerHTML += `<p><b>AI:</b> ${data.response}</p>`;
                    } else {
                        chatBox.innerHTML += `<p><b>Error:</b> ${data.error}</p>`;
                    }

                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch (error) {
                    chatBox.innerHTML += `<p><b>Error:</b> Unable to connect to server.</p>`;
                }
            }
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

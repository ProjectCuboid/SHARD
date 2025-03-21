from flask import Flask, render_template, request, jsonify
import subprocess
import shlex
import platform

app = Flask(__name__)

# Detect OS
OS_TYPE = platform.system()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/execute", methods=["POST"])
def execute():
    command = request.form.get("command")

    # Prevent dangerous commands (improve as needed)
    blocked_commands = ["rm", "del", "shutdown", "reboot", "poweroff", "format", "mkfs"]
    if any(cmd in command for cmd in blocked_commands):
        return jsonify({"output": "Blocked command for security reasons."})

    try:
        # Use PowerShell on Windows, Shell on Linux/macOS
        if OS_TYPE == "Windows":
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(shlex.split(command), capture_output=True, text=True)

        return jsonify({"output": result.stdout or result.stderr})
    
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)

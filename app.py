from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import re

app = Flask(__name__)
CORS(app)

def generate_mcqs_with_ollama(text):
    prompt = f"""
    Based on the following content, generate 3 multiple-choice questions (MCQs).
    Each question should have 4 options and one correct answer.

    Content:
    {text}

    Return the output strictly in the following JSON format:
    [
        {{
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "answer": "..."
        }},
        ...
    ]
    """

    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral'],
            input=prompt.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = result.stdout.decode('utf-8', errors='replace')

        # Find JSON structure in the output using regex
        json_match = re.search(r'\[\s*{.*?}\s*\]', output, re.DOTALL)
        if json_match:
            mcqs_json = json.loads(json_match.group())
            return mcqs_json
        else:
            return [{"error": "Could not parse MCQs from model output.", "raw_output": output}]
    except Exception as e:
        return [{"error": f"Exception occurred: {str(e)}"}]

@app.route('/generate-mcqs', methods=['POST'])
def generate_mcqs():
    data = request.get_json()
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No input text provided."}), 400

    mcqs = generate_mcqs_with_ollama(text)
    return jsonify({"mcqs": mcqs}), 200

@app.route('/highlight', methods=['POST'])
def highlight_pdf():
    data = request.get_json()
    text = data.get("text", "")
    print("Highlighting this text:", text)
    return jsonify({"status": "PDF created successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)

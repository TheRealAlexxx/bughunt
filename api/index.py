import json
from flask import Flask, jsonify

app = Flask(__name__, static_folder='../bughunt/static', static_url_path='/static')

# Load questions from JSON
with open('bughunt/questions.json', 'r') as f:
    QUESTIONS = json.load(f)

@app.route("/api/questions")
def get_questions():
    return jsonify(QUESTIONS)

from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Load questions from JSON
questions_path = os.path.join(os.path.dirname(__file__), '..', 'bughunt', 'questions.json')
with open(questions_path, 'r') as f:
    QUESTIONS = json.load(f)

@app.route("/api/questions")
def get_questions():
    return jsonify(QUESTIONS)

@app.route("/api")
def get_api():
    return jsonify(QUESTIONS)

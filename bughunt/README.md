# Bug Hunt

A lightweight Flask web app for a debugging quiz game. Players inspect buggy code snippets, choose the correct fix, earn points, and move through the full question set.

## Features

- Flask backend with in-memory question data
- Vanilla HTML, CSS, and JavaScript frontend
- Immediate correct and incorrect answer feedback
- Locked answers after selection
- Score, question progress, and progress bar
- Final score screen with restart button
- Responsive dark theme UI

## Project Structure

```text
bughunt/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── README.md
```

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:10000` in your browser.

## API

- `GET /` serves the game UI.
- `GET /api/questions` returns the quiz questions as JSON.

## Deploy

This app is ready for Render or Replit. Use `python app.py` as the start command. The Flask server binds to `0.0.0.0` on port `10000`.

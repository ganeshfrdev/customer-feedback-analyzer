from fastapi import FastAPI
import random
import sqlite3
from datetime import datetime
from transformers import pipeline

app = FastAPI()

# Fake feedback templates
FEEDBACK_TEMPLATES = [
    "Great job @{username}, love your product!",
    "@{username} needs to fix shipping, so slow!",
    "Amazing service from @{username} today!",
    "@{username}, your app crashed again...",
    "Thanks @{username} for the quick response!",
    "Terrible experience with @{username}, ugh.",
    "@{username} is the best in the game!",
    "Why is @{username} so expensive?",
]

# Setup sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Database setup
def init_db():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {"message": "Hello World from Customer Feedback Analyzer!"}

@app.get("/feedback/{username}")
def get_fake_feedback(username: str, count: int = 5):
    if count > 10:
        count = 10
    feedback = [random.choice(FEEDBACK_TEMPLATES).format(username=username) for _ in range(count)]
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for text in feedback:
        c.execute("INSERT INTO feedback (username, text, created_at) VALUES (?, ?, ?)", 
                 (username, text, current_time))
    conn.commit()
    conn.close()
    return {"username": username, "feedback": feedback}

@app.get("/stored-feedback/{username}")
def get_stored_feedback(username: str):
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("SELECT text, created_at FROM feedback WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return {"username": username, "feedback": [{"text": row[0], "created_at": row[1]} for row in rows]}

@app.get("/analyze/{username}")
def analyze_feedback(username: str):
    """
    Analyze stored feedback for sentiment.
    """
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("SELECT text FROM feedback WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return {"username": username, "analysis": "No feedback found"}

    # Analyze sentiment
    feedback_texts = [row[0] for row in rows]
    results = sentiment_analyzer(feedback_texts)
    
    # Summarize
    analysis = [
        {"text": text, "sentiment": result["label"], "confidence": result["score"]}
        for text, result in zip(feedback_texts, results)
    ]
    return {"username": username, "analysis": analysis}
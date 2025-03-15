from fastapi import FastAPI
import random
import sqlite3
from datetime import datetime

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

# Run once on startup
init_db()

@app.get("/")
def read_root():
    return {"message": "Hello World from Customer Feedback Analyzer!"}

@app.get("/feedback/{username}")
def get_fake_feedback(username: str, count: int = 5):
    """
    Generate and store fake feedback for a username.
    count: Number of feedback items (default 5, max 10).
    """
    if count > 10:
        count = 10
    # Generate feedback
    feedback = [
        random.choice(FEEDBACK_TEMPLATES).format(username=username)
        for _ in range(count)
    ]
    # Store in database
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for text in feedback:
        c.execute(
            "INSERT INTO feedback (username, text, created_at) VALUES (?, ?, ?)",
            (username, text, current_time)
        )
    conn.commit()
    conn.close()
    return {"username": username, "feedback": feedback}

@app.get("/stored-feedback/{username}")
def get_stored_feedback(username: str):
    """
    Retrieve all stored feedback for a username.
    """
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("SELECT text, created_at FROM feedback WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return {"username": username, "feedback": [{"text": row[0], "created_at": row[1]} for row in rows]}
from fastapi import FastAPI
import random

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

@app.get("/")
def read_root():
    return {"message": "Hello World from Customer Feedback Analyzer!"}

@app.get("/feedback/{username}")
def get_fake_feedback(username: str, count: int = 5):
    """
    Simulate feedback for a username.
    count: Number of feedback items (default 5, max 10).
    """
    if count > 10:
        count = 10  # Cap it for simplicity
    # Generate random feedback
    feedback = [
        random.choice(FEEDBACK_TEMPLATES).format(username=username)
        for _ in range(count)
    ]
    return {"username": username, "feedback": feedback}
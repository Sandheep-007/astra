# response_manager.py

import json
import os
import random

RESPONSES_FILE = os.path.join(os.path.dirname(__file__), "responses.json")

try:
    with open(RESPONSES_FILE, "r", encoding="utf-8") as file:
        responses = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    responses = {}

def respond(response_type):
    options = responses.get(response_type, [])
    if not options:
        return "I'm not sure how to respond to that."
    return random.choice(options)

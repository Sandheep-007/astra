import re
import requests
from response_manager import respond

def get_answer(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(url, timeout=5)
        data = response.json()

        # Try AbstractText first
        raw_text = data.get("AbstractText", "")
        if raw_text:
            return clean_text(raw_text)

        # Fallback to RelatedTopics if AbstractText is empty
        related = data.get("RelatedTopics", [])
        for topic in related:
            if isinstance(topic, dict) and "Text" in topic:
                return clean_text(topic["Text"])

        # No usable result found
        return None

    except requests.RequestException:
        return respond("internet_error")


def clean_text(text):
    # Remove brackets and their content
    text = re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}", "", text)

    # Keep only allowed characters
    text = re.sub(r"[^a-zA-Z0-9\s\.,?!]", "", text)

    # Remove extra whitespace
    return ' '.join(text.strip().split())

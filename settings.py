import os
import sys

# --- Resolve path for VOSK model safely for both .py and .exe ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return sys._MEIPASS
    else:
        # Running as a script
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
VOSK_MODEL_PATH = os.path.join(BASE_PATH, "vosk-model-small-en-us-0.15")

# --- Call phrases for VOSK to trigger Astra ---
CALL_PHRASES = [
    "astra", "hey astra",
    "ash tray", "asdra", "asra", "astraa",
    "castro", "ashra", "estera", "estra", "ashta"
]

# --- Verbs that indicate the user wants to open an app ---
OPEN_COMMAND_VERBS = [
    "open",
    "launch",
    "start",
    "run"
]

# --- Known web applications with their URLs (used if app is not installed locally) ---
KNOWN_WEB_APPS = {
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "reddit": "https://www.reddit.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "netflix": "https://www.netflix.com"
}

# --- Interrogative words to detect questions ---
QUESTION_WORDS = [
    "what", "who", "when", "where", "why", "how",
    "what's", "who's", "when's", "where's", "why's", "how's",
    "which", "which's"
]

# --- Google Speech Recognition timeout (in seconds) ---
GOOGLE_SR_TIMEOUT = 10

# --- Preferred gender for pyttsx3 TTS voice ---
PREFERRED_VOICE_GENDER = "female"

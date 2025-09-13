from settings import OPEN_COMMAND_VERBS, QUESTION_WORDS
from app_utils import open_app_or_web, search_google
from duckduckgo_api import get_answer
from response_manager import respond

import threading

# Internal state to track whether it's the first or second command
is_first_command = True

def handle_command(text, listener):
    global is_first_command

    words = text.lower().split()

    # Check for "open app" type command
    if any(verb in words for verb in OPEN_COMMAND_VERBS):
        print(f"[COMMAND] App launch: {text}")
        app_name = extract_app_name(words).strip()
        opened = open_app_or_web(app_name)

        if opened:
            listener.speak(respond("open_app"))
        else:
            listener.speak(respond("not_found"))

        is_first_command = False
        return True

    # Check for question
    elif any(qword in words for qword in QUESTION_WORDS):
        print(f"[COMMAND] Question: {text}")
        listener.google_sr_active = False  # Temporarily pause Google SR
        answer = get_answer(text)

        if answer:
            short_answer = _shorten_answer(answer)

            def speak_and_resume():
                listener.speak(short_answer)
                if not listener.stop_flag:
                    listener.google_sr_active = True
                    listener._reset_timer()

            threading.Thread(target=speak_and_resume).start()
        else:
            # Fallback: open web + speak fallback + reset timer
            search_google(text)
            listener.speak(respond("fallback"))
            if not listener.stop_flag:
                listener.google_sr_active = True
                listener._reset_timer()

        is_first_command = False
        return True

    # Unclear or unrecognized command
    else:
        print(f"[COMMAND] Unrecognized or unclear: {text}")
        if is_first_command:
            listener.speak(respond("unclear"))
            listener._reset_timer()
        is_first_command = False
        return False

def extract_app_name(words):
    # Extract everything after the first recognized trigger verb
    for i, word in enumerate(words):
        if word in OPEN_COMMAND_VERBS and i + 1 < len(words):
            return ' '.join(words[i + 1:])
    return ''

def _shorten_answer(answer):
    # Limit to first 2 sentences or max 200 characters
    short = '. '.join(answer.split('. ')[:2]).strip()
    if len(short) > 200:
        short = short[:197].rstrip() + "..."
    return short

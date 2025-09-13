import queue
import threading
import time
import json
import difflib
import sounddevice as sd
import vosk
import speech_recognition as sr
import pyttsx3

from settings import CALL_PHRASES, GOOGLE_SR_TIMEOUT, VOSK_MODEL_PATH
from response_manager import respond
from command_handler import handle_command

class Listener:
    def __init__(self):
        self.vosk_model = vosk.Model(VOSK_MODEL_PATH)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.speaking = False
        self.google_sr_active = False
        self.stop_flag = False
        self.timer_thread = None
        self.engine = pyttsx3.init()

        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        self.voice_lock = threading.Lock()
        self.q = queue.Queue()
        self.stream = None
        self.vosk_thread = None

    def run(self):
        self.start_listening()

    def speak(self, text):
        with self.voice_lock:
            if self.stop_flag:
                return
            self.speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.speaking = False

    def start_listening(self):
        self.stop_flag = False
        self.vosk_thread = threading.Thread(target=self._listen_for_call)
        self.vosk_thread.daemon = True
        self.vosk_thread.start()

    def stop_listening(self):
        self.stop_flag = True
        self.google_sr_active = False

        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.cancel()

        if self.stream:
            try:
                self.stream.close()
            except:
                pass

        print("🛑 Astra fully stopped.")

    def _listen_for_call(self):
        try:
            self.stream = sd.RawInputStream(
                samplerate=16000, blocksize=8000, dtype='int16',
                channels=1, callback=self._callback
            )
            self.stream.start()
        except Exception as e:
            print("⚠️ Error starting VOSK stream:", e)
            return

        rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
        print("\n🎙️ Listening for 'Astra' or similar phrases...\n")

        while not self.stop_flag:
            if not self.q.empty():
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").lower()
                    print(f"[VOSK HEARD]: {text}")

                    words = text.split()
                    triggered = any(
                        difflib.get_close_matches(word, CALL_PHRASES, n=1, cutoff=0.6)
                        for word in words
                    ) or bool(difflib.get_close_matches(text, CALL_PHRASES, n=1, cutoff=0.6))

                    if triggered:
                        print(f"✅ Triggered by: {text}")
                        if self.stream:
                            self.stream.stop()
                        self._trigger_google_sr()
                        break

        if self.stream:
            try:
                self.stream.close()
            except:
                pass

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(status, flush=True)
        self.q.put(bytes(indata))

    def _trigger_google_sr(self):
        if self.stop_flag:
            return

        self.google_sr_active = True
        self.speak(respond("greeting"))
        self._reset_timer()

        is_first_command = True

        while self.google_sr_active and not self.stop_flag:
            try:
                with self.microphone as source:
                    print("🎧 Listening for user command...")
                    audio = self.recognizer.listen(source, timeout=GOOGLE_SR_TIMEOUT)

                if self.stop_flag:
                    break

                user_input = self.recognizer.recognize_google(audio).lower()
                print(f"🗣️ User said: {user_input}")

                success = handle_command(user_input, self)

                if success:
                    self._reset_timer()
                    is_first_command = False
                else:
                    if is_first_command:
                        self.speak(respond("unclear"))
                        self._reset_timer()
                    else:
                        if not self.timer_thread or not self.timer_thread.is_alive():
                            self._start_timer()

            except sr.WaitTimeoutError:
                print("⏳ No command received, switching back to VOSK.")
                self._switch_to_vosk()

            except sr.UnknownValueError:
                print("❌ Could not understand audio.")
                if is_first_command:
                    self.speak(respond("unclear"))
                    self._reset_timer()
                else:
                    if not self.timer_thread or not self.timer_thread.is_alive():
                        self._start_timer()

    def _reset_timer(self):
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.cancel()
        self._start_timer()

    def _start_timer(self):
        self.timer_thread = threading.Timer(GOOGLE_SR_TIMEOUT, self._switch_to_vosk)
        self.timer_thread.start()

    def _switch_to_vosk(self):
        if self.stop_flag:
            return

        def wait_and_start():
            while self.speaking:
                time.sleep(0.1)

            if not self.stop_flag:
                self.google_sr_active = False
                print("🔁 Reactivating VOSK listening...")
                self.start_listening()

        threading.Thread(target=wait_and_start).start()

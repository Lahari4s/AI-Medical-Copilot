import threading
import pyttsx3

def speak_text(text):
    def run_speech():
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 160)
            engine.say(text[:1000])
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print("Voice error:", e)

    threading.Thread(target=run_speech).start()
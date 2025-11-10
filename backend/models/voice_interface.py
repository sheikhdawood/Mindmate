# voice_interface.py
import os
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from chatbot_core import MentalHealthChatbot

class VoiceInterface:
    def __init__(self):
        self.bot = MentalHealthChatbot()
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:
            print("\n🎤 Listening...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"🗣️ You said: {text}")
                return text
            except sr.UnknownValueError:
                return "Sorry, I didn’t catch that."
            except sr.RequestError:
                return "Speech recognition service unavailable."

    def speak(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        playsound("response.mp3")
        os.remove("response.mp3")

    def run(self):
        print("🧠 Voice Mental Health Chatbot — Speak to start.\nSay 'exit' anytime to stop.\n")

        while True:
            user_input = self.listen()

            if any(word in user_input.lower() for word in ["exit", "quit", "bye", "stop"]):
                self.speak("Take care of yourself. Remember, you are not alone.")
                print("👋 Session ended.")
                break

            emotion = (
                "sadness" if "sad" in user_input.lower()
                else "joy" if "happy" in user_input.lower()
                else "anger" if "angry" in user_input.lower()
                else "default"
            )

            response = self.bot.generate_reply(user_input, emotion)
            print(f"🤖 Bot: {response}\n")
            self.speak(response)


if __name__ == "__main__":
    VoiceInterface().run()

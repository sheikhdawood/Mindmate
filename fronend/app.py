import streamlit as st
import requests
from gtts import gTTS
from io import BytesIO
import base64
import speech_recognition as sr

FASTAPI_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="MindMate - Mental Health Chatbot", page_icon="🧠", layout="centered")

st.title("🧠 MindMate - Your Mental Health Companion")
st.caption("Providing emotional support, positivity, and mindful suggestions 💬")

# Session state setup

if "history" not in st.session_state:
    st.session_state.history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# --- Voice Input ---
def listen_to_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... please speak clearly.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.success(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Sorry, I didn’t catch that.")
        except sr.RequestError:
            st.error("⚠️ Speech recognition service unavailable.")
        return None

# --- Text-to-speech ---
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    b64 = base64.b64encode(mp3_fp.read()).decode()
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# --- Send message to FastAPI backend ---
def send_message(message):
    response = requests.post(FASTAPI_URL, json={"user_id": user_id, "message": message})
    if response.status_code == 200:
        data = response.json()
        return data["reply"], data["emotion"]
    else:
        return "⚠️ Server error. Try again later.", "error"

# --- Sidebar ---
user_id = st.sidebar.text_input("Enter your User ID:", "user_001")

# --- Main Chat UI ---
st.subheader("💬 Chat with MindMate")

col1, col2 = st.columns([3, 1])

# Use key for text input to keep state synced
with col1:
    user_input = st.text_input(
        "Type your message here...",
        value=st.session_state.user_input,
        key="user_input"
    )

# Speak button updates input using callback
def update_from_voice():
    voice_text = listen_to_voice()
    if voice_text:
        st.session_state.user_input = voice_text

with col2:
    st.button("🎤 Speak", on_click=update_from_voice)

# Send message
if st.button("Send") and st.session_state.user_input.strip():
    reply, emotion = send_message(st.session_state.user_input.strip())
    st.session_state.history.append(("You", st.session_state.user_input.strip(), None))
    st.session_state.history.append(("MindMate", reply, emotion))
    speak_text(reply)
    # st.session_state.user_input = ""  # clear after send
    st.rerun()

# --- Display conversation history ---
st.subheader("🧾 Conversation History")
for sender, text, emotion in st.session_state.history:
    if sender == "You":
        st.markdown(f"**🧍 You:** {text}")
    else:
        emo_display = f" | Emotion detected: *{emotion}*" if emotion else ""
        st.markdown(f"**🤖 MindMate:** {text}{emo_display}")

# --- Clear chat ---
if st.sidebar.button("🗑️ Clear Chat"):
    try:
        requests.delete(f"http://127.0.0.1:8000/clear-chat/{user_id}")
    except:
        pass
    st.session_state.history = []
    st.session_state.user_input = ""
    st.rerun()

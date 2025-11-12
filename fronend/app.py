import streamlit as st
import requests
from gtts import gTTS
from io import BytesIO
import base64
import speech_recognition as sr
import pandas as pd
import plotly.express as px
from collections import Counter
import random

# ===== Backend URLs =====
FASTAPI_BASE = "http://127.0.0.1:8000"
CHAT_URL = f"{FASTAPI_BASE}/chat"
REGISTER_URL = f"{FASTAPI_BASE}/auth/register"
LOGIN_URL = f"{FASTAPI_BASE}/auth/login"
HISTORY_URL = f"{FASTAPI_BASE}/get-history"
CLEAR_URL = f"{FASTAPI_BASE}/clear-chat"

# ===== Page Setup =====
st.set_page_config(page_title="MindMate - Mental Health Chatbot", page_icon="🧠", layout="wide")

# ===== Helper: Auth API =====
import requests


def register_user(username, email, password):
    try:
        payload = {
            "name": username,
            "email": email,
            "password": password
        }
        res = requests.post(REGISTER_URL, json=payload)

        if res.status_code == 200:
            data = res.json()
            return {
                "success": True,
                "message": data.get("message", "Registration successful"),
                "token": data.get("token")
            }
        else:
            data = res.json()
            return {
                "success": False,
                "error": data.get("detail", "Registration failed. Try again.")
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }

def login_user(name, email, password):
    res = requests.post(LOGIN_URL, json={"name": name, "email": email, "password": password})
    return res.json() if res.status_code == 200 else {"error": "Login failed"}

# ===== Authentication =====
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "history" not in st.session_state:
    st.session_state.history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

st.title("🧠 MindMate - Your Mental Health Companion")
st.caption("Providing emotional support, positivity, and mindful suggestions 💬")

# ===== LOGIN / REGISTER UI =====
auth_tab = st.sidebar.radio("🔐 Authentication", ["Login", "Register"])

if not st.session_state.token:
    if auth_tab == "Login":
        st.sidebar.subheader("Login")
        name = st.sidebar.text_input("Name")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            data = login_user(name, email, password)
            if "access_token" in data:
                st.session_state.token = data["access_token"]
                st.session_state.user_id = data["user"]["_id"]
                st.session_state.user_name = name
                st.success(f"✅ Welcome back, {data['user']['username']}!")
                st.rerun()
            else:
                st.error(data.get("error", "Invalid credentials"))
    else:
        st.sidebar.subheader("Register")
        username = st.sidebar.text_input("Username")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            data = register_user(username, email, password)
            if "message" in data:
                st.success("🎉 Registration successful! Please login.")
            else:
                st.error(data.get("error", "Registrationnnnnn failed."))
else:
    # ===== MAIN CHAT SECTION =====
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

    def send_message(message):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(CHAT_URL, json={"user_id": st.session_state.user_id, "message": message}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["reply"], data["emotion"]
        else:
            return "⚠️ Server error. Try again later.", "error"

    # ===== Sidebar User Info =====
    st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.user_name}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.token = None
        st.session_state.user_id = None
        st.session_state.history = []
        st.rerun()

    st.sidebar.markdown("---")

    # ===== Main Layout =====
    col_chat, col_analytics = st.columns([2.2, 1.1])

    with col_chat:
        st.subheader("💬 Chat with MindMate")
        col1, col2 = st.columns([3, 1])

        with col1:
            user_input = st.text_input("Type your message...", value=st.session_state.user_input, key="user_input")

        def update_from_voice():
            voice_text = listen_to_voice()
            if voice_text:
                st.session_state.user_input = voice_text

        with col2:
            st.button("🎤 Speak", on_click=update_from_voice)

        if st.button("Send") and st.session_state.user_input.strip():
            reply, emotion = send_message(st.session_state.user_input.strip())
            st.session_state.history.append(("You", st.session_state.user_input.strip(), None))
            st.session_state.history.append(("MindMate", reply, emotion))
            speak_text(reply)
            # st.session_state.user_input = ""
            st.rerun()

        # ===== Chat Display =====
        st.markdown("<div class='main'>", unsafe_allow_html=True)
        emotion_colors = {"joy": "#00C853", "sadness": "#42A5F5", "anger": "#EF5350", "neutral": "#A9A9A9"}
        for sender, text, emotion in st.session_state.history:
            if sender == "You":
                st.markdown(f"<div class='chat-bubble-user'><b>🧍You:</b> {text}</div>", unsafe_allow_html=True)
            else:
                color = emotion_colors.get(emotion, "#E8EAF6")
                st.markdown(
                    f"<div style='background-color:{color};padding:10px;border-radius:12px;margin:6px 0;'>🤖 <b>MindMate:</b> {text}<br><small>Emotion: {emotion}</small></div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # ===== Analytics Section =====
    with col_analytics:
        st.markdown("### 📊 Emotional Analytics")

        with st.expander("💫 Mood Trend Tracker", expanded=False):
            if st.session_state.history:
                emotions = [emo for s, _, emo in st.session_state.history if s == "MindMate" and emo not in [None, "error", "default"]]
                if emotions:
                    counts = Counter(emotions)
                    df_emotions = pd.DataFrame(list(counts.items()), columns=["Emotion", "Count"])
                    fig = px.bar(df_emotions, x="Emotion", y="Count", color="Emotion", title="Mood Trend 💫")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No emotions detected yet.")
            else:
                st.info("Start chatting to track your mood trend.")

        with st.expander("🕒 Emotion Timeline", expanded=False):
            if st.session_state.history:
                emotion_data = []
                for s, _, emo in st.session_state.history:
                    if s == "MindMate" and emo not in [None, "error", "default"]:
                        emotion_data.append({"timestamp": len(emotion_data) + 1, "emotion": emo})

                if emotion_data:
                    df = pd.DataFrame(emotion_data)
                    levels = {"sadness": 1, "anger": 2, "neutral": 3, "joy": 4}
                    df["level"] = df["emotion"].map(levels).fillna(3)
                    fig2 = px.line(df, x="timestamp", y="level", text="emotion", markers=True, title="Emotion Flow 🧘‍♀️")
                    fig2.update_yaxes(tickvals=list(levels.values()), ticktext=list(levels.keys()))
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No timeline data yet.")
            else:
                st.info("Start chatting to generate emotion timeline.")

        with st.expander("🌤️ Mood Summary", expanded=False):
            if st.session_state.history:
                emotions = [emo for s, _, emo in st.session_state.history if s == "MindMate" and emo not in [None, "error", "default"]]
                if emotions:
                    counts = Counter(emotions)
                    total = sum(counts.values())
                    dominant = max(counts, key=counts.get)
                    positivity = round(((counts.get("joy", 0) + 0.5 * counts.get("neutral", 0)) / total) * 100, 1)

                    if positivity > 70:
                        summary = "You’re radiating positivity 🌞"
                    elif positivity >= 40:
                        summary = "Mixed emotions — holding steady 💫"
                    else:
                        summary = "Feeling low — remember, every emotion is valid ❤️"

                    st.metric("Dominant Emotion", dominant.capitalize())
                    st.metric("Positivity Level", f"{positivity}%")
                    st.info(summary)
                else:
                    st.info("No emotions detected yet.")
            else:
                st.info("Start chatting to generate mood summary.")

        with st.expander("🪷 Self-Care Tips", expanded=True):
            self_care_tips = {
                "sadness": [
                    "Take a deep breath — it's okay to feel. 🌧️",
                    "Write your thoughts — it brings clarity. 🖊️",
                    "Reach out to someone you trust. 💌",
                    "Step outside for fresh air. 🍃"
                ],
                "anger": [
                    "Pause and breathe slowly — peace over anger. 🌿",
                    "Go for a short walk to release tension. 🏃‍♂️",
                    "Reflect — what triggered it? ✨",
                    "Let it pass gently. ☁️"
                ],
                "joy": [
                    "Celebrate small wins! 🎉",
                    "Share your happiness with others. 💛",
                    "Take a gratitude moment. 🌈",
                    "Smile — you’re glowing! 😄"
                ],
                "neutral": [
                    "Take a mindful minute — breathe. 🕊️",
                    "Stretch a bit to refresh. 🌱",
                    "Journal your thoughts. ✍️",
                    "You’re doing great. 🌻"
                ]
            }

            latest_emotion = None
            for s, _, emo in reversed(st.session_state.history):
                if s == "MindMate" and emo not in [None, "error", "default"]:
                    latest_emotion = emo
                    break

            if latest_emotion:
                tip = random.choice(self_care_tips.get(latest_emotion, self_care_tips["neutral"]))
                st.success(f"💬 *{tip}*")
            else:
                st.info("Start chatting to receive personalized tips.")


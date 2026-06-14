
import streamlit as st
import google.generativeai as genai
import os

API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

SUBJECTS = [
    "Matematika", "Fisika", "Kimia", "Biologi",
    "Bahasa Inggris", "Sejarah", "Coding Python",
    "Coding JavaScript", "Umum"
]

def get_gemini_response(history, system_prompt):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )
    gemini_history = []
    for msg in history[:-1]:
        gemini_history.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [msg["content"]]
        })
    chat = model.start_chat(history=gemini_history)
    
    # ← stream=True ini kuncinya
    response = chat.send_message(history[-1]["content"], stream=True)
    for chunk in response:
        yield chunk.text  # kirim per potongan teks
# ============================================================

st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="wide")

with st.sidebar:
    st.title("⚙️ Pengaturan Tutor")
    tutor_name = st.text_input("Nama Tutor", value="Pak Budi")
    subject = st.selectbox("Mata Pelajaran", SUBJECTS)
    style = st.radio("Gaya Mengajar", [
        "Santai dan friendly 😊",
        "Formal dan terstruktur 📚",
        "Socratic (pancing pertanyaan) 🤔"
    ])
    st.divider()
    if st.button("🗑️ Reset Percakapan"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Model: Gemini 1.5 Flash")

st.title(f"🎓 {tutor_name} — Tutor {subject}")
st.caption("Tanyakan apa saja seputar pelajaran yang ingin dipelajari!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Tanya {tutor_name}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        sp = build_system_prompt(subject, style, tutor_name)
        
        # st.write_stream otomatis handle generator → tampil streaming
        full_response = st.write_stream(
            get_gemini_response(st.session_state.messages, sp)
        )

    st.session_state.messages.append({"role": "assistant", "content": full_response})

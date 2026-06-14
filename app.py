
import streamlit as st
from groq import Groq
import os

API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

SUBJECTS = [
    "Matematika", "Fisika", "Kimia", "Biologi",
    "Bahasa Inggris", "Sejarah", "Coding Python",
    "Coding JavaScript", "Umum"
]

def build_system_prompt(subject, style, name):
    return f"""Kamu adalah {name}, tutor AI ahli {subject}.
Gaya mengajar: {style}.
Aturan:
- Jelaskan bertahap dari dasar ke lanjut
- Gunakan analogi dan contoh nyata
- Untuk soal/kode, beri petunjuk dulu sebelum jawaban
- Tanya apakah siswa paham sebelum lanjut
- Jawab Bahasa Indonesia kecuali diminta lain
- Jika di luar topik {subject}, arahkan kembali sopan"""

def get_response(history, system_prompt):
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    full_response = ""
    placeholder = st.empty()

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        stream=True,
        max_tokens=1024
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content or ""
        full_response += text
        placeholder.markdown(full_response + " ▌")

    placeholder.markdown(full_response)
    return full_response

st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="wide")

with st.sidebar:
    st.title("⚙️ Pengaturan Tutor")
    tutor_name = st.text_input("Nama Tutor", value="Pak Budi")
    subject    = st.selectbox("Mata Pelajaran", SUBJECTS)
    style      = st.radio("Gaya Mengajar", [
        "Santai dan friendly 😊",
        "Formal dan terstruktur 📚",
        "Socratic (pancing pertanyaan) 🤔"
    ])
    st.divider()
    if st.button("🗑️ Reset Percakapan"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Model: Llama 3.3 70B via Groq")

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
        response = get_response(st.session_state.messages, sp)
    st.session_state.messages.append({"role": "assistant", "content": response})

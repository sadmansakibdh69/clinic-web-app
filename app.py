import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book a clinic appointment for a patient",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"}
                },
                "required": ["patient_name", "date", "time"]
            }
        }
    }
]

def book_appointment(patient_name, date, time):
    with open("appointments.txt", "a") as f:
        f.write(f"Patient: {patient_name} | Date: {date} | Time: {time}\n")
    return f"Appointment booked for {patient_name} on {date} at {time}"

st.title("🏥 Medicare Clinic Bot")

# Show appointments tab
tab1, tab2 = st.tabs(["💬 Chat", "📋 Appointments"])

with tab1:
    if "history" not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("Type your question...")

    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a clinic assistant. Help patients and book appointments when asked."},
            ] + st.session_state.history,
            tools=tools
        )

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            result = book_appointment(**arguments)
            st.session_state.history.append({"role": "assistant", "content": result})
        else:
            reply = response.choices[0].message.content
            st.session_state.history.append({"role": "assistant", "content": reply})

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

with tab2:
    st.subheader("📋 All Appointments")
    if os.path.exists("appointments.txt"):
        with open("appointments.txt", "r") as f:
            appointments = f.readlines()
        if appointments:
            for apt in appointments:
                st.info(apt.strip())
        else:
            st.write("No appointments yet.")
    else:
        st.write("No appointments yet.")
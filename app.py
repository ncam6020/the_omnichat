import streamlit as st
import openai
from PIL import Image
import pytesseract
import docx
import io

# Set page config
st.set_page_config(page_title="Minutes in a Minute ⏱️", page_icon="⏱️", layout="wide")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'meeting_details' not in st.session_state:
    st.session_state.meeting_details = {}

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""

if 'handwritten_notes' not in st.session_state:
    st.session_state.handwritten_notes = ""

# Sidebar
st.sidebar.title("Configuration")

# API Key input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
if api_key:
    openai.api_key = api_key

# Meeting Details Form
st.sidebar.subheader("Meeting Details")
with st.sidebar.expander("Add Meeting Details"):
    date = st.date_input("Date")
    time = st.time_input("Time")
    location = st.text_input("Location")
    project_name = st.text_input("Project Name")
    attendees = st.text_area("Attendees (one per line)")
    
    if st.button("Save Meeting Details"):
        st.session_state.meeting_details = {
            "Date": date.strftime("%Y-%m-%d"),
            "Time": time.strftime("%H:%M"),
            "Location": location,
            "Project Name": project_name,
            "Attendees": attendees.split("\n")
        }
        st.sidebar.success("Meeting details saved!")

# Upload Teams Transcript
uploaded_file = st.sidebar.file_uploader("Upload Teams Transcript (Word document)", type="docx")
if uploaded_file is not None:
    doc = docx.Document(uploaded_file)
    st.session_state.transcript = "\n".join([para.text for para in doc.paragraphs])
    st.sidebar.success("Transcript uploaded and processed!")

# Upload Handwritten Notes
uploaded_image = st.sidebar.file_uploader("Upload Handwritten Notes", type=["png", "jpg", "jpeg"])
if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.session_state.handwritten_notes = pytesseract.image_to_string(image)
    st.sidebar.success("Handwritten notes uploaded!")

# Model Parameters
model = st.sidebar.selectbox("Select OpenAI Model", ["gpt-3.5-turbo", "gpt-4"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)

# Reset Conversation
if st.sidebar.button("Reset Conversation"):
    st.session_state.chat_history = []
    st.session_state.transcript = ""
    st.session_state.handwritten_notes = ""
    st.sidebar.success("Conversation reset!")

# Main Content Area
st.title("Minutes in a Minute ⏱️")

# Generate Meeting Minutes Button
if st.button("Generate Meeting Minutes", key="generate_minutes"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        with st.spinner("Generating meeting minutes..."):
            prompt = f"""
            Generate professional meeting minutes based on the following information:
            
            Meeting Details:
            {st.session_state.meeting_details}
            
            Transcript:
            {st.session_state.transcript}
            
            Handwritten Notes:
            {st.session_state.handwritten_notes}
            
            Please format the minutes in a clear, concise manner with appropriate headings and bullet points.
            Include a summary of key discussion points, decisions made, and action items.
            End with a disclaimer stating these are AI-generated minutes and participants should provide any corrections if needed.
            """
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "system", "content": "You are a professional meeting minutes generator."},
                          {"role": "user", "content": prompt}],
                temperature=temperature
            )
            
            minutes = response.choices[0].message.content
            st.session_state.chat_history.append(("assistant", minutes))

# Transcribe Handwritten Notes Button
if st.button("Transcribe Handwritten Notes", key="transcribe_notes"):
    if st.session_state.handwritten_notes:
        st.text_area("Transcribed Notes", st.session_state.handwritten_notes, height=200)
    else:
        st.warning("No handwritten notes uploaded yet.")

# Display Chat History (Meeting Minutes)
for role, content in st.session_state.chat_history:
    if role == "assistant":
        st.markdown(content)

# Chat Input for Further Interaction
user_input = st.text_input("Let's Make Some Meeting Minutes...", key="user_input")
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    
    with st.spinner("Thinking..."):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant for generating and modifying meeting minutes."}] +
                     [{"role": m[0], "content": m[1]} for m in st.session_state.chat_history],
            temperature=temperature
        )
        
        ai_response = response.choices[0].message.content
        st.session_state.chat_history.append(("assistant", ai_response))
        st.markdown(ai_response)

# Footer
st.markdown("---")
st.markdown("Powered by OpenAI and Streamlit")

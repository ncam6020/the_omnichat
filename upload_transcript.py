import streamlit as st
from docx import Document

def upload_transcript(display_in_chat=False):
    # Upload Transcript component
    uploaded_file = st.sidebar.file_uploader("Upload a Word file (e.g., meeting transcript):", type=['docx'], key='upload_transcript')
    if uploaded_file is not None:
        # Read and convert Word document to text
        doc = Document(uploaded_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        transcript_text = '\n'.join(full_text)

        # Add transcript text to session state for LLM use
        st.session_state.transcript_context = transcript_text

        # Provide success feedback to the user
        st.success("Transcript uploaded and processed successfully!")

        # Optionally, add transcript to chat if required
        if display_in_chat:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"Transcript: {transcript_text}"
                    }]
                }
            )

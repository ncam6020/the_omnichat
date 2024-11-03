# Modified function to use `display_in_chat` parameter
def upload_transcript(display_in_chat=False):
    uploaded_file = st.sidebar.file_uploader("Upload a Word file (e.g., meeting transcript):", type=['docx'], key='upload_transcript')
    if uploaded_file is not None:
        # Read and convert Word document to text
        doc = Document(uploaded_file)
        full_text = [para.text for para in doc.paragraphs]
        transcript_text = '\n'.join(full_text)

        # Add transcript text to session messages for LLM use
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
        else:
            # Store the transcript for LLM use but do not display it in the chat window
            st.session_state.transcript_context = transcript_text

        st.success("Transcript uploaded and processed successfully!")


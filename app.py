# Cleaned up version of the MinutesInAMinute Streamlit app
import streamlit as st
from openai import OpenAI
import dotenv
import os
from PIL import Image
import base64
from io import BytesIO
from meeting_details_form import render_meeting_details_form
from upload_transcript import upload_transcript
import openai
import docx

dotenv.load_dotenv()

# Only use OpenAI models
openai_models = [
    "gpt-4o-mini", 
    "gpt-4-turbo", 
    "gpt-3.5-turbo-16k", 
    "gpt-4",
    "gpt-4o",
    "gpt-4-32k",
]

# Function to query and stream the response from OpenAI
def stream_llm_response(model_params, api_key):
    response_message = ""
    client = OpenAI(api_key=api_key)

    # Add transcript context if available
    if "transcript_context" in st.session_state and "messages" in st.session_state:
        st.session_state.messages.insert(0, {
            "role": "user",
            "content": [{
                "type": "text",
                "text": f"Transcript context: {st.session_state.transcript_context}"
            }]
        })

    for chunk in client.chat.completions.create(
        model=model_params["model"] if "model" in model_params else "gpt-4o",
        messages=st.session_state.messages,
        temperature=model_params["temperature"] if "temperature" in model_params else 0.3,
        max_tokens=4096,
        stream=True,
    ):
        chunk_text = chunk.choices[0].delta.content or ""
        response_message += chunk_text
        yield chunk_text

    st.session_state.messages.append({
        "role": "assistant", 
        "content": [
            {
                "type": "text",
                "text": response_message,
            }
        ]})

# Function to convert file to base64
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode('utf-8')

def main():
    # --- Page Config ---
    st.set_page_config(
        page_title="Minutes in about a Minute",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # --- Header ---
    st.markdown("""<h1 style="text-align: center; color: #6ca395;">🤖 <i>Minutes in a Minute</i> 💬</h1>""", unsafe_allow_html=True)

    # --- Side Bar ---
    with st.sidebar:
        default_openai_api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        st.text_input("Introduce your OpenAI API Key (https://platform.openai.com/)", value=default_openai_api_key, type="password", key="openai_api_key")
        st.divider()
        
        # Add button to view/update meeting form
        if st.button('View/Update Meeting Form'):
            st.session_state.update_form = True

        # Upload transcript functionality
        upload_transcript(display_in_chat=False)

        st.divider()

        
        # Chat input
        if prompt := st.chat_input("Lets Make Some Meeting Minutes..."):
            st.session_state.messages.append(
                {
                    "role": "user", 
                    "content": [{
                        "type": "text",
                        "text": prompt,
                    }]
                }
            )
            
            # Display the new messages
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                st.write_stream(
                    stream_llm_response(
                        model_params=model_params, 
                        api_key=openai_api_key
                    )
                )

if __name__ == "__main__":
    main()

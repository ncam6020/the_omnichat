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

    # --- Sidebar Configuration ---
    with st.sidebar:
        # API Key Input
        default_openai_api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        st.text_input("Introduce your OpenAI API Key (https://platform.openai.com/)", value=default_openai_api_key, type="password", key="openai_api_key")
        st.divider()
        
        # Add button for meeting form
        st.write(f"### **🖼️ Add Meeting Details:**")
        if st.button('Key Meeting Data'):
            st.session_state.update_form = True
        
        st.divider()
      
        # Upload MSWord Transcripts
        st.write(f"### **🖼️ Add Teams Transcripts:**")
        upload_transcript(display_in_chat=False)

        st.divider()

        # Image Upload for Handwritten Notes
        st.write(f"### **🖼️ Add Handwritten Notes:**")

        def add_image_to_messages():
            if st.session_state.uploaded_img or ("camera_img" in st.session_state and st.session_state.camera_img):
                img_type = st.session_state.uploaded_img.type if st.session_state.uploaded_img else "image/jpeg"
                raw_img = Image.open(st.session_state.uploaded_img or st.session_state.camera_img)
                # Append image to the session, view it in the chat
                st.session_state.messages.append(
                    {
                        "role": "user", 
                        "content": [{
                            "type": "image_url",
                            "image_url": {"url": f"data:{img_type};base64,{get_image_base64(raw_img)}"}
                        }]
                    }
                )
                st.success("Image uploaded successfully! Now you can use the 'Transcribe Handwritten Notes' button to extract the text.")

        st.file_uploader(
            "Upload an image:", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=False,
            key="uploaded_img",
            on_change=add_image_to_messages,
        )

        if st.button("Transcribe Handwritten Notes"):
            if "uploaded_img" in st.session_state or "camera_img" in st.session_state:
                raw_img = Image.open(st.session_state.uploaded_img or st.session_state.camera_img)
                prompt = "Please transcribe my handwritten notes to text."
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                )
                st.success("Image transcription prompt added. The assistant will now process it.")

    # --- Main Content Configuration ---
    # Checking if the user has introduced the OpenAI API Key, if not, a warning is displayed
    openai_api_key = st.session_state.openai_api_key
    if openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key:
        st.write("#")
        st.warning("⬅️ Please introduce an API Key to continue...")
    else:
        client = OpenAI(api_key=openai_api_key)

        # Debug API key being used (truncated for safety)
        st.write(f"Using API Key: {openai_api_key[:8]}...")  # Truncated key for safety

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # --- Meeting Details Form ---
        render_meeting_details_form()

        # Displaying the previous messages if there are any
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                for content in message["content"]:
                    if content["type"] == "text":
                        st.write(content["text"])
                    elif content["type"] == "image_url":      
                        st.image(content["image_url"]["url"])

        # If there's a transcription request, handle it here in the main content
        if "uploaded_img" in st.session_state or "camera_img" in st.session_state:
            if st.session_state.messages and st.session_state.messages[-1]["content"][0]["text"] == "Please transcribe my handwritten notes to text.":
                with st.chat_message("assistant"):
                    try:
                        st.write_stream(
                            stream_llm_response(
                                model_params={
                                    "model": st.session_state.get("model", "gpt-4o"),
                                    "temperature": st.session_state.get("temperature", 0.3)
                                },
                                api_key=openai_api_key
                            )
                        )
                    except openai.error.AuthenticationError:
                        st.error("Authentication Error: Please check your OpenAI API Key.")

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
                try:
                    st.write_stream(
                        stream_llm_response(
                            model_params=model_params, 
                            api_key=openai_api_key
                        )
                    )
                except openai.error.AuthenticationError:
                    st.error("Authentication Error: Please check your OpenAI API Key.")

if __name__ == "__main__":
    main()

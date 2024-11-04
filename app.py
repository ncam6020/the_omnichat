# Cleaned up version of the Minutes in a Minute Streamlit app
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

def extract_text_from_image(image, api_key):
    # Convert the image to a base64 string
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Use OpenAI's GPT model to interpret the image content
    prompt = "Extract the handwritten notes from the provided image and transcribe them into text."
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert at reading and transcribing handwritten notes."},
            {"role": "user", "content": f"Image data: {img_str}. {prompt}"}
        ],
        temperature=0.5,
        max_tokens=1000
    )

    extracted_text = response.choices[0].message["content"].strip()
    return extracted_text

def main():
    # --- Page Config ---
    st.set_page_config(
        page_title="Minutes in a Minute",
        page_icon="⏱️",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # --- Header ---
    st.markdown("""<h1 style="text-align: center; color: #6ca395;">⏱️ <i>Minutes in a Minute</i> 💬</h1>""", unsafe_allow_html=True)

    # --- Side Bar ---
    with st.sidebar:
        default_openai_api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        st.text_input("Introduce your OpenAI API Key (https://platform.openai.com/)", value=default_openai_api_key, type="password", key="openai_api_key")
        st.divider()

        # Side bar model options and inputs (Moved here as second component)
        model = st.selectbox("Select a model:", openai_models, index=0)
        with st.expander("⚙️ Model parameters"):
            model_temp = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.3, step=0.1)

        model_params = {
            "model": model,
            "temperature": model_temp,
        }

        def reset_conversation():
            if "messages" in st.session_state and len(st.session_state.messages) > 0:
                st.session_state.pop("messages", None)

        st.button(
            "🗑️ Reset conversation", 
            on_click=reset_conversation,
        )

        st.divider()
        
        # Step 1 - Add Meeting Details
        st.subheader("Step 1 - Add Meeting Details")
        if st.button('View/Update Meeting Form'):
            st.session_state.update_form = True

        # Step 2 - Upload Transcript
        st.subheader("Step 2 - Upload Transcript")
        upload_transcript(display_in_chat=False)

        # Step 3 - Add Handwritten Notes
        st.subheader("Step 3 - Add Handwritten Notes")
        st.file_uploader(
            "Upload an image:", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=False,
            key="uploaded_img"
        )
        if st.button('Process Uploaded Image'):
            if st.session_state.uploaded_img:
                img_type = st.session_state.uploaded_img.type
                raw_img = Image.open(st.session_state.uploaded_img)
                extracted_text = extract_text_from_image(raw_img, st.session_state.openai_api_key)
                # Append extracted text to session state without displaying in chat
                st.session_state.transcript_context = f"{st.session_state.transcript_context}\n{extracted_text}" if "transcript_context" in st.session_state else extracted_text
                st.success("Image uploaded and text extracted successfully!")

    # --- Main Content ---
    openai_api_key = st.session_state.openai_api_key
    if openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key:
        st.write("#")
        st.warning("⬅️ Please introduce an API Key to continue...")
    else:
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

        # Chat input
        if prompt := st.chat_input("Hi! Ask me anything..."):
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

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

        # File Upload for Word Documents
        st.write(f"### **📄 Upload a Word File:**")
        word_file = st.file_uploader(
            "Upload a Word document:",
            type=["docx"],
            accept_multiple_files=False,
            key="uploaded_word_file",
        )

        if word_file is not None:
            # Extract and display text from the uploaded Word file
            doc = docx.Document(word_file)
            transcript_text = "\n".join([para.text for para in doc.paragraphs])

            prompt = "Here is the transcript from the uploaded Word document:\n" + transcript_text
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            )
            st.success("Word file uploaded successfully! Transcript text has been added, and the assistant will now process it.")

            # Explicitly trigger the assistant to generate a response right away in the main content area
            model_params = {
                "model": "gpt-4o",  # Default model for processing
                "temperature": 0.3,
            }
            with st.chat_message("assistant"):
                st.write_stream(
                    stream_llm_response(
                        model_params=model_params,
                        api_key=default_openai_api_key
                    )
                )

    # --- Main Content ---
    # Checking if the user has introduced the OpenAI API Key, if not, a warning is displayed
    openai_api_key = st.session_state.openai_api_key
    if openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key:
        st.write("#")
        st.warning("⬅️ Please introduce an API Key to continue...")
    else:
        client = OpenAI(api_key=openai_api_key)

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

        # Side bar model options and inputs
        with st.sidebar:
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

            # Image Upload
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

            cols_img = st.columns(2)
            with cols_img[0]:
                st.file_uploader(
                    "Upload an image:", 
                    type=["png", "jpg", "jpeg"], 
                    accept_multiple_files=False,
                    key="uploaded_img",
                    on_change=add_image_to_messages,
                )

            # Commented out camera activation functionality
            # with cols_img[1]:                    
            #     st.checkbox("Activate camera", key="activate_camera")
            #     if st.session_state.activate_camera:
            #         st.camera_input(
            #             "Take a picture", 
            #             key="camera_img",
            #             on_change=add_image_to_messages,
            #         )

        # Button to extract text from the uploaded image
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

                # Explicitly trigger the assistant to generate a response right away in the main content area
                with st.chat_message("assistant"):
                    st.write_stream(
                        stream_llm_response(
                            model_params=model_params,
                            api_key=openai_api_key
                        )
                    )

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

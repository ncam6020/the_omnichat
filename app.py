import streamlit as st
import streamlit.components.v1 as components

def render_meeting_details_form():
    if 'form_filled' not in st.session_state or st.session_state.get('update_form', False):
        # --- Meeting Details Form ---
        with st.form(key='meeting_details_form'):
            st.header("Meeting Details")
            meeting_date = st.date_input("Meeting Date:", value=st.session_state.get('meeting_date', None))
            project_name = st.text_input("Project Name:", value=st.session_state.get('project_name', ""))
            project_number = st.text_input("Project Number:", value=st.session_state.get('project_number', ""))
            meeting_location = st.text_input("Meeting Location:", value=st.session_state.get('meeting_location', ""))
            attendees = st.text_area("Attendees:", value=st.session_state.get('attendees', ""))
            
            # Adding a new field for rich text notes
            notes = st.text_area("Notes (You can paste bullets or lists here):", value=st.session_state.get('notes', ""))

            submit_button = st.form_submit_button(label='Submit Meeting Details')

            if submit_button:
                st.session_state.meeting_date = meeting_date
                st.session_state.project_name = project_name
                st.session_state.project_number = project_number
                st.session_state.meeting_location = meeting_location
                st.session_state.attendees = attendees
                st.session_state.notes = notes

                meeting_details = {
                    "Meeting Date": meeting_date,
                    "Project Name": project_name,
                    "Project Number": project_number,
                    "Meeting Location": meeting_location,
                    "Attendees": attendees,
                    "Notes": notes
                }
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": f"Meeting Details: {meeting_details}"
                        }]
                    }
                )
                st.session_state.form_filled = True
                st.session_state.update_form = False
                st.success("Meeting details submitted successfully!")
    else:
        st.info("Meeting details have already been added to the chatbot.")

# Adding button in the sidebar to view and update the form
with st.sidebar:
    if st.button('View/Update Meeting Form'):
        st.session_state.update_form = True

# Upload Transcript component
from upload_transcript import upload_transcript
upload_transcript()

import streamlit as st
import streamlit.components.v1 as components

def render_meeting_details_form():
    if 'form_filled' not in st.session_state or st.session_state.get('update_form', False):
        # --- Meeting Details Form ---
        with st.form(key='meeting_details_form'):
            st.header("Meeting Details")
            meeting_date = st.date_input("Meeting Date:")
            project_name = st.text_input("Project Name:")
            project_number = st.text_input("Project Number:")
            meeting_location = st.text_input("Meeting Location:")
            attendees = st.text_area("Attendees:")
            
            # Adding a new field for rich text notes with bullet support
            notes = components.html(
                """
                <div contenteditable="true" style="border: 1px solid #ccc; padding: 10px; height: 200px; overflow: auto;">
                    <p>Enter your notes here...</p>
                </div>
                """,
                height=250
            )
            
            submit_button = st.form_submit_button(label='Submit Meeting Details')

            if submit_button:
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
        render_meeting_details_form()

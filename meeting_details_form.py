import streamlit as st

def render_meeting_details_form():
    # --- Meeting Details Form ---
    with st.form(key='meeting_details_form'):
        st.header("Meeting Details")
        meeting_date = st.date_input("Meeting Date:")
        project_name = st.text_input("Project Name:")
        project_number = st.text_input("Project Number:")
        meeting_location = st.text_input("Meeting Location:")
        attendees = st.text_area("Attendees:")
        notes = st.text_area("Notes (You can paste bullets or lists here):")

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
            st.success("Meeting details submitted successfully!")

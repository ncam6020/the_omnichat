import streamlit as st

def render_meeting_details_form():
    # --- Meeting Details Form ---
    with st.form(key='meeting_details_form'):
        st.header("Meeting Details")
        meeting_date = st.date_input("Meeting Date:")
        meeting_time = st.time_input("Meeting Time:")
        project_name = st.text_input("Project Name:")
        project_number = st.text_input("Project Number:")
        meeting_location = st.text_input("Meeting Location:")
        attendees = st.text_area("Attendees:")
        next_meeting_date = st.date_input("Next Meeting Date:")
        cc = st.text_area("Cc:")
        submit_button = st.form_submit_button(label='Submit Meeting Details')

        if submit_button:
            meeting_details = {
                "Meeting Date": meeting_date,
                "Meeting Time": meeting_time,
                "Project Name": project_name,
                "Project Number": project_number,
                "Meeting Location": meeting_location,
                "Attendees": attendees,
                "Next Meeting Date": next_meeting_date,
                "Cc": cc
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

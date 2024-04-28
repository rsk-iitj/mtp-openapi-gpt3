import streamlit as st
import pandas as pd
import json
import sqlite3
from datetime import datetime
import os


def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect('session_data.db')


def get_applications():
    """Retrieve all unique applications from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT application_name FROM sessions")
    apps = cursor.fetchall()
    conn.close()
    return [app[0] for app in apps]


def get_sessions_for_app(application_name):
    """Retrieve all sessions for a given application."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, doc_gen_id, model_used, filename FROM sessions WHERE application_name = ?",
                   (application_name,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions


def load_test_plan_data(filename):
    """Load the JSON data from the specified file."""
    with open(filename, 'r') as f:
        return json.load(f)


def sanitize_filename(name):
    """Sanitize the filename to avoid path traversal or illegal characters."""
    import re
    return re.sub(r'[^\w\s-]', '', name).strip()


def save_feedback(feedback_data, application_name, model_used):
    """Save feedback data to a CSV file, including the model used."""
    base_dir = "output/feedback"
    app_dir = os.path.join(base_dir, sanitize_filename(application_name))
    os.makedirs(app_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{sanitize_filename(application_name)}_test_plan_feedback_{timestamp}.csv"
    full_path = os.path.join(app_dir, filename)

    # Include the model info in the feedback DataFrame
    feedback_df = pd.DataFrame(feedback_data)
    feedback_df['Model Used'] = model_used  # Add a new column with the model info

    # Save the DataFrame to a CSV file
    feedback_df.to_csv(full_path, index=False)
    st.success(f"Feedback submitted successfully and saved to '{full_path}'.")


def feedback_app():
    st.title("Test Plan Feedback Application")

    # Select Application
    application_name = st.selectbox("Select an Application", get_applications())
    if not application_name:
        st.stop()
    st.subheader(f"Feedback for Test Plan of Application:  {application_name}!")
    # Select Document Session
    sessions = get_sessions_for_app(application_name)
    session_choice = st.selectbox("Select a Document Session", sessions,
                                  format_func=lambda x: f"{x[1]} - {os.path.basename(x[3])}")
    if not session_choice:
        st.stop()

    session_id, doc_gen_id, model_used, filename = session_choice
    data = load_test_plan_data(filename)
    section_details = data['section_details']
    st.subheader(f"Document Session Details as mentioned below.")
    st.info(f"Session ID: {session_id}")
    st.info(f"Document Generation ID: {doc_gen_id}")
    st.info(f"Model Used: {model_used if model_used else 'Not Specified'}")
    st.info(f"Filename: {os.path.basename(filename)}")

    with st.form("feedback_form"):
        feedback_data = []
        for detail in section_details:
            with st.expander(f"View Content for {detail['Section']}"):
                st.write(detail['Content'])
            detail_rating = st.slider(f"Detail for {detail['Section']}", 1, 10,
                                      key=f"detail_rating_{detail['Section']}")
            clarity_rating = st.slider(f"Clarity for {detail['Section']}", 1, 10,
                                       key=f"clarity_rating_{detail['Section']}")
            relevance_rating = st.slider(f"Relevance for {detail['Section']}", 1, 10,
                                         key=f"relevance_rating_{detail['Section']}")
            feedback_data.append({
                "Section": detail['Section'],
                "Content": detail['Content'],
                "Word Count": detail['Word Count'],
                "Generation Time": detail['Generation Time'],
                "Detail Rating": detail_rating,
                "Clarity Rating": clarity_rating,
                "Relevance Rating": relevance_rating
            })

        st.subheader("Overall Test Plan Feedback")
        overall_quality = st.slider("Overall Quality", 1, 10)
        overall_details = st.slider("Overall Detailing", 1, 10)
        overall_clarity = st.slider("Overall Clarity", 1, 10)
        overall_relevance = st.slider("Overall Relevance", 1, 10)
        feedback_data.append({
            "Section": "Overall Feedback",
            "Content": "N/A",
            "Word Count": "N/A",
            "Detail Rating": overall_details,
            "Clarity Rating": overall_clarity,
            "Relevance Rating": overall_relevance,
            "Overall Quality": overall_quality
        })

        if st.form_submit_button("Submit All Feedback"):
            save_feedback(feedback_data, application_name, model_used)


if __name__ == "__main__":
    feedback_app()

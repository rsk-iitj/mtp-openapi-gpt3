import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os
import sqlite3

def sanitize_filename(name):
    """Sanitize the filename to avoid path traversal or illegal characters."""
    import re
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')


def load_test_plan_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def save_feedback(feedback_data, application_name, model_name):
    base_dir = "output/feedback"
    app_dir = os.path.join(base_dir, sanitize_filename(application_name))
    # Ensure the directory exists, if not create it
    os.makedirs(app_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{sanitize_filename(application_name)}_test_plan_feedback_{timestamp}.csv"
    # Construct full path to save the file
    full_path = os.path.join(app_dir, filename)

    # Create a DataFrame and add the model name as a column
    df = pd.DataFrame(feedback_data)
    df['Model Name'] = model_name  # Add the model name for each feedback entry

    df.to_csv(full_path, index=False)
    st.success(f"Feedback submitted successfully and saved to '{full_path}'.")


def feedback_app():
    try:
        filename = sys.argv[1]
        session_id = sys.argv[2]
        doc_id = sys.argv[3]# Assumes the filename is the first argument
        model_used = sys.argv[4]
    except IndexError:
        st.error("No filename provided. Please launch this app with a filename argument.")
        return

    data = load_test_plan_data(filename)
    section_details = data['section_details']
    application_name = data['application_name']
    st.title(f"Feedback for Test Plan of Application: {application_name}")
    st.info(f"Session id to Generate Feedback Form  : {session_id}!")
    st.info(f"Doc id to Generate Feedback Form: {doc_id}!")
    st.info(f"File Used to Generate Feedback Form : {filename}!")
    st.info(f"Model Used: {model_used}!")

    with st.form("feedback_form"):
        feedback_data = []
        for detail in section_details:
            with st.expander(f"View content for {detail['Section']}"):
                st.write(detail['Content'])
            st.subheader(f"Feedback for {detail['Section']}")
            detail_rating = st.slider(f"Detail for {detail['Section']}", 1, 10,
                                      key=f"detail_{detail['Section']}_rating")
            clarity_rating = st.slider(f"Clarity for {detail['Section']}", 1, 10,
                                       key=f"clarity_{detail['Section']}_rating")
            relevance_rating = st.slider(f"Relevance for {detail['Section']}", 1, 10,
                                         key=f"relevance_{detail['Section']}_rating")
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
        overall_quality = st.slider("Overall Quality", 1, 10, key="overall_quality")
        overall_details = st.slider("Overall Detailing", 1, 10, key="overall_details")
        overall_clarity = st.slider("Overall Clarity", 1, 10, key="overall_clarity")
        overall_relevance = st.slider("Overall Relevance", 1, 10, key="overall_relevance")

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

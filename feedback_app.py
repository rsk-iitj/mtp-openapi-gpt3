import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys


def sanitize_filename(name):
    """Sanitize the filename to avoid path traversal or illegal characters."""
    import re
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')


def load_test_plan_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def save_feedback(feedback_data, application_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{sanitize_filename(application_name)}_test_plan_feedback_{timestamp}.csv"
    df = pd.DataFrame(feedback_data)
    df.to_csv(filename, index=False)
    st.success(f"Feedback submitted successfully and saved to '{filename}'.")


def feedback_app():
    st.title("Feedback for Test Plan")

    # Use sys.argv to get the filename passed as an argument
    try:
        filename = sys.argv[1]  # Assumes the filename is the first argument
    except IndexError:
        st.error("No filename provided. Please launch this app with a filename argument.")
        return

    data = load_test_plan_data(filename)
    section_details = data['section_details']
    application_name = data['application_name']

    with st.form("feedback_form"):
        feedback_data = []
        for detail in section_details:
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
            save_feedback(feedback_data, application_name)


if __name__ == "__main__":
    feedback_app()

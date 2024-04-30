import streamlit as st
import os
from file_handling.file_reader_folder import extract_texts_from_folder
from nlp_pre_processing.keyword_extraction import extract_keywords
from open_ai.openai_integration import generate_section, list_engines
from nlp_pre_processing.criticality_analysis import assess_sentiment

st.title('Automated Test Plan Generator')

# Load OpenAI API key and list available engines
api_key = st.secrets["OPENAI_API_KEY"]
engines = list_engines(api_key)
selected_engine = st.selectbox("Select an OpenAI engine:", engines)

# Domain selection
domains = [
    "Telecom Industry", "E-Commerce", "IT Industry", "Marketing, Advertising, Sales", "Government sector",
    "Media & Entertainment", "Travel & Tourism", "IoT & Geofencing", "Finances",
    "Supply Chain, Inventory & Order Management", "Health Care, Fitness & Recreation",
    "Social Media, Social Media Analysis", "Ticketing", "Service Sector", "Gaming Industry",
    "Education Industry", "Mobile App Development", "Distribution Management System",
    "Science & Innovation", "Construction & Engineering", "Manufacturing",
    "Ecology and Environmental Protection", "Project Management Industry", "Logistics",
    "Procurement Management Solution", "Digital Agriculture"
]
selected_domain = st.selectbox("Select the application domain:", domains)

# Detailed tech stack inputs
tech_stack = {
    "Frontend Technology": st.selectbox("Select Frontend Technology", ["React", "Angular", "Vue", "Other"]),
    "Backend Technology": st.selectbox("Select Backend Technology", ["Node.js", "Python", "Java", "Other"]),
    "Database": st.selectbox("Select Database", ["MySQL", "MongoDB", "PostgreSQL", "Other"]),
    "Messaging Queue": st.selectbox("Select Messaging Queue", ["RabbitMQ", "Kafka", "AWS SQS", "Other"]),
    "Cloud Infrastructure": st.selectbox("Select Cloud Infrastructure", ["AWS", "Azure", "Google Cloud", "Other"]),
    "Additional Technologies": st.text_input("Specify any additional technologies not listed above:")
}

# Automation and resources
test_automation_required = st.radio("Is Test Automation Required?", ('Yes', 'No'))
num_testers = st.number_input("Number of Testers", min_value=0, value=0, step=1)
num_automation_testers = st.number_input("Number of Automation Testers", min_value=0, value=0, step=1)
num_test_lead = st.number_input("Number of Test Leads", min_value=0, value=0, step=1)
num_test_managers = st.number_input("Number of Test Managers", min_value=0, value=0, step=1)

# Directory path input for documents
document_directory = st.text_input("Enter the directory path to scan for documents:")

if st.button("Extract Text and Generate Test Plan"):
    if document_directory:
        # Extract text from all supported documents in the directory
        extracted_texts = extract_texts_from_folder(document_directory)
        user_stories_text = "\n\n".join(extracted_texts)
        st.text_area("Extracted User Stories", user_stories_text, height=300)

        # Continue with keyword extraction and sentiment analysis
        keywords = extract_keywords(user_stories_text)
        sentiment = assess_sentiment(user_stories_text).polarity

        sections = [
            "Test Plan Identifier", "References", "Introduction", "Test Items", "Software Risk Issues",
            "Features to be Tested", "Features not to be Tested", "Approach", "Item Pass/Fail Criteria",
            "Suspension Criteria and Resumption Requirements", "Test Deliverables", "Remaining Test Tasks", "Test Data Needs",
            "Environmental Needs", "Staffing and Training Needs", "Responsibilities", "Schedule",
            "Planning Risks and Contingencies", "Approvals", "Glossary", "Test Estimation"
        ]

        options = {
            'domain': selected_domain, 'tech_stack': tech_stack,
            'test_automation': test_automation_required, 'num_testers': num_testers,
            'num_automation_testers': num_automation_testers, 'num_test_lead': num_test_lead,
            'num_test_managers': num_test_managers,
            'keywords': ', '.join(keywords), 'sentiment': sentiment
        }

        full_test_plan = {}
        for section in sections:
            full_test_plan[section] = generate_section(selected_engine, section, user_stories_text, api_key, options)
            st.subheader(section)
            st.write(full_test_plan[section])
    else:
        st.error("Please enter a valid directory path.")

import streamlit as st
from file_handling.file_reader_folder import extract_texts_from_folder
from pre_processing.keyword_extraction import extract_keywords
from open_ai.openai_integration_updated import generate_section, list_engines, generate_test_plan_identifier, extract_main_features_and_criticality,ai_based_testing_estimation,generate_excluded_features_section
from pre_processing.sentiment_analysis import assess_sentiment
from open_ai.openai_integration_updated import generate_test_deliverables_section,generate_environmental_needs_section,generate_schedule_section,generate_responsibilities_section
from open_ai.openai_integration_updated import generate_introduction_section,generate_glossary_section,generate_remaining_test_tasks
st.title('Automated Test Plan Generator')

# Load OpenAI API key and list available engines
api_key = st.secrets["OPENAI_API_KEY"]
engines = list_engines(api_key)
selected_engine = st.selectbox("Select an OpenAI engine:", engines)

# Application name and document handling inputs
application_name = st.text_input("Enter the Application Name:")
creation_date = st.date_input("Creation Date")
created_by = st.text_input("Created By")
approvers = st.text_input("Enter Approvers (comma-separated):")
reviewers = st.text_input("Enter Reviewers (comma-separated):")

# Domain and technical stack selections
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
reference_urls = st.text_area("Enter reference URLs (comma-separated if multiple):")
tech_stack = {
    "Frontend Technology": st.selectbox("Select Frontend Technology", ["React", "Angular", "Vue", "Other"]),
    "Backend Technology": st.selectbox("Select Backend Technology", ["Node.js", "Python", "Java", "Other"]),
    "Database": st.selectbox("Select Database", ["MySQL", "MongoDB", "PostgreSQL", "Other"]),
    "Messaging Queue": st.selectbox("Select Messaging Queue", ["RabbitMQ", "Kafka", "AWS SQS", "Other"]),
    "Cloud Infrastructure": st.selectbox("Select Cloud Infrastructure", ["AWS", "Azure", "Google Cloud", "Other"]),
    "Additional Technologies": st.text_input("Specify any additional technologies not listed above:")
}

# Automation and resources

num_testers = st.number_input("Number of Functional Testers", min_value=0, value=0, step=1)
num_test_lead = st.number_input("Number of Test Leads", min_value=0, value=0, step=1)
num_test_managers = st.number_input("Number of Test Managers", min_value=0, value=0, step=1)

test_automation = st.checkbox("Is Automation Testing Required?")
num_automation_testers = st.number_input("Number of Automation Testers", min_value=0, value=0, step=1) if test_automation else 0

performance_testing = st.checkbox("Is Performance Testing Required?")
num_performance_testers = st.number_input("Number of Performance Testers", min_value=0, value=0, step=1) if performance_testing else 0

security_testing = st.checkbox("Is Security Testing Required?")
num_security_testers = st.number_input("Number of Security Testers", min_value=0, value=0, step=1) if security_testing else 0
# Directory path input for documents
document_directory = st.text_input("Enter the directory path to scan for documents:")

if st.button("Extract Text and Generate Test Plan"):
    if document_directory:
        extracted_texts, file_names = extract_texts_from_folder(document_directory)
        user_stories_text = "\n\n".join(extracted_texts)
        st.text_area("Extracted User Stories", user_stories_text, height=300)

        keywords = extract_keywords(user_stories_text)
        features, criticalities = extract_main_features_and_criticality(selected_engine, user_stories_text, api_key)
        urls_list = reference_urls.split(',') if reference_urls else []
        sections = [
            "Test Plan Identifier", "References","Approvals", "Introduction", "Test Items", "Software Risk Issues",
            "Features to be Tested", "Features not to be Tested", "Approach", "Item Pass/Fail Criteria",
            "Suspension Criteria and Resumption Requirements", "Test Deliverables", "Remaining Test Tasks", "Test Data Needs",
            "Environmental Needs", "Staffing and Training Needs", "Responsibilities", "Schedule",
            "Planning Risks and Contingencies", "Test Estimation","Glossary"
        ]

        options = {
            'application_name': application_name,
            'created_by': created_by,
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'domain': selected_domain, 'tech_stack': tech_stack,
            'test_automation': test_automation, 'num_testers': num_testers,
            'num_automation_testers': num_automation_testers,
            'num_test_lead': num_test_lead,
            'num_performance_testers': num_performance_testers,
            'num_security_testers': num_security_testers,
            'num_test_managers': num_test_managers,
            'keywords': ', '.join(keywords), 'features': features, 'criticalities': criticalities,
            'approvers': approvers.split(','),
            'reviewers': reviewers.split(','),
            'file_names': file_names
        }


        full_test_plan = {}
        for section in sections:
            st.subheader(section)
            if section == "Test Plan Identifier":
                references_text = "Documents:\n" + "\n".join(options['file_names'])
                references_text += "\n\nReferenced URLs:\n" + "\n".join(options['urls'])
                full_test_plan[section] = references_text
            elif section == "References":
                references_text = "\n".join(options['file_names'])  # List all file names as references
                full_test_plan[section] = references_text
            elif section == "Approvals":
                approvals_text = "Approvers:\n" + "\n".join(options['approvers']) + "\n\n" + "Reviewers:\n" + "\n".join(options['reviewers'])
                full_test_plan[section] = approvals_text
            elif section == "Test Estimation":
                estimation_texts = []
                if test_automation:
                    estimation_texts.append(ai_based_testing_estimation(selected_engine, user_stories_text, features, num_automation_testers, "Automation Testing", api_key))
                else:
                    estimation_texts.append("Estimation for Automation Testing was not done as it was not chosen to be estimated.")
                if performance_testing:
                    estimation_texts.append(ai_based_testing_estimation(selected_engine, user_stories_text, features, num_performance_testers, "Performance Testing", api_key))
                else:
                    estimation_texts.append("Estimation for Security Testing was not done as it was not chosen to be estimated.")
                if security_testing:
                    estimation_texts.append(ai_based_testing_estimation(selected_engine, user_stories_text, features, num_security_testers, "Security Testing", api_key))
                else:
                    estimation_texts.append("Estimation for Security Testing was not done as it was not chosen to be estimated.")
                full_test_plan[section] = "\n\n".join(estimation_texts)
            elif section == "Features not to be Tested":
                excluded_features_text = generate_excluded_features_section(
                    selected_engine,
                    "Features not to be Tested",
                    user_stories_text,
                    features,
                    api_key,
                    options
                )
                full_test_plan[section] = excluded_features_text
            elif section == "Test Deliverables":
                deliverables_text = generate_test_deliverables_section(selected_engine, api_key, options)
                full_test_plan[section] = deliverables_text
            elif section == "Environmental Needs":
                environmental_needs_text = generate_environmental_needs_section(selected_engine, api_key, options)
                full_test_plan[section] = environmental_needs_text
            elif section == "Schedule":
                schedule_section = generate_schedule_section(selected_engine, api_key, options)
                full_test_plan[section] = schedule_section
            elif section == "Responsibilities":
                responsibility_section = generate_responsibilities_section(selected_engine, api_key, options)
                full_test_plan[section] = responsibility_section

            elif section == "Introduction":
                intro_section = generate_introduction_section(selected_engine, api_key, options)
                full_test_plan[section] = intro_section
            elif section == "Glossary":
                glossery_section = generate_glossary_section(selected_engine, api_key, user_stories_text)
                full_test_plan[section] = glossery_section
            elif section == "Remaining Test Tasks":
                remaing_section = generate_remaining_test_tasks(selected_engine, api_key, user_stories_text, options)
                full_test_plan[section] = remaing_section
            else:
                full_test_plan[section] = generate_section(selected_engine, section, user_stories_text, api_key, options)
            st.write(full_test_plan[section])
    else:
        st.error("Please enter a valid directory path.")

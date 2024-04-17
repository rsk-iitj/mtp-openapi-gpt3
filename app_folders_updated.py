import streamlit as st
import time
import re
from datetime import datetime
from file_handling.file_reader_folder import extract_texts_from_folder,save_test_plan,download_link
from pre_processing.keyword_extraction import extract_keywords
from open_ai.openai_integration_updated import generate_section, list_engines, generate_test_plan_identifier, \
    extract_main_features_and_criticality, ai_based_testing_estimation, generate_excluded_features_section, \
    generate_features_to_be_tested_section, generate_staffing_and_training_needs
from pre_processing.sentiment_analysis import assess_sentiment
from open_ai.openai_integration_updated import generate_test_deliverables_section,generate_environmental_needs_section,generate_schedule_section,generate_responsibilities_section
from open_ai.openai_integration_updated import generate_introduction_section,generate_glossary_section,generate_remaining_test_tasks
st.title('Automated Test Plan Generator')

# Load OpenAI API key and list available engines
api_key = st.secrets["OPENAI_API_KEY"]
engines = list_engines(api_key)
selected_engine = st.selectbox("Select an OpenAI engine:", engines)

# Application name and document handling inputs
def custom_header(text, level=2, size='16px'):
    st.markdown(f'<h{level} style="font-size: {size};">{text}</h{level}>', unsafe_allow_html=True)

custom_header("Author Details", level=3, size='22px')
creation_date = st.date_input("Creation Date")
created_by = st.text_input("Created By")

custom_header("Approver Section", level=3, size='22px')
if 'approvers' not in st.session_state:
    st.session_state['approvers'] = []
if 'reviewers' not in st.session_state:
    st.session_state['reviewers'] = []

def format_person_info(person):
    # Handle 'To be Decided' dates and properly formatted dates
    date = person['date']
    if date == 'To be Decided':
        formatted_date = date
    else:
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
    return f"Name: {person['name']}, Role: {person['role']}, Date: {formatted_date}"

def add_person(category, name, role, date):
    # Store the date directly if 'To be Decided'
    date_to_store = 'To be Decided' if date == 'To be Decided' else date.strftime('%Y-%m-%d')
    st.session_state[category].append({
        'name': name,
        'role': role,
        'date': date_to_store
    })

def display_people(category):
    if st.session_state[category]:
        for person in st.session_state[category]:
            st.text(format_person_info(person))

# Form for Approvers
with st.form("approvers_form"):
    approver_name = st.text_input("Approver Name", key="app_name")
    approver_role = st.text_input("Approver Role", key="app_role")
    date_tbd = st.checkbox("Date To be Decided", key="app_date_tbd")
    approver_date = st.date_input("Approval Date", key="app_date") if not date_tbd else 'To be Decided'
    submitted1 = st.form_submit_button("Add Approver")
    if submitted1:
        add_person('approvers', approver_name, approver_role, approver_date)
        st.success("Approver added successfully!")
        display_people('approvers')

# Form for Reviewers
with st.form("reviewers_form"):
    reviewer_name = st.text_input("Reviewer Name", key="rev_name")
    reviewer_role = st.text_input("Reviewer Role", key="rev_role")
    date_tbd = st.checkbox("Date To be Decided", key="rev_date_tbd")
    reviewer_date = st.date_input("Review Date", key="rev_date") if not date_tbd else 'To be Decided'
    submitted2 = st.form_submit_button("Add Reviewer")
    if submitted2:
        add_person('reviewers', reviewer_name, reviewer_role, reviewer_date)
        st.success("Reviewer added successfully!")
        display_people('reviewers')

def generate_approvals_text():
    approvers_text = "Approvers:\n" + "\n".join(format_person_info(person) for person in st.session_state['approvers'])
    reviewers_text = "Reviewers:\n" + "\n".join(format_person_info(person) for person in st.session_state['reviewers'])
    return approvers_text + "\n\n" + reviewers_text


def generate_version_number():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
# Domain and technical stack selections

custom_header("Application Section", level=3, size='22px')

application_name = st.text_input("Enter the Application Name:")
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
sections = [
    "Test Plan Identifier", "References", "Approvals", "Introduction", "Test Items", "Software Risk Issues",
    "Features to be Tested", "Features not to be Tested", "Approach", "Item Pass/Fail Criteria",
    "Suspension Criteria and Resumption Requirements", "Test Deliverables", "Remaining Test Tasks", "Test Data Needs",
    "Environmental Needs", "Staffing and Training Needs", "Responsibilities", "Schedule",
    "Planning Risks and Contingencies", "Test Estimation", "Glossary"
]

selected_domain = st.selectbox("Select the application domain:", domains)

custom_header("Technology Stack", level=3, size='18px')

tech_stack = {
    "Frontend Technology": st.selectbox("Select Frontend Technology", ["React", "Angular", "Vue", "Other"]),
    "Backend Technology": st.selectbox("Select Backend Technology", ["Node.js", "Python", "Java", "Other"]),
    "Database": st.selectbox("Select Database", ["MySQL", "MongoDB", "PostgreSQL", "Other"]),
    "Messaging Queue": st.selectbox("Select Messaging Queue", ["RabbitMQ", "Kafka", "AWS SQS", "Other"]),
    "Cloud Infrastructure": st.selectbox("Select Cloud Infrastructure", ["AWS", "Azure", "Google Cloud", "Other"]),
    "Additional Technologies": st.text_input("Specify any additional technologies not listed above:")
}

# Automation and resources

custom_header("Existing Team Details", level=3, size='22px')
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

custom_header("Reference Section", level=3, size='22px')
reference_urls = st.text_area("Enter reference URLs (comma-separated if multiple):")
if reference_urls.strip():  # Checks if there's any non-whitespace character
    urls = [url.strip() for url in re.split(r'[,\n]+', reference_urls) if url.strip()]
else:
    urls = []
custom_header("Upload the documents", level=3, size='22px')

document_directory = st.text_input("Enter the directory path to scan for all requirements & design documents:")

section_status_placeholder = st.empty()
local_progress_placeholder = st.empty()
overall_status_placeholder = st.empty()
overall_progress_placeholder = st.empty()

def display_all_sections_complete():
    st.markdown(
        "<div style='background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;'>"
        "All sections generated successfully! ✔️</div>",
        unsafe_allow_html=True
    )

# Function to simulate the generation of a section
def generate_section_progress(section_name, index, total_sections):
    section_status_placeholder.info(f"Generating Section: **{section_name}**...")
    local_progress = local_progress_placeholder.progress(0)
    steps = 10  # Number of steps within each section generation

    for step in range(steps):
        time.sleep(0.1)  # Simulate some processing time
        local_progress.progress((step + 1) / steps)

    overall_progress_placeholder.progress((index + 1) / total_sections)
    section_status_placeholder.success(f"Completed Section: **{section_name}** ✔️")

total_sections = len(sections)

if st.button("Generate Test Plan"):
    overall_status_placeholder.info("Preparing the Test Plan...")
    if document_directory:
        extracted_texts, file_names = extract_texts_from_folder(document_directory)
        user_stories_text = "\n\n".join(extracted_texts)
        st.text_area("Extracted User Stories", user_stories_text, height=300)

        keywords = extract_keywords(user_stories_text)
        features, criticalities = extract_main_features_and_criticality(selected_engine, user_stories_text, api_key)
        urls_list = reference_urls.split(',') if reference_urls else []


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
            'approvers': st.session_state['approvers'],
            'reviewers': st.session_state['reviewers'],
            'file_names': file_names,
            'performance_testing':performance_testing,
            'security_testing':security_testing,
            "urls":urls
        }


        full_test_plan = {}
        for index, section in enumerate(sections):
            st.subheader(section)
            if section == "Test Plan Identifier":
                test_plan_iden =  generate_test_plan_identifier(selected_engine, api_key, options, retries=5, base_delay=1.0)
                full_test_plan[section] = test_plan_iden
            elif section == "References":
                references_text = "Documents:\n"
                if options['file_names']:
                    references_text += "\n".join(f"{i + 1}. {name}" for i, name in enumerate(options['file_names']))
                else:
                    references_text += "No documents available."

                if options['urls']:
                    references_text += "\n\nReferenced URLs:\n" + "\n".join(
                        f"{i + 1}. {url}" for i, url in enumerate(options['urls']))
                else:
                    references_text += "\n\nNo referenced URLs provided."

                full_test_plan['References'] = references_text
            elif section == "Approvals":
                approvals_text =""
                if 'approvers' in st.session_state and 'reviewers' in st.session_state:
                    approvals_text = generate_approvals_text()
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
            elif section == "Features to be Tested":
                included_features_text = generate_features_to_be_tested_section(selected_engine, user_stories_text, api_key, options)
                full_test_plan[section] = included_features_text
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
            elif section == "Staffing and Training Needs":
                staffing_needs = generate_staffing_and_training_needs(selected_engine, user_stories_text, features, api_key, options)
                full_test_plan[section] = staffing_needs
            elif section == "Glossary":
                glossery_section = generate_glossary_section(selected_engine, api_key, user_stories_text)
                full_test_plan[section] = glossery_section
            elif section == "Remaining Test Tasks":
                remaing_section = generate_remaining_test_tasks(selected_engine, api_key, user_stories_text, options)
                full_test_plan[section] = remaing_section
            else:
                full_test_plan[section] = generate_section(selected_engine, section, user_stories_text, api_key, options)
            generate_section_progress(section, index, total_sections)
            st.write(full_test_plan[section])
        display_all_sections_complete()
        overall_status_placeholder.success("Test Plan generation complete! ✔, Scroll down to end of Test Plan to Download Test Plan!")
        doc = save_test_plan(full_test_plan)
        version_number = generate_version_number()
        filename = f"{sanitize_filename(application_name)}_v{version_number}_Test_Plan.docx"
        link = download_link(doc, filename, "Download Test Plan as Word Document")
        st.markdown(link, unsafe_allow_html=True)
        if st.button('Reset'):
            st.experimental_rerun()
    else:
        st.error("Please enter a valid directory path.")


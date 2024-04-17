from random import random
import openai
import time

def list_engines(api_key):
    """Retrieve and list all available OpenAI engines."""
    openai.api_key = api_key
    response = openai.Engine.list()
    return [engine['id'] for engine in response['data']]

def extract_main_features_and_criticality(engine, user_stories, api_key):
    """Extract main features from user stories using OpenAI and assess their criticality, with retry logic."""
    openai.api_key = api_key
    attempt_count = 0
    max_attempts = 5
    while attempt_count < max_attempts:
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Identify and evaluate the criticality of main features in the user stories."},
                    {"role": "user", "content": f"User stories:\n\n{user_stories}\n\nList the main features and assess their criticality."}
                ],
                max_tokens=250  # Adjusted for a more comprehensive response
            )
            features_criticality = response.choices[0].message['content'].strip()
            features = [feature.split(':')[0].strip() for feature in features_criticality.split(',')]
            criticalities = [feature.split(':')[1].strip() if ':' in feature else 'Unknown' for feature in features_criticality.split(',')]
            return features, criticalities
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default to 10 seconds if retry_after is not provided
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            attempt_count += 1
            if attempt_count == max_attempts:
                print("Maximum retry attempts reached. Failing operation.")
                break  # Exit loop after max retries
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            break  # Exit loop on unknown error
    return [], []  # Return empty lists if retries do not succeed


def generate_section(engine, section_name, user_stories, api_key, options):
    """Generate a specific section of the test plan based on section requirements."""
    openai.api_key = api_key
    main_features, criticalities = extract_main_features_and_criticality(engine, user_stories, api_key)

    # Combine features and criticalities into a formatted string
    features_with_criticality = [f"{feature}: {criticality}" for feature, criticality in
                                 zip(main_features, criticalities)]

    prompt = f"""
    Section: {section_name}
    Application Name: {options['application_name']}
    Domain: {options['domain']}
    Main Features: {', '.join(features_with_criticality)}
    Keywords: {options['keywords']}
    User Stories: {user_stories}
    Please provide concise details for this section focusing on the needs for this "{section_name}" of a test plan document, keeping in mind the domain and main features!.
    """
    attempt_count = 0
    while attempt_count < 10:  # Limit the number of retries to avoid infinite loops
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system",
                     "content": f"Generate the {section_name} section with a focus on essential requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e,
                                                 'retry_after') else 10  # Use 10 seconds if retry_after is not available
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            raise e
    raise Exception("Failed to generate section after multiple attempts due to rate limiting.")


def generate_test_plan_identifier(engine, api_key, options, retries=5, base_delay=1.0):
    """Generate the 'Test Plan Identifier' section with specific metadata, with retries for handling rate limits."""
    openai.api_key = api_key
    prompt = f"""
    Generate a unique identifier and creator information for a test plan.
    Application Name: {options['application_name']}
    Created By: {options['created_by']}
    Date: {options['creation_date']}
    Please provide a test plan identifier that includes a unique number and details about who created the test plan and when it was created.
    """
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Create a unique identifier for the test plan."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.5
            )
            return response.choices[0].message['content'].strip()
        except openai.error.RateLimitError:
            if attempt < retries - 1:
                sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                print(f"Rate limit exceeded. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print("Max retries exceeded. Failed to generate test plan identifier.")
                raise
        except openai.error.OpenAIError as e:
            print(f"Failed to generate test plan identifier: {str(e)}")
            raise




def ai_based_testing_estimation(engine, user_stories, feature_details, num_testers, testing_type, api_key):
    """Estimate testing efforts using AI based on the provided number of testers and testing type."""
    openai.api_key = api_key
    prompt = f"""
    Estimate the effort in man-days needed for {testing_type} given the following details:
    Features and their descriptions: {feature_details}
    Number of Testers: {num_testers}
    Please provide a detailed estimation considering the complexity and workload.
    """
    attempt_count = 0
    while attempt_count < 5:  # Limit the number of retries
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Calculate testing effort based on the details provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            estimated_effort = response.choices[0].message['content'].strip()
            return f"{testing_type} Estimated Effort: {estimated_effort} man-days"
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default to 10 seconds if not specified
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An error occurred while estimating efforts for {testing_type}: {str(e)}")
            if attempt_count == 4:  # Last attempt
                return f"{testing_type} Estimation failed after multiple attempts."
            attempt_count += 1
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"{testing_type} Estimation error, please check logs."


def generate_excluded_features_section(engine, section_name, user_stories, features, api_key, options):
    """Generate the 'Features not to be Tested' section with a focus on why these features are excluded."""
    openai.api_key = api_key
    prompt = f"""
    Section: {section_name}
    Application Name: {options['application_name']}
    Domain: {options['domain']}
    Exclusion Rationale: Identify features that should not be tested for this release. Consider features that are stable, 
    outside the scope of the current project, or deprecated. Highlight why testing these features is unnecessary or redundant.

    Current Features: {', '.join(features)}
    Keywords: {options['keywords']}
    Please elaborate on the rationale for excluding certain features from the testing process, ensuring clarity and justification for project stakeholders.
    """
    attempt_count = 0
    while attempt_count < 10:  # Limit the number of retries to avoid infinite loops
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": f"Generate the {section_name} section focused on non-testing rationale."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            raise e
    raise Exception("Failed to generate section after multiple attempts due to rate limiting.")


def generate_test_deliverables_section(engine, api_key, options):
    """Generate the 'Test Deliverables' section focused on actual testing outputs."""
    openai.api_key = api_key
    prompt = f"""
    Section: Test Deliverables
    Application Name: {options['application_name']}
    Domain: {options['domain']}
    Please list all the key deliverables that the testing team will provide upon completion of the testing phase. 
    This includes various types of reports and documentation that are crucial for understanding the results and process of testing.

    Expected Deliverables:
    - Test Case Documentation
    - Test Execution Report
    - Defect Reports
    - Test Summary Report
    - Testing Metrics and Analysis
    - Automation Scripts (if applicable)
    - Performance Testing Reports (if performed)

    Discuss the importance of each deliverable and how they contribute to the project's success.
    """
    try:
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[
                {"role": "system", "content": "Generate a comprehensive list of testing deliverables with descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        print(f"An OpenAI error occurred: {str(e)}")
        raise

def generate_environmental_needs_section(engine, api_key, options):
    """Generate the 'Environmental Needs' section focused on testing environments and resources."""
    openai.api_key = api_key
    prompt = f"""
    Section: Environmental Needs
    Application Name: {options['application_name']}
    Domain: {options['domain']}
    Describe the testing environments and resources required for the application, including any specific hardware, software, network configurations, and third-party services needed for comprehensive testing.

    Considerations might include:
    - Types of testing environments needed (e.g., Development, QA, Staging, Production).
    - Specific server or cloud infrastructure requirements.
    - Necessary desktops, mobile devices, or other hardware for testing.
    - Tools and services required for testing functionalities and performance.
    - Network setup and security configurations.
    - Any other physical or virtual resources necessary for executing the test plan effectively.

    Detail how these environments and resources contribute to the testing process and the importance of configuring them appropriately.
    """
    try:
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[
                {"role": "system", "content": "Generate detailed requirements for the testing environments necessary for the project."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        print(f"An OpenAI error occurred: {str(e)}")
        raise



def generate_schedule_section(engine, api_key, options):
    """Generate detailed schedules for various types of testing based on availability and testing needs."""
    openai.api_key = api_key

    # Mapping testing types to their respective requirement flags from options
    test_types = {
        'Functional Testing': True,  # Always required
        'Automation Testing': options['test_automation'],
        'Performance Testing': options['performance_testing'],
        'Security Testing': options['security_testing']
    }

    schedules = []
    for test_type, is_required in test_types.items():
        if is_required:  # Check if testing is required
            prompt = f"""
            Section: Schedule
            Application Name: {options['application_name']}
            Generate a detailed schedule for {test_type}. Consider the number of testers and the complexity of the application to define:
            - Test Planning: Define the timeframe for initial planning activities.
            - Test Design: Specify the period for creating detailed test cases and scripts.
            - Test Execution: Outline the execution phase timeline.
            - Test Reporting: Indicate when and how test results will be reviewed and reported.
            """

            try:
                response = openai.ChatCompletion.create(
                    model=engine,
                    messages=[
                        {"role": "system", "content": "Generate a detailed testing schedule."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.5
                )
                schedule_details = response.choices[0].message['content']
                schedules.append(f"{test_type} Schedule:\n{schedule_details}")
            except openai.error.OpenAIError as e:
                print(f"An error occurred while generating the schedule for {test_type}: {str(e)}")
                schedules.append(f"{test_type} Schedule: Error generating schedule.")

    return "\n\n".join(schedules)




def generate_responsibilities_section(engine, api_key, options):
    """Generate responsibilities based on the team composition and testing requirements."""
    openai.api_key = api_key
    responsibilities = []

    # Define roles based on the provided counts
    roles = {
        'Functional Testers': options['num_testers'],
        'Automation Testers': options['num_automation_testers'],
        'Performance Testers': options['num_performance_testers'],
        'Security Testers': options['num_security_testers'],
        'Test Lead': options['num_test_lead'],
        'Test Manager': options['num_test_managers']
    }

    # Only include roles that have personnel
    active_roles = {role: count for role, count in roles.items() if count > 0}

    if not active_roles:
        return "No responsibilities assigned due to lack of testing personnel."

    # Generate responsibilities for each active role
    for role, count in active_roles.items():
        prompt = f"""
        Role: {role}
        Count: {count}
        Generate detailed responsibilities for {role.lower()}s involved in the testing process based on the scope and complexity of the application:
        - What are the key tasks for {role.lower()}s?
        - How should they coordinate with other team members?
        - What are the deliverables expected from them?
        """

        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Generate detailed responsibilities for testing roles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            role_responsibilities = response.choices[0].message['content']
            responsibilities.append(f"{role} ({count} members): {role_responsibilities}")
        except openai.error.OpenAIError as e:
            print(f"An error occurred while generating responsibilities for {role}: {str(e)}")
            responsibilities.append(f"{role} ({count} members): Error in generating responsibilities.")

    return "\n\n".join(responsibilities)



def generate_introduction_section(engine, api_key, options):
    """Generate an introduction section that describes the application, its domain, tech stack, and the objectives of the test plan with retry logic."""
    openai.api_key = api_key
    # Constructing the tech stack description with specific technology names
    tech_stack_description = ', '.join([f"{tech}: {value}" for tech, value in options['tech_stack'].items() if value and value != 'Other'])

    prompt = f"""
    Application Name: {options['application_name']}
    Domain: {options['domain']}
    Tech Stack: {tech_stack_description}
    Describe the application's main functionality and its relevance to the specified domain. Outline the objectives of the test plan, focusing on how the testing will ensure the application meets its design and functionality requirements.
    """
    attempt_count = 0
    while attempt_count < 5:  # Retry up to 5 times
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Generate an introduction for the test plan."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default to 10 seconds if retry_after is not available
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            attempt_count += 1
            if attempt_count == 5:
                raise Exception("Maximum retry attempts reached, unable to generate introduction.") from e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            if attempt_count == 5:
                return "An unexpected error occurred while generating the introduction section."
            attempt_count += 1

    return "Failed to generate the introduction section after multiple attempts."




def generate_glossary_section(engine, api_key, user_stories_text):
    """Generate a glossary section that extracts and defines abbreviations and jargons from the user stories."""
    openai.api_key = api_key
    prompt = f"""
    Identify and define any abbreviations, jargons, or technical terms found in the following user stories:
    {user_stories_text}
    Provide concise definitions for each identified term to be included in the glossary of a test plan document.
    """
    attempt_count = 0
    while attempt_count < 5:  # Retry up to 5 times
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Extract and define technical terms for the glossary section."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,  # Increased token limit for comprehensive extraction
                temperature=0.5
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default to 10 seconds if retry_after is not available
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            attempt_count += 1
            if attempt_count == 5:
                raise Exception("Maximum retry attempts reached, unable to generate glossary.") from e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            if attempt_count == 5:
                return "An unexpected error occurred while generating the glossary section."
            attempt_count += 1

    return "Failed to generate the glossary section after multiple attempts."


def generate_remaining_test_tasks(engine, api_key, user_stories_text, options):
    """Generate a section outlining remaining test tasks after the initial planning phase."""
    openai.api_key = api_key
    prompt = f"""
    Given the initial planning has been completed for the application '{options['application_name']}' within the domain '{options['domain']}', list all remaining tasks that need to be addressed in the testing lifecycle. Include tasks related to:
    - Test Scripting
    - Test Execution
    - Test Reporting
    - Final Validation and Closure
    Context: The initial test planning has covered the fundamental setup and strategy outline. The application involves technologies such as {', '.join(options['tech_stack'].values())} and requires both functional and non-functional testing approaches.
    """
    attempt_count = 0
    while attempt_count < 5:  # Retry logic for robustness
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Generate a detailed list of remaining testing tasks."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,  # Sufficient tokens to cover detailed tasks
                temperature=0.5
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default wait time
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            if attempt_count == 5:
                raise Exception("Maximum retry attempts reached for generating remaining test tasks.") from e
            attempt_count += 1
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            if attempt_count == 5:
                return "An unexpected error occurred while generating the remaining test tasks section."
            attempt_count += 1

    return "Failed to generate the remaining test tasks section after multiple attempts."


def generate_features_to_be_tested_section(engine, user_stories, api_key, options):
    """Generate the 'Features to be Tested' section with details about each feature's importance and necessity for testing."""
    openai.api_key = api_key
    features, criticalities = extract_main_features_and_criticality(engine, user_stories, api_key)

    feature_details = []
    max_retries = 3  # Maximum number of retries for each feature
    for feature, criticality in zip(features, criticalities):
        attempt_count = 0
        while attempt_count < max_retries:
            try:
                prompt = f"""
                Feature: {feature}
                Criticality: {criticality}
                Explain why this feature is critical to be tested and what risks are involved if it is not thoroughly tested.
                """
                response = openai.ChatCompletion.create(
                    model=engine,
                    messages=[
                        {"role": "system", "content": "Generate a detailed explanation for testing a feature."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.5
                )
                detail = response.choices[0].message['content'].strip()
                feature_details.append(f"{feature} ({criticality}): {detail}")
                break  # Break the loop if successful
            except openai.error.RateLimitError as e:
                wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default wait time
                print(f"Rate limit exceeded for feature {feature}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempt_count += 1
            except openai.error.OpenAIError as e:
                print(f"Failed to generate detail for feature {feature} on attempt {attempt_count + 1}: {str(e)}")
                attempt_count += 1
            if attempt_count == max_retries:
                feature_details.append(
                    f"{feature} ({criticality}): Detailed explanation could not be generated after multiple attempts.")

    return "\n".join(feature_details)



def generate_staffing_and_training_needs(engine, user_stories, features, api_key, options):
    """Generate staffing and training needs based on the complexity of the project."""
    openai.api_key = api_key
    attempt_count = 0
    while attempt_count < 5:  # Limit the number of retries
        try:
            prompt = f"""
            Given the following details of a software project, determine the staffing and training needs for various types of testing:
            Application Name: {options['application_name']}
            Domain: {options['domain']}
            Features: {', '.join(features)}
            User Stories: {user_stories}
            Current Technical Stack: {options['tech_stack']}
            Evaluate how many testers are needed for functional, automation, performance, and security testing. Also, specify the types of training that would be beneficial for the testing team.
            """
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Calculate the required testing resources and training needs."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            return response.choices[0].message['content'].strip()
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default to 10 seconds
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            if attempt_count == 4:  # Last attempt
                raise e  # Optionally raise an error or handle it as needed
            attempt_count += 1
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            if attempt_count == 4:  # Last attempt
                raise e
            attempt_count += 1
    return "Unable to generate staffing and training needs after several attempts."

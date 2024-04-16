import openai
import time

def extract_main_features(engine, user_stories, api_key):
    """Extract main features from user stories using OpenAI with retry logic."""
    openai.api_key = api_key
    attempt_count = 0
    while attempt_count < 5:  # Limit the number of retries to prevent infinite loops
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "You are a highly skilled AI assistant capable of extracting key features from user stories."},
                    {"role": "user", "content": f"User stories:\n\n{user_stories}\n\nIdentify the main features described in these user stories."}
                ],
                max_tokens=150
            )
            main_features = response.choices[0].message['content'].strip().split(', ')
            return main_features
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Default to 10 seconds if retry_after is not available
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            attempt_count += 1
            if attempt_count == 5:
                raise Exception("Maximum retry attempts reached, unable to extract features.") from e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []  # Optionally, return an empty list or re-raise the exception
    return []  # Return empty list if all retries fail without a successful response


import openai
import time

def list_engines(api_key):
    """Retrieve and list all available OpenAI engines."""
    openai.api_key = api_key
    response = openai.Engine.list()
    return [engine['id'] for engine in response['data']]

def extract_main_features(engine, user_stories, api_key):
    """Extract main features from user stories using OpenAI with retry logic."""
    openai.api_key = api_key
    attempt_count = 0
    while attempt_count < 5:
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Identify the main features from the user stories."},
                    {"role": "user", "content": user_stories}
                ],
                max_tokens=150
            )
            main_features = response.choices[0].message['content'].strip().split(', ')
            return main_features
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            attempt_count += 1
            if attempt_count == 5:
                raise Exception("Maximum retry attempts reached, unable to extract features.") from e

def generate_section(engine, section_name, user_stories, api_key, options):
    """Generate a specific section of the test plan based on section requirements."""
    openai.api_key = api_key
    main_features = extract_main_features(engine, user_stories, api_key)
    sentiment_description = 'Critical' if options['criticality'] > 0.5 else 'Non-critical'
    prompt = f"""
    Section: {section_name}
    Application Name: {options['application_name']}
    Domain: {options['domain']}
    Main Features: {', '.join(main_features)}
    Keywords: {options['keywords']}
    Sentiment: {sentiment_description}
    Please provide concise details for this section of the test plan.
    """
    attempt_count = 0
    while attempt_count < 10:
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Generate details for the test plan section."},
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

def generate_test_plan_identifier(engine, api_key, options):
    """Generate the 'Test Plan Identifier' section with specific metadata."""
    openai.api_key = api_key
    prompt = f"""
    Generate a unique identifier and creator information for a test plan.
    Application Name: {options['application_name']}
    Created By: {options['created_by']}
    Date: {options['creation_date']}
    """
    try:
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[
                {"role": "system", "content": "Create a unique identifier for the test plan."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"Failed to generate test plan identifier: {str(e)}")
        raise

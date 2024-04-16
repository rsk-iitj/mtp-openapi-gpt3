import openai
import time

def list_engines(api_key):
    """Retrieve and list all available OpenAI engines."""
    openai.api_key = api_key
    response = openai.Engine.list()
    return [engine['id'] for engine in response['data']]

def generate_section(engine, section_name, user_stories, api_key, options):
    """Generate a specific section of the test plan based on section requirements."""
    openai.api_key = api_key
    prompt = f"""
    Section: {section_name}
    Domain: {options['domain']}
    User Stories: {user_stories}
    Keywords: {options['keywords']}
    Sentiment: {'Positive' if options['sentiment'] > 0 else 'Negative'}
    Please provide a concise details for this section focusing on needs for this "{section_name}" of a test plan keeping in mind domain, main features & user stories.
    """
    attempt_count = 0
    while attempt_count < 10:  # Limit the number of retries to avoid infinite loops
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": f"Generate the {section_name} section with a focus on essential requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 10  # Use 10 seconds if retry_after is not available
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            attempt_count += 1
        except openai.error.OpenAIError as e:
            print(f"An OpenAI error occurred: {str(e)}")
            raise e
    raise Exception("Failed to generate section after multiple attempts due to rate limiting.")


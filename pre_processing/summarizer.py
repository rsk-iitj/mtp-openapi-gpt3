# Example: summarizer.py
from transformers import pipeline

summarizer = pipeline("summarization", model="t5-small")

def summarize_text(user_stories):
    return summarizer(user_stories, max_length=100, min_length=30, do_sample=False)[0]['summary_text']


def preprocess_user_stories(user_stories):
    # Split long user stories into chunks if they exceed the token limit of the model
    chunks = (user_stories[i:i + 1024] for i in range(0, len(user_stories), 1024))
    summarized_text = ' '.join(summarizer(chunk)[0]['summary_text'] for chunk in chunks if chunk.strip())
    return summarized_text
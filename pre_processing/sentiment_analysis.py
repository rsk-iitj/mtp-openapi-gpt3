from textblob import TextBlob

import nltk

# Download necessary NLTK corpora
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('brown')

def assess_sentiment(user_stories):
    return TextBlob(user_stories).sentiment

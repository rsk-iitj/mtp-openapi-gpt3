# Example: keyword_extraction.py
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(text, top_n=10):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    keywords = [word for word in words if word not in stop_words and word.isalnum()]
    frequent_keywords = Counter(keywords).most_common(top_n)
    return [word for word, freq in frequent_keywords]

# In your main app.py


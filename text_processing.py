import nltk
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

def preprocess_text(text):
    """Process the input text for keyword extraction"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if w not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(w) for w in filtered_tokens]
    return lemmas

def extract_keywords_and_phrases(text, category_name):
    """Extract keywords and phrases from the text"""
    lemmas = preprocess_text(text)
    keywords_list = []
    for lemma in lemmas:
        keywords_list.append({"term": lemma, "tone": assign_tone(lemma, category_name)})
    return keywords_list

def assign_tone(term, category_name):
    """Assign tone to the term based on the category"""
    tone = []
    if category_name == "Explicit Sexual Acts":
        if any(word in term for word in ["fuck", "cum", "rimming", "fisting", "docking", "bdsm", "pegging"]):
            tone.append("explicit")
    elif category_name == "Emotional Intensity & States":
        if any(word in term for word in ["love", "affection", "romantic"]):
            tone.append("romantic")
    return tone

import spacy
import re
from collections import Counter

nlp = spacy.load("en_core_web_sm")  # Load the English language model

def preprocess_text(text):
    """Process the input text using spaCy."""
    doc = nlp(text)
    # Extract relevant tokens (nouns, adjectives, verbs, adverbs) and lemmatize
    return [token.lemma_.lower() for token in doc if token.pos_ in ("NOUN", "ADJ", "VERB", "ADV") and not token.is_stop and not token.is_punct and not token.is_space]
    # Consider adding named entities as well
    # return [token.lemma_.lower() for token in doc if token.pos_ in ("NOUN", "ADJ", "VERB", "ADV") and not token.is_stop] + [ent.text for ent in doc.ents]


def extract_keywords_and_phrases(text, category_name):
    """Extract key terms using spaCy."""
    doc = nlp(text)
    keywords = []

    # Add relevant lemmas (nouns, adjectives, verbs, adverbs)
    for token in doc:
      if token.pos_ in ("NOUN", "ADJ", "VERB", "ADV") and not token.is_stop and not token.is_punct and not token.is_space:
        keywords.append({"term": token.lemma_.lower(), "tone": assign_tone(token.lemma_.lower(), category_name)})

    # Add named entities
    for ent in doc.ents:
        keywords.append({"term": ent.text, "tone": assign_tone(ent.text, category_name)})

    # Add noun chunks (multi-word phrases)
    for chunk in doc.noun_chunks:
        keywords.append({"term": chunk.text, "tone": assign_tone(chunk.text, category_name)})

    return keywords

def assign_tone(term, category_name):
    """Assign tone to the term based on the category (placeholder - needs improvement)."""
    # VERY basic example - replace with VADER or a custom lexicon
    tone = []
    if category_name == "Explicit Sexual Acts":
      for word in ["fuck", "cum", "rimming", "fisting", "docking", "bdsm", "pegging"]:
        if word in term.lower():
          tone.append("explicit")
          break

    elif category_name == "Emotional Intensity & States":
      for word in ["love", "affection", "romantic"]:
        if word in term.lower():
          tone.append("romantic")
          break

    return tone

def process_texts(texts):
    """Processes a list of texts and returns word frequencies."""
    all_words = []
    for text in texts:
        # Use the improved extraction
        keywords = extract_keywords_and_phrases(text, "General")  # Use a general category for initial extraction
        all_words.extend([kw["term"] for kw in keywords])  # Extract just the terms

    word_counts = Counter(all_words)
    return dict(word_counts)  # Convert Counter to a regular dictionary

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import nltk
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from SPARQLWrapper import SPARQLWrapper, JSON  
import internetarchive as ia
import time
from urllib.parse import quote_plus
import logging
import matplotlib.pyplot as plt
import networkx as nx
import spacy
import streamlit as st
from transformers import pipeline

# Install required packages if missing
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = [
    "nltk", "scikit-learn", "pandas", "requests", "beautifulsoup4", "SPARQLWrapper", "internetarchive",
    "transformers", "spacy", "networkx", "matplotlib", "streamlit", "pyarrow"
]

for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Installing missing package: {package}")
        install_package(package)

# Download necessary resources
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)

nlp = spacy.load("en_core_web_sm")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize pipeline if transformers are available
try:
    narrative_generator = pipeline("text-generation", model="gpt2", max_length=200)
    transformers_available = True
except ImportError:
    print("Warning: transformers package not found. Narrative generation will be disabled.")
    transformers_available = False


def preprocess_text(text):
    """Process the input text for keyword extraction"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    tokens = nltk.word_tokenize(text)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    filtered_tokens = [w for w in tokens if w not in stop_words]
    lemmatizer = nltk.stem.WordNetLemmatizer()
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

def generate_lexicon(categories, all_texts):
    """Generate the lexicon based on categories and all texts"""
    lexicon = {"categories": []}
    for category in categories:
        keywords = []
        for text in all_texts:
            keywords.extend(extract_keywords_and_phrases(text, category))
        unique = {}
        for kw in keywords:
            term = kw["term"]
            if term not in unique:
                unique[term] = set(kw["tone"])
            else:
                unique[term].update(kw["tone"])
        unique_list = [{"term": term, "tone": list(tones)} for term, tones in unique.items()]
        lexicon["categories"].append({"name": category, "keywords": unique_list})
    return lexicon

def run_dashboard(lexicon):
    """Run the Streamlit dashboard"""
    st.title("Gay Life & Sexual Experiences Lexicon")
    
    # Dropdown menu to select a category
    selected_category = st.selectbox("Choose a category:", [cat["name"] for cat in lexicon["categories"]])
    
    # Display the selected category's terms
    for cat in lexicon["categories"]:
        if cat["name"] == selected_category:
            st.header(f"{cat['name']}")
            terms = ", ".join([kw["term"] for kw in cat["keywords"]])
            st.write("Here are the keywords associated with this category:")
            st.write(f"<ul>{''.join([f'<li>{term}</li>' for term in terms.split(', ')])}</ul>", unsafe_allow_html=True)

def main():
    categories = [
        "Physical Sensations & Actions", "Explicit Sexual Acts", "Emotional Intensity & States",
        "Contextual & Environmental Details", "Sexual Dynamics & Roles", "Sensory Descriptions",
        "Erotic Modifiers & Adjectives", "Historical & Cultural Context", "Psychological & Emotional Descriptors",
        "Sexual Fantasies & Imagination", "Relationship Dynamics & Intimacy", "Literary & Cinematic Influences",
        "Dynamic Modifiers & Temporal Cues", "Academic Terms", "Gay Archetypes", "Gay Roleplay & Kink Scenarios",
        "Kinks", "Gay Erotic Terms"
    ]
    all_texts = ["Example text for processing. This is a placeholder."]
    lexicon = generate_lexicon(categories, all_texts)
    
    # Display the Streamlit dashboard with generated lexicon
    run_dashboard(lexicon)

if __name__ == "__main__":
    main()

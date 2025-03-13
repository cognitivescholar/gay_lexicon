#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # <-- CRUCIAL: Must be at the top

# Import the functions from your modules.
from data_acquisition import (get_gutenberg_texts, get_wikiquote_quotes,
                              get_wikidata_items,
                              get_internet_archive_texts, get_reddit_comments)
from text_processing import preprocess_text, extract_keywords_and_phrases, assign_tone
from lexicon import generate_lexicon
# from utils import remove_duplicates  # Uncomment if you have this function
import streamlit as st


def main():
    categories = [  # Your categories here
        "Physical Sensations & Actions", "Explicit Sexual Acts", "Emotional Intensity & States",
        "Contextual & Environmental Details", "Sexual Dynamics & Roles", "Sensory Descriptions",
        "Erotic Modifiers & Adjectives", "Historical & Cultural Context", "Psychological & Emotional Descriptors",
        "Sexual Fantasies & Imagination", "Relationship Dynamics & Intimacy", "Literary & Cinematic Influences",
        "Dynamic Modifiers & Temporal Cues", "Academic Terms", "Gay Archetypes", "Gay Roleplay & Kink Scenarios",
        "Kinks", "Gay Erotic Terms"
    ]

    all_texts = []

    # --- Data Source Flags (You can control which sources to use here) ---
    use_gutenberg = True
    use_wikiquote = True
    use_wikidata = True
    use_internet_archive = True
    use_reddit = True

    # --- Project Gutenberg ---
    if use_gutenberg:
        author_keywords_list = [["Oscar Wilde"]]  # Example.
        gutenberg_texts = get_gutenberg_texts(author_keywords_list, num_books=2)
        all_texts.extend(gutenberg_texts)

    # --- Wikiquote ---
    if use_wikiquote:
        author_keywords_list = [["Gay", "Erotica"]]  # Example
        wikiquote_quotes = get_wikiquote_quotes(author_keywords_list)
        all_texts.extend(wikiquote_quotes)

    # --- Wikidata ---
    if use_wikidata:
        author_keywords_list = [["Gay", "Erotica"]]  # Example
        wikidata_items = get_wikidata_items(author_keywords_list)
        # Wikidata returns structured data, not raw text, so we need to extract
        # the descriptions.
        wikidata_texts = [item['description'] for item in wikidata_items]
        all_texts.extend(wikidata_texts)

    # --- Internet Archive ---
    if use_internet_archive:
        author_keywords_list = [["Gay", "Erotica"]] # Example
        ia_texts = get_internet_archive_texts(author_keywords_list, num_texts=2)
        all_texts.extend(ia_texts)

    # --- Reddit ---
    if use_reddit:
        subreddit_name = "gay"  # Example - be mindful of subreddit rules
        reddit_comments = get_reddit_comments(subreddit_name)
        all_texts.extend(reddit_comments)

    print(f"Collected {len(all_texts)} texts.")

    lexicon = generate_lexicon(categories, all_texts)
    run_dashboard(lexicon)


def run_dashboard(lexicon):
    """Runs the Streamlit dashboard."""
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


if __name__ == "__main__":
    main()

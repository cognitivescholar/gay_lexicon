from text_processing import extract_keywords_and_phrases

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

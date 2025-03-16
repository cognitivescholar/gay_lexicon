import os
import re
import random
from collections import Counter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# 📂 Folder where your downloaded texts are stored
OUTPUT_FOLDER = "output"

def load_texts():
    """Reads all saved texts from the output folder."""
    texts = {}
    
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith(".txt"):
            with open(os.path.join(OUTPUT_FOLDER, filename), "r", encoding="utf-8") as f:
                texts[filename] = f.read()
    
    return texts

# Load all texts
all_texts = load_texts()
print(f"\n📂 Loaded {len(all_texts)} texts for analysis!\n")

# 🔥 STEP 1: Summarize Each Text
def summarize_texts(texts):
    """Summarizes each text using Sumy's LSA summarizer."""
    summaries = {}

    for filename, content in texts.items():
        try:
            parser = PlaintextParser.from_string(content, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, 3)  # Get 3 sentences as a summary
            summaries[filename] = " ".join([str(sentence) for sentence in summary])
        except:
            summaries[filename] = "(Could not summarize: Text too short or complex.)"

    return summaries

summaries = summarize_texts(all_texts)

print("\n📖 **Summaries of Texts:**")
for file, summary in summaries.items():
    print(f"\n📜 **{file} Summary:**\n{summary}\n")

# 🔥 STEP 2: Detect LGBTQ+ Themes
THEMES = {
    "Forbidden Love": ["forbidden", "unspoken", "secret", "hidden", "unspeakable"],
    "Homoeroticism": ["desire", "passion", "longing", "embrace", "lips", "touch", "yearning"],
    "Repression": ["sin", "wrong", "shame", "hide", "deny", "suppress"],
    "Masculinity & Affection": ["brotherhood", "comradeship", "manly", "affection", "devotion"],
    "Society & Judgment": ["scandal", "trial", "ruined", "ostracized", "immoral"]
}

def detect_themes(texts):
    """Scans texts and detects recurring queer themes based on keyword counts."""
    theme_counts = {theme: 0 for theme in THEMES}

    for filename, content in texts.items():
        content_lower = content.lower()
        for theme, keywords in THEMES.items():
            for word in keywords:
                theme_counts[theme] += len(re.findall(r'\b' + word + r'\b', content_lower))

    return theme_counts

theme_results = detect_themes(all_texts)

print("\n🔥 **THEME ANALYSIS:** 🔥")
for theme, count in theme_results.items():
    print(f"{theme}: {count} mentions")

# 🔥 STEP 3: Extract Scandalous Passages
def extract_passages(texts, keywords, num_passages=3):
    """Finds and extracts juicy passages containing key words."""
    extracted = {}

    for filename, content in texts.items():
        matches = []
        lines = content.split(". ")  # Split text into sentences
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                matches.append(line.strip())

        if matches:
            extracted[filename] = random.sample(matches, min(num_passages, len(matches)))

    return extracted

keywords = ["embrace", "passion", "longing", "lips", "touch", "scandal", "desire", "shame"]
juicy_passages = extract_passages(all_texts, keywords)

print("\n🔥 **SCANDALOUS PASSAGES FOUND:** 🔥")
for file, passages in juicy_passages.items():
    print(f"\n📖 **From {file}:**")
    for passage in passages:
        print(f"- {passage}")

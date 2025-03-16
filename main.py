import json
import os
import time
from data_acquisition import (
    get_gutenberg_texts,
    get_wikiquote_quotes,
    fetch_wikipedia_texts,
    get_internet_archive_texts,
    fetch_reddit_texts,
    get_wikidata_items,
)

# Load or create config file
CONFIG_FILE = "config.json"

def load_config():
    """Loads the configuration from config.json, or creates one if missing."""
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found. Creating a new one.")
        default_config = {
            "project_gutenberg": {"enabled": True, "author_keywords": [], "title_keywords": []},
            "wikiquote": {"enabled": True, "page_titles": [], "phrases": []},
            "wikipedia": {"enabled": True, "page_titles": []},
            "internet_archive": {
                "enabled": True,
                "collection": "texts",
                "mediatype": "texts",
                "keyword_search": "",
                "year": "",
            },
            "reddit": {"enabled": True, "subreddit_names": [], "post_limit": 10, "comment_limit": 5},
            "wikidata": {"enabled": True, "queries": []},
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

def update_config(config):
    """Saves the updated configuration to the config.json file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def main():
    """Main function to run the data collection process."""
    config = load_config()

    # Gather input dynamically
    if config["project_gutenberg"]["enabled"]:
        authors = input("📚 Enter author names (comma-separated): ").strip().split(",")
        titles = input("📖 Enter book titles (comma-separated): ").strip().split(",")
        config["project_gutenberg"]["author_keywords"] = [a.strip() for a in authors if a.strip()]
        config["project_gutenberg"]["title_keywords"] = [t.strip() for t in titles if t.strip()]

    if config["wikiquote"]["enabled"]:
        pages = input("💬 Enter Wikiquote topics (comma-separated): ").strip().split(",")
        phrases = input("🔍 Enter specific phrases to search for in quotes (comma-separated): ").strip().split(",")
        config["wikiquote"]["page_titles"] = [p.strip() for p in pages if p.strip()]
        config["wikiquote"]["phrases"] = [ph.strip() for ph in phrases if ph.strip()]

    if config["wikipedia"]["enabled"]:
        wiki_titles = input("🌎 Enter Wikipedia page titles (comma-separated): ").strip().split(",")
        config["wikipedia"]["page_titles"] = [w.strip() for w in wiki_titles if w.strip()]

    if config["internet_archive"]["enabled"]:
        keyword = input("📜 Enter keywords for Archive.org search: ").strip()
        year = input("📅 Enter year (or leave blank for all years): ").strip()
        config["internet_archive"]["keyword_search"] = keyword
        config["internet_archive"]["year"] = year if year else ""

    if config["reddit"]["enabled"]:
        subreddits = input("👥 Enter subreddit names (comma-separated): ").strip().split(",")
        config["reddit"]["subreddit_names"] = [s.strip() for s in subreddits if s.strip()]

    if config["wikidata"]["enabled"]:
        queries = input("🔍 Enter Wikidata search queries (comma-separated): ").strip().split(",")
        config["wikidata"]["queries"] = [q.strip() for q in queries if q.strip()]

    # Save the updated config
    update_config(config)

    # Fetch data
    print("\n✨ Fetching all the juicy texts... Hold on to your wigs! ⏳✨\n")
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Create output folder
    OUTPUT_FOLDER = "output"
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Fetch texts
    gutenberg_texts = get_gutenberg_texts(
        config["project_gutenberg"]["author_keywords"],
        config["project_gutenberg"]["title_keywords"],
    )
    
    wikiquote_texts = get_wikiquote_quotes(config["wikiquote"]["page_titles"], config["wikiquote"]["phrases"])
    wikipedia_texts = fetch_wikipedia_texts(config["wikipedia"]["page_titles"])
    archive_texts = get_internet_archive_texts(
        config["internet_archive"]["collection"],
        config["internet_archive"]["mediatype"],
        config["internet_archive"]["keyword_search"],
        config["internet_archive"]["year"],
    )
    reddit_texts = fetch_reddit_texts(config["reddit"]["subreddit_names"], 20, 10)
    wikidata_entries = get_wikidata_items(config["wikidata"]["queries"])

    # Save results
    with open(f"{OUTPUT_FOLDER}/gutenberg_texts_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(gutenberg_texts))
    with open(f"{OUTPUT_FOLDER}/wikiquote_quotes_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(wikiquote_texts))
    with open(f"{OUTPUT_FOLDER}/wikipedia_texts_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(wikipedia_texts))
    with open(f"{OUTPUT_FOLDER}/archive_texts_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(archive_texts))
    with open(f"{OUTPUT_FOLDER}/reddit_threads_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(reddit_texts))
    with open(f"{OUTPUT_FOLDER}/wikidata_entries_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join([f"{entry['label']}: {entry['description']}" for entry in wikidata_entries]))

    print("\n💖 **ALL DATA FETCHED, HONEY!** 💖")
    print("\n📚 Data breakdown:")
    print(f"📂 Gutenberg Texts: {len(gutenberg_texts)}")
    print(f"💬 Wikiquote Quotes: {len(wikiquote_texts)}")
    print(f"🌎 Wikipedia Texts: {len(wikipedia_texts)}")
    print(f"📜 Archive.org Texts: {len(archive_texts)}")
    print(f"👥 Reddit Threads: {len(reddit_texts)}")
    print(f"🔍 Wikidata Entries: {len(wikidata_entries)}")

    print("\n📂 **All data has been saved in the `output/` folder!** 💾✨")


if __name__ == "__main__":
    main()

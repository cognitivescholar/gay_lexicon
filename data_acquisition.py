import requests
from bs4 import BeautifulSoup
import wikiquote
import wikipedia
import internetarchive as ia
from SPARQLWrapper import SPARQLWrapper, JSON
import praw
import os

# 📚 PROJECT GUTENBERG - SCRAPER
GUTENBERG_SEARCH_URL = "https://www.gutenberg.org/ebooks/search/?query={}&submit_search=Go%21"
GUTENBERG_BASE_URL = "https://www.gutenberg.org"

def search_gutenberg_books(query):
    """Searches Gutenberg for books based on a query (author or title)."""
    search_url = GUTENBERG_SEARCH_URL.format(query.replace(" ", "+"))
    response = requests.get(search_url)
    if response.status_code != 200:
        print(f"🚨 Failed to search Gutenberg for '{query}'")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    book_links = soup.select("li.booklink a.link")
    
    books = []
    for link in book_links[:5]:  # Limit results to avoid overloading
        book_id = link['href'].split('/')[-1]
        book_title = link.text.strip()
        books.append((book_id, book_title))
    
    return books

def get_gutenberg_texts(author_keywords, title_keywords):
    """Fetches texts from Project Gutenberg by searching for author and title keywords."""
    texts = []
    
    # Search by author
    for author in author_keywords:
        print(f"🔎 Searching Gutenberg for books by {author}...")
        books = search_gutenberg_books(author)
        texts.extend(download_gutenberg_books(books))
    
    # Search by title
    for title in title_keywords:
        print(f"🔎 Searching Gutenberg for books titled '{title}'...")
        books = search_gutenberg_books(title)
        texts.extend(download_gutenberg_books(books))

    return texts

def download_gutenberg_books(books):
    """Downloads books from Gutenberg given a list of (book_id, title)."""
    downloaded_texts = []
    
    for book_id, title in books:
        book_url = f"{GUTENBERG_BASE_URL}/cache/epub/{book_id}/pg{book_id}.txt"
        print(f"📥 Downloading '{title}' from {book_url}...")
        
        try:
            response = requests.get(book_url)
            if response.status_code == 200:
                text = response.text
                downloaded_texts.append(text)
            else:
                print(f"🚨 Failed to download '{title}' (HTTP {response.status_code})")
        except Exception as e:
            print(f"🚨 Error downloading '{title}': {e}")

    return downloaded_texts

# 🗣️ WIKIQUOTE SCRAPER
def get_wikiquote_quotes(page_titles, phrases):
    """Fetches quotes from Wikiquote pages matching given topics."""
    all_quotes = []

    for title in page_titles:
        try:
            quotes = wikiquote.quotes(title, lang="en")
            for quote in quotes:
                if not phrases or any(phrase.lower() in quote.lower() for phrase in phrases):
                    all_quotes.append(quote)
        except Exception as e:
            print(f"🚨 Error fetching quotes from Wikiquote page '{title}': {e}")

    return all_quotes

# 🌎 WIKIPEDIA SCRAPER
def fetch_wikipedia_texts(page_titles):
    """Fetches texts from Wikipedia based on page titles."""
    texts = []
    
    for title in page_titles:
        try:
            page = wikipedia.page(title, auto_suggest=False, redirect=True)
            texts.append(page.content)
        except wikipedia.exceptions.PageError:
            print(f"🚨 Error: Wikipedia page '{title}' not found.")
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"🚨 Error: '{title}' is ambiguous. Options: {e.options}")
        except Exception as e:
            print(f"🚨 Error fetching Wikipedia page '{title}': {e}")

    return texts

# 📜 INTERNET ARCHIVE SCRAPER
def get_internet_archive_texts(collection, mediatype, keyword_search, year):
    """Fetches texts from the Internet Archive."""
    all_texts = []
    
    search_query = f'collection:{collection} AND mediatype:{mediatype} AND "{keyword_search}" AND year:{year}'

    try:
        search = ia.search_items(search_query)
        count = 0

        for result in search:
            if count >= 5:
                break  # Stop when we've hit the limit

            try:
                identifier = result.get('identifier', None)
                if not identifier:
                    continue

                item = ia.get_item(identifier)
                files = list(item.get_files(formats=['Text', 'DjVuTXT', 'Plain Text']))

                for file in files:
                    if 'name' in file:
                        text_file = file['name']
                        with ia.get_item(identifier).get_file(text_file).open() as f:
                            text_content = f.read().decode('utf-8', errors='ignore')
                        all_texts.append(text_content)
                        count += 1
                        break  # Only grab the first available text file

            except Exception as e:
                print(f"🚨 Error fetching text from IA item {identifier}: {e}")

    except Exception as e:
        print(f"🚨 Error searching Internet Archive: {e}")

    return all_texts

# 👥 REDDIT SCRAPER
def fetch_reddit_texts(subreddit_names, post_limit=10, comment_limit=5):
    """Fetches texts from Reddit based on subreddit, post limit, and comment limit."""
    all_texts = []

    try:
        reddit = praw.Reddit(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent=os.environ.get('REDDIT_USER_AGENT')
        )
        for subreddit_name in subreddit_names:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=post_limit):
                post_text = submission.selftext
                comments_text = []
                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list()[:comment_limit]:
                    comments_text.append(comment.body)
                all_texts.append(post_text + "\n".join(comments_text))

    except Exception as e:
        print(f"🚨 Error fetching from subreddit {subreddit_name}: {e}")

    return all_texts

# 🔍 WIKIDATA SCRAPER
def get_wikidata_items(queries):
    """Fetches Wikidata items and their descriptions."""
    all_items = []

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    for query in queries:
        query_string = f"""
        SELECT DISTINCT ?item ?itemLabel ?description
        WHERE {{
          ?item rdfs:label|skos:altLabel "{query}"@en .
          ?item schema:description ?description.
          FILTER(LANG(?description) = "en")
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        LIMIT 100
        """
        sparql.setQuery(query_string)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                item_data = {
                    "label": result["itemLabel"]["value"],
                    "description": result["description"]["value"],
                }
                all_items.append(item_data)
        except Exception as e:
            print(f"🚨 Error querying Wikidata: {e}")

    return all_items

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET  # You need this here, too!
import re
from urllib.parse import quote_plus
import logging
import internetarchive as ia
from SPARQLWrapper import SPARQLWrapper, JSON  # CORRECT

def get_gutenberg_texts(author_keywords_list, num_books=1):
    """
    Fetches texts from Project Gutenberg based on author keywords.
    """
    all_texts = []
    for author_keywords in author_keywords_list:
        author_query = "+".join(author_keywords)
        search_url = f"https://www.gutenberg.org/ebooks/search/?query={author_query}&submit_search=Go%21"
        response = requests.get(search_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        book_links = soup.select('li.booklink a')

        for i, link in enumerate(book_links):
            if i >= num_books:
                break
            book_id = link['href'].split('/')[-1]
            try:  # Use try-except to handle potential errors
                text = get_gutenberg_text_by_id(book_id)
                if text:
                    all_texts.append(text)
            except Exception as e:
                print(f"Error getting book ID {book_id}: {e}")
    return all_texts

def get_gutenberg_text_by_id(book_id):
    """
    Fetches the full text of a book from Project Gutenberg given its ID.
    Handles both plain text and HTML formats, with error handling.
    """
    # Try plain text first
    text_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    response = requests.get(text_url)

    if response.status_code == 200:
        text = response.text
        start_marker = "*** START OF THIS PROJECT GUTENBERG EBOOK"
        end_marker = "*** END OF THIS PROJECT GUTENBERG EBOOK"
        start_index = text.find(start_marker)
        end_index = text.find(end_marker)

        if start_index != -1 and end_index != -1:
             return text[start_index + len(start_marker):end_index]
        else:
             return text #If it couldn't find markers, return the entire thing.
    else:
        # If plain text fails, try HTML and extract the main text
        html_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-h/{book_id}-h.htm"
        response = requests.get(html_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find and extract all <p> tags (adjust as needed for specific book structures)
            text = "\n".join([p.get_text(separator=" ", strip=True) for p in soup.find_all('p')])
            return text
        else:
            #If both fail, return
            return ""

# --- Wikiquote ---
def get_wikiquote_quotes(author_keywords_list):
    all_quotes = []
    for author_keywords in author_keywords_list:
        author_query = "+".join(author_keywords)  # Simple joining for now
        # URL-encode the query for Wikiquote
        encoded_query = quote_plus(author_query)
        url = f"https://en.wikiquote.org/w/api.php?action=query&format=json&list=search&srsearch={encoded_query}&srwhat=text&srlimit=50" #Increased to 50.

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'query' in data and 'search' in data['query']:
                for result in data['query']['search']:
                    page_title = result['title']
                    quotes = get_quotes_from_page(page_title)
                    all_quotes.extend(quotes)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Wikiquote: {e}")
    return all_quotes

def get_quotes_from_page(page_title):
    quotes = []
    # URL-encode the page title
    encoded_title = quote_plus(page_title)
    url = f"https://en.wikiquote.org/w/api.php?action=parse&format=json&page={encoded_title}&prop=wikitext"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'parse' in data and 'wikitext' in data['parse']:
            wikitext = data['parse']['wikitext']['*']
            # Extract quotes using a more robust regex (handles multi-line quotes)
            quote_matches = re.findall(r'\*\s?(.*?(?:\n\*\*.*)*)', wikitext)
            for match in quote_matches:
                 # Remove any remaining Wikitext formatting (e.g., bolding)
                cleaned_quote = re.sub(r"'{2,}", "", match).strip()
                if cleaned_quote:
                    quotes.append(cleaned_quote)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quotes from page {page_title}: {e}")
    return quotes

# --- Wikidata ---
def get_wikidata_items(author_keywords_list):
    all_items = []
    for author_keywords in author_keywords_list:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        query_terms = " ".join(author_keywords)  # Combine keywords for Wikidata query
        query = f"""
        SELECT DISTINCT ?item ?itemLabel ?description
        WHERE {{
          ?item rdfs:label|skos:altLabel "{query_terms}"@en.
          ?item schema:description ?description.
          FILTER(LANG(?description) = "en")
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 100
        """
        sparql.setQuery(query)
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
            print(f"Error querying Wikidata: {e}")
    return all_items

# --- Internet Archive ---
def get_internet_archive_texts(author_keywords_list, num_texts=2):
    all_texts = []
    for author_keywords in author_keywords_list:
        search_query = " ".join(author_keywords)  # Combine for IA search

        try:
            search = ia.search_items(search_query, fields=['identifier', 'title'])

            for i, result in enumerate(search): #Added limit here.
                if i >= num_texts:
                    break
                identifier = result['identifier']
                item = ia.get_item(identifier)

                # Check if the item has text files and retrieve them
                if item.item_metadata and 'files' in item.item_metadata:
                    for file in item.item_metadata['files']:
                        if file['format'] in ('Text', 'DjVuTXT', 'Plain Text'):
                            try:
                                text = item.get_file(file['name']).read().decode('utf-8', errors='ignore')
                                all_texts.append(text)
                                break #Stop after we get the first usable text.
                            except Exception as e:
                                print(f"Error reading file {file['name']} from IA item {identifier}: {e}")
        except Exception as e:
            print(f"Error searching Internet Archive: {e}")
    return all_texts

# --- Reddit ---
def get_reddit_comments(subreddit_name, num_posts=5, num_comments=10):
    """
    Fetches comments from a specified subreddit.  Now includes error handling.
    """
    all_comments = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    base_url = f"https://www.reddit.com/r/{subreddit_name}.json?limit={num_posts}"

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if 'data' in data and 'children' in data['data']:
            for post in data['data']['children']:
                if 'data' in post and 'id' in post['data']:
                    post_id = post['data']['id']
                    comments_url = f"https://www.reddit.com/r/{subreddit_name}/comments/{post_id}.json?limit={num_comments}"
                    comments_response = requests.get(comments_url, headers=headers)
                    comments_response.raise_for_status()
                    comments_data = comments_response.json()

                    if isinstance(comments_data, list) and len(comments_data) > 1 and 'data' in comments_data[1] and 'children' in comments_data[1]['data']:
                        for comment in comments_data[1]['data']['children']:
                            if 'data' in comment and 'body' in comment['data']:
                                all_comments.append(comment['data']['body'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Reddit: {e}")
    except (KeyError, IndexError) as e:
        print(f"Error parsing Reddit JSON: {e}")  # More specific error handling
    return all_comments

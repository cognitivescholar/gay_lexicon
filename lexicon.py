import json

def generate_lexicon(word_frequencies, existing_lexicon={}):
    """Generates or updates a lexicon based on word frequencies, with user approval."""
    approved_lexicon = existing_lexicon.copy()  # Start with existing lexicon

    print("\n--- Reviewing potential lexicon terms ---")
    for term, count in word_frequencies.items():
        if term not in approved_lexicon: #Only ask if it isn't already there
            while True: #Loop to ensure you get a valid input.
                response = input(f"Term: {term} (Frequency: {count})\nInclude in lexicon? (y/n/done): ").lower()
                if response == 'y':
                    approved_lexicon[term] = count
                    break  # Exit loop after valid input
                elif response == 'n':
                    break # Exit loop
                elif response == 'done':
                    return approved_lexicon
                else:
                    print("Invalid input. Please enter 'y', 'n', or 'done'.")
    return approved_lexicon
def load_lexicon(filepath="approved_lexicon.json"):
    """Loads an existing lexicon from a JSON file, if it exists."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("No existing lexicon found. Starting with an empty lexicon.")
        return {}  # Return an empty dictionary if the file doesn't exist
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{filepath}'. Starting with an empty lexicon.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred reading '{filepath}': {e}. Starting with an empty lexicon.")
        return {}

def save_lexicon(lexicon, filepath="approved_lexicon.json"):
    """Saves the lexicon to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lexicon, f, indent=4)  # Use json.dump for structured output
    except Exception as e:
        print(f"Error saving lexicon: {e}")

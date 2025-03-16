def remove_duplicates(input_list):
    """Removes duplicate items from a list while preserving order."""
    seen = set()
    return [x for x in input_list if not (x in seen or seen.add(x))]

# Add any other utility functions you might need here

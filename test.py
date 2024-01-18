import re
from typing import Optional

def extract_from_collection_modified(collection: str) -> Optional[str]:
    """
    Extracts a portion of a string based on specific patterns.
    First, it looks for 'paragraph_number_' or 'papers_number_'.
    If found, it extracts everything after the number and '_'.
    If not found, it extracts everything after 'paragraphs' or 'papers'.

    :param collection: The string to be processed.
    :return: The extracted string portion, or None if no relevant pattern is found.
    """
    # Try to extract after "paragraph_number_"
    paragraph_num_match = re.search(r"paragraph_(\d+)_", collection)
    if paragraph_num_match:
        # Extract everything after the number and "_"
        start_index = paragraph_num_match.end()
        return collection[start_index:]

    # Try to extract after "papers_number_"
    papers_num_match = re.search(r"papers_(\d+)_", collection)
    if papers_num_match:
        # Extract everything after the number and "_"
        start_index = papers_num_match.end()
        return collection[start_index:]

    # If no number patterns found, try to extract after "paragraphs" or "papers"
    paragraph_match = re.search(r"paragraphs_", collection)
    if paragraph_match:
        start_index = paragraph_match.end()
        return collection[start_index:]

    papers_match = re.search(r"papers_", collection)
    if papers_match:
        start_index = papers_match.end()
        return collection[start_index:]

    # Return None if no pattern matched
    return None

# Example string
collection = "algae_papers_10_specter2"

# Test the function
extracted_part = extract_from_collection_modified(collection)
print(extracted_part)

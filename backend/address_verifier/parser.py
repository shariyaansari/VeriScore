# address_verifier/parser.py
import re

# --- Individual Component Extractors ---

def extract_pincode(address):
    """Finds a 6-digit pincode in the address string."""
    match = re.search(r'\b\d{6}\b', address)
    if match:
        return match.group(0)
    return None

def extract_landmark(address):
    """Finds a landmark based on common keywords."""
    keywords = ['near', 'opposite', 'opp', 'behind', 'besides', 'next to', 'close to']
    lower_address = address.lower()
    for keyword in keywords:
        if keyword in lower_address:
            parts = lower_address.split(keyword, 1)
            landmark_text = parts[1].split(',')[0].strip()
            return landmark_text.title()
    return None

def extract_house_info(address):
    """A simple approach to get the first part of the address, likely house/building."""
    parts = address.split(',')
    if len(parts) > 1:
        return f"{parts[0].strip()}, {parts[1].strip()}"
    return parts[0].strip()

def extract_sector_info(address):
    """Extracts sector, block, or phase information."""
    match = re.search(r'(sector|block|phase)\s*[-]?\s*[\w\d]+', address, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

def extract_village_post(address):
    """Extracts village or post office information."""
    village, post = None, None
    village_match = re.search(r'(village|vpo|vill)\s*[:\-]?\s*([\w\s]+?)(,|$)', address, re.IGNORECASE)
    if village_match:
        village = village_match.group(2).strip().title()

    post_match = re.search(r'(post office|post|po)\s*[:\-]?\s*([\w\s]+?)(,|$)', address, re.IGNORECASE)
    if post_match:
        post = post_match.group(2).strip().title()
        
    return village, post

# ==============================================================================
# THIS IS THE MAIN FUNCTION YOUR API ROUTE WILL CALL
# ==============================================================================
def parse_full_address(raw_address):
    """
    Takes a raw address string and breaks it down into a structured dictionary
    by calling all the individual extractor functions.
    """
    # Call all your extractor functions
    pincode = extract_pincode(raw_address)
    landmark = extract_landmark(raw_address)
    house_info = extract_house_info(raw_address)
    sector_info = extract_sector_info(raw_address)
    village, post_office = extract_village_post(raw_address)
    
    # Assemble the final JSON object with all the new fields
    structured_address = {
      "raw_address": raw_address,
      "pincode": pincode,
      "house_building_info": house_info,
      "landmark": landmark,
      "sector_block_info": sector_info,
      "village": village,
      "post_office": post_office,
    }
    
    return structured_address
# address_verifier/verifier.py
import os
import requests
from googleapiclient.discovery import build
import googlemaps
import geocoder
from geopy.distance import geodesic
from fuzzywuzzy import fuzz 

# API Clients Initialization
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))

# Configuration Variables
API_KEY = os.getenv("GOOGLE_API_KEY")
GENERAL_CX = os.getenv("GENERAL_SEARCH_CX")
GOV_CX = os.getenv("GOV_SEARCH_CX")

# def verify_address(company_name, address, user_ip):
    # """Verifies a business address using multiple signals."""
    
    # --- NEW: Initialize the client here, after secrets are loaded ---
    # gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))
    
    # confidence_score = 0
#    findings = []

def google_search(query, search_engine_id):
    """Performs a Google search using the Custom Search API."""
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        result = service.cse().list(q=query, cx=search_engine_id, num=1).execute() # Only need the top result
        return result.get("items", [])
    except Exception as e:
        print(f"An API error occurred: {e}")
        return []


def verify_with_google_places(company_name, address):
    print("\n" + "="*50)
    print("--- DEBUGGING: Inside verify_with_google_places ---")

    if not API_KEY or API_KEY == "YOUR_GOOGLE_API_KEY" or not API_KEY.strip():
        print("DEBUG: Google API Key is missing or empty.")
        print("="*50 + "\n")
        return False, "Google API Key not configured"

    search_query = f"{company_name} {address}"
    endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': search_query,
        'inputtype': 'textquery',
        'fields': 'name',
        'key': API_KEY
    }

    print(f"DEBUG: Sending query to Google: {search_query}")

    try:
        response = requests.get(endpoint, params=params)
        results = response.json()

        print("DEBUG: Raw Google API Response:")
        print(results)
        print("-"*20)

        if results.get("status") == "OK" and results.get("candidates"):
            top_result_name = results["candidates"][0].get("name", "")
            print(f"DEBUG: Top result name from Google: '{top_result_name}'")

            similarity_score = fuzz.token_set_ratio(company_name.lower(), top_result_name.lower())
            print(f"DEBUG: Fuzzy match score between '{company_name}' and '{top_result_name}': {similarity_score}%")

            if similarity_score > 85:
                print("DEBUG: Match SUCCESSFUL (Similarity > 85%)")
                print("="*50 + "\n")
                return True, f"High-confidence name match found: '{top_result_name}'"
            else:
                print("DEBUG: Match FAILED (Similarity <= 85%)")
                print("="*50 + "\n")
                return False, f"A business was found, but the name '{top_result_name}' is not a close match."
        else:
            print(f"DEBUG: Google API returned status '{results.get('status')}' with no results.")
            print("="*50 + "\n")
            return False, f"No business found on Google Maps. (API Status: {results.get('status')})"

    except Exception as e:
        print(f"DEBUG: An exception occurred: {e}")
        print("="*50 + "\n")
        return False, f"Google API error: {e}"
# ==============================================================================
# FINAL, SCORING LOGIC
# ==============================================================================
def verify_address(company_name, address, user_ip):
    """
    Builds a confidence score from zero based on the quality of evidence.
    """
    confidence_score = 0
    findings = []

    # 1. Google Places Name Match (Highest Weight: 70 points)
    is_name_match, gmaps_reason = verify_with_google_places(company_name, address)
    if is_name_match:
        confidence_score += 70
        note = f"{gmaps_reason}. (+70 points)"
    else:
        note = gmaps_reason
    findings.append({"source": "Google Places Name Match", "note": note})

    # 2. Government Website Search (Strong Supporting Evidence: 25 points)
    gov_results = google_search(f'"{company_name}" "{address}"', GOV_CX)
    if gov_results:
        confidence_score += 25
        note = "Company and address found on a trusted government source. (+25 points)"
        findings.append({"source": "Government Domain Search", "note": note, "evidence_url": gov_results[0].get('link')})
    
    # 3. General Web Search (Low Supporting Evidence: 5 points)
    general_results = google_search(f'"{company_name}" "{address}"', GENERAL_CX)
    if general_results:
        confidence_score += 5
        note = "Company and address mentioned on the general web. (+5 points)"
        findings.append({"source": "General Web Search", "note": note, "evidence_url": general_results[0].get('link')})
        
    # 4. IP Geolocation Check (Small Bonus: 5 points)
    try:
        geocode_result = gmaps.geocode(address)
        ip_location = geocoder.ip('me' if user_ip == '127.0.0.1' else user_ip)
        if geocode_result and ip_location.ok:
            business_coords = (geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng'])
            distance_km = geodesic(business_coords, ip_location.latlng).kilometers
            if distance_km <= 200:
                confidence_score += 5
                note = f"User's IP is within 200km of business. (+5 points)"
                findings.append({"source": "IP Geolocation", "note": note})
    except Exception:
        pass

    final_score = min(confidence_score, 100) # Cap the score at 100
    
    return {
        "company_name": company_name,
        "address": address,
        "confidence_score": final_score,
        "findings": findings
    }
    
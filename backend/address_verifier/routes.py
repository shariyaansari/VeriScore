# address_verifier/routes.py
from flask import Blueprint, request, jsonify
from .parser import parse_full_address

# Create a 'Blueprint' - a way to organize a group of related routes
api = Blueprint('api', __name__)

@api.route('/verify', methods=['POST'])
def verify_address():
    # Get the JSON data sent from the frontend
    data = request.get_json()
    if not data or 'address' not in data:
        return jsonify({"error": "Address not provided"}), 400

    raw_address = data['address']
    
    # Call your main parser function from parser.py
    structured_data = parse_full_address(raw_address)
    
    # Send the structured JSON back to the frontend
    return jsonify(structured_data)
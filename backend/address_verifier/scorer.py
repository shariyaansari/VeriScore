# # # address_verifier/scorer.py

# # def calculate_confidence_score(structured_address):
# #     """
# #     Calculates a confidence score based on the available address components.
# #     This is a simplified version for the address parsing feature.
# #     """
# #     score = 0
    
# #     # Rule 1: Pincode is mandatory for a basic score
# #     if structured_address.get("pincode"):
# #         score += 40
# #     else:
# #         # If there's no pincode, the address is not very useful.
# #         return 0

# #     # Rule 2: Landmarks and Sectors add high confidence
# #     if structured_address.get("landmark"):
# #         score += 30
# #     if structured_address.get("sector_block_info"):
# #         score += 30

# #     # Rule 3: Detailed house info is a good sign
# #     if structured_address.get("house_building_info"):
# #         # Simple check: longer house info is probably more detailed
# #         if len(structured_address["house_building_info"]) > 10:
# #             score += 20
            
# #     # Cap the score at 100
# #     return min(score, 100)
# # address_verifier/routes.py
# from flask import Blueprint, request, jsonify, current_app
# import time
# from .verifier import verify_address # <-- The ONLY import you need for verification

# api = Blueprint('api', __name__)

# @api.route('/verify', methods=['POST'])
# def verify_endpoint():
#     user_ip = request.remote_addr
#     data = request.get_json()

#     if not data or "company_name" not in data or "address" not in data:
#         return jsonify({"error": "Missing company_name or address"}), 400

#     company = data["company_name"]
#     address = data["address"]
    
#     # --- 1. Call the correct verification logic from verifier.py ---
#     result = verify_address(company, address, user_ip)
    
#     # --- 2. Save the result for the dashboard ---
#     score = result['confidence_score']
#     result_to_save = {
#         "id": len(current_app.verifications_db) + 1,
#         "address": f"{company}, {address}",
#         "status": "verified" if score >= 80 else "suspicious" if score >= 40 else "rejected",
#         "confidence": score / 100.0,
#         "timestamp": time.time()
#     }
#     current_app.verifications_db.append(result_to_save)
    
#     # --- 3. Return the detailed verification result to the frontend ---
#     return jsonify(result)

# @api.route('/dashboard-stats', methods=['GET'])
# def get_dashboard_stats():
#     db = current_app.verifications_db
#     total = len(db)
#     verified = sum(1 for v in db if v['status'] == 'verified')
#     suspicious = sum(1 for v in db if v['status'] == 'suspicious')
#     rejected = sum(1 for v in db if v['status'] == 'rejected')
#     rate = (verified / total * 100) if total > 0 else 0
    
#     recent = sorted(db, key=lambda x: x['timestamp'], reverse=True)[:5]

#     stats = {
#         "total_verifications": total, "verified_count": verified,
#         "suspicious_count": suspicious, "rejected_count": rejected,
#         "verification_rate": rate, "recent_verifications": recent
#     }
#     return jsonify(stats)
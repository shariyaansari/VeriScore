# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from address_verifier.parser import parse_full_address
# from address_verifier.scorer import calculate_confidence_score
# import time
# from address_verifier import create_app
# verifications_db = []

# # This creates the app instance and runs all the setup inside create_app()
# app = create_app()



# def create_app():
#     app = Flask(__name__)
#     CORS(app)

#     @app.route('/api/verify', methods=['POST'])
#     def verify_address():
#         data = request.get_json()
#         if not data or 'address' not in data:
#             return jsonify({"error": "Address not provided"}), 400

#         raw_address = data['address']
        
#         # --- Existing Logic ---
#         structured_data = parse_full_address(raw_address)
#         score = calculate_confidence_score(structured_data)
#         structured_data['confidence_score'] = score
        
#         # --- NEW: Save the result to our "database" ---
#         result_to_save = {
#             "id": len(verifications_db) + 1,
#             "address": raw_address,
#             "status": "verified" if score > 80 else "suspicious" if score > 40 else "rejected",
#             "confidence": score / 100.0,
#             "timestamp": time.time()
#         }
#         verifications_db.append(result_to_save)
#         # ---------------------------------------------
        
#         return jsonify(structured_data)

#     # --- NEW: Dashboard Endpoint ---
#     @app.route('/api/dashboard-stats', methods=['GET'])
#     def get_dashboard_stats():
#         total_verifications = len(verifications_db)
#         verified_count = sum(1 for v in verifications_db if v['status'] == 'verified')
#         suspicious_count = sum(1 for v in verifications_db if v['status'] == 'suspicious')
#         rejected_count = sum(1 for v in verifications_db if v['status'] == 'rejected')
        
#         verification_rate = (verified_count / total_verifications * 100) if total_verifications > 0 else 0
        
#         # Sort verifications by timestamp to get the most recent ones
#         recent_verifications = sorted(verifications_db, key=lambda x: x['timestamp'], reverse=True)[:5]

#         stats = {
#             "total_verifications": total_verifications,
#             "verified_count": verified_count,
#             "suspicious_count": suspicious_count,
#             "rejected_count": rejected_count,
#             "verification_rate": verification_rate,
#             "recent_verifications": recent_verifications
#         }
#         return jsonify(stats)
#     # ---------------------------

#     return app

# # This block runs the server when you execute "python app.py"
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)

# app.py
from address_verifier import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
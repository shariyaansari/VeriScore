# address_verifier/routes.py
from flask import Blueprint, request, jsonify, current_app
import time
from .verifier import verify_address
from flask import send_file
from fpdf import FPDF
import io
from bson import ObjectId  # Import ObjectId for MongoDB document lookup
# Add this at the top with the other imports if it's not there
from flask import jsonify 
import requests 

api = Blueprint('api', __name__)

# @api.route('/verify', methods=['POST'])
# def verify_endpoint():
#     user_ip = request.remote_addr
#     data = request.get_json()

#     if not data or "company_name" not in data or "address" not in data:
#         return jsonify({"error": "Missing company_name or address"}), 400

#     company = data["company_name"]
#     address = data["address"]
    
#     result = verify_address(company, address, user_ip)
    
#     # Get a reference to the database from the current app
#     db = current_app.db
    
#     score = result['confidence_score']
#     verification_doc = {
#         "company_name": company,
#         "address": address,
#         "confidence_score": score,
#         "status": "verified" if score >= 80 else "suspicious" if score >= 40 else "rejected",
#         "timestamp": time.time(),
#         "lat": result.get("lat"),
#         "lng": result.get("lng"),
#         "findings": result.get("findings")
#     }
#     # Use the db object to insert into the 'verifications' collection
#     db.verifications.insert_one(verification_doc)
    
#     return jsonify(result)
@api.route('/verify', methods=['POST'])
def verify_endpoint():
    user_ip = request.remote_addr
    data = request.get_json()

    if not data or "company_name" not in data or "address" not in data:
        return jsonify({"error": "Missing company_name or address"}), 400

    company = data["company_name"]
    address = data["address"]
    
    # 1. Run the main verification logic
    result = verify_address(company, address, user_ip)
    
    # 2. Save the result to the database
    db = current_app.db
    score = result['confidence_score']
    verification_doc = { "company_name": company, "address": address, "confidence_score": score, "status": "verified" if score >= 80 else "suspicious" if score >= 40 else "rejected", "timestamp": time.time(), "lat": result.get("lat"), "lng": result.get("lng"), "findings": result.get("findings") }
    inserted_result = db.verifications.insert_one(verification_doc)
    
    # Add the final ID to the response
    result['id'] = str(inserted_result.inserted_id)
    
    # --- 3. WEBHOOK LOGIC ---
    webhook_url = data.get("webhook_url")
    if webhook_url and "http" in webhook_url: # Basic check for a valid URL
        try:
            # Send the final result to the user's webhook URL
            requests.post(webhook_url, json=result, timeout=5)
            print(f"✅ Sent webhook to: {webhook_url}")
        except Exception as e:
            # Don't crash if the webhook fails
            print(f"❌ Webhook failed: {e}")
    # ---------------------------
    
    # 4. Return the result to the frontend
    return jsonify(result)

@api.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    # Get a reference to the database from the current app
    db = current_app.db
    
    total = db.verifications.count_documents({})
    verified = db.verifications.count_documents({"status": "verified"})
    suspicious = db.verifications.count_documents({"status": "suspicious"})
    rejected = db.verifications.count_documents({"status": "rejected"})
    rate = (verified / total * 100) if total > 0 else 0
    
    recent_verifications_cursor = db.verifications.find().sort("timestamp", -1).limit(5)
    
    recent = []
    for v in recent_verifications_cursor:
        recent.append({
            "id": str(v['_id']),
            "address": f"{v['company_name']}, {v['address']}",
            "confidence": v['confidence_score'] / 100.0,
            "status": v['status'],
            "timestamp": v['timestamp'],
            "lat": v.get('lat'),
            "lng": v.get('lng')
        })

    stats = {
        "total_verifications": total, "verified_count": verified,
        "suspicious_count": suspicious, "rejected_count": rejected,
        "verification_rate": rate, "recent_verifications": recent
    }
    return jsonify(stats)

@api.route('/get-report/<string:verification_id>', methods=['GET'])
def get_verification_report(verification_id):
    db = current_app.db
    try:
        # Find the verification result in MongoDB using its ObjectId
        verification = db.verifications.find_one({"_id": ObjectId(verification_id)})
    except Exception:
        return jsonify({"error": "Invalid verification ID format"}), 400

    if not verification:
        return jsonify({"error": "Verification not found"}), 404

    # --- PDF Generation Logic ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Verification Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Company: {verification.get('company_name')}", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, f"Address: {verification.get('address')}")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Final Confidence Score: {verification.get('confidence_score')}%", ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Findings Breakdown:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for finding in verification.get('findings', []):
        pdf.multi_cell(0, 6, f"- {finding.get('source')}: {finding.get('note')}")

    # --- Create and return the downloadable file ---
    pdf_buffer = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'VeriScore_Report_{verification_id}.pdf'
    )

# Add this new function with the other @api.route definitions
@api.route('/')
def index():
    return jsonify({"status": "ok", "message": "VeriScore API is running!"})
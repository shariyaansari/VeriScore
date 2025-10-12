# # address_verifier/__init__.py
# from flask import Flask, jsonify  # <-- Make sure jsonify is imported here
# from flask_cors import CORS
# from dotenv import load_dotenv

# def create_app():
#     # 1. Load environment variables from .env file FIRST.
#     load_dotenv() 
    
#     app = Flask(__name__)
#     CORS(app)

#     # 2. Initialize your in-memory "database"
#     app.verifications_db = []

#     # 3. Import and register your API routes under the /api prefix
#     from .routes import api
#     app.register_blueprint(api, url_prefix='/api')

#     ## --- NEW CODE STARTS HERE --- ##

#     # 4. Define a simple route for the server's root URL
#     @app.route('/')
#     def index():
#         # This message will now appear at http://127.0.0.1:5000/
#         return jsonify({"status": "ok", "message": "VeriScore API is running!"})
        
#     ## --- NEW CODE ENDS HERE --- ##

#     return app

# address_verifier/__init__.py
# address_verifier/__init__.py
# address_verifier/__init__.py
# address_verifier/__init__.py
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

def create_app():
    load_dotenv() 
    app = Flask(__name__)
    CORS(app)

    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        client.admin.command('ismaster')
        # This now gets the database connection from the client
        app.db = client.get_database() 
        print(f"✅ Successfully connected to MongoDB database: '{app.db.name}'")
    except Exception as e:
        print(f"❌ FAILED to connect to MongoDB. Error: {e}")

    from .routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app
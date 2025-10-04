# app.py
from flask import Flask
from flask_cors import CORS
from address_verifier.routes import api

def create_app():
    app = Flask(__name__)
    
    # IMPORTANT: Enable CORS to allow your friend's frontend to call your API
    CORS(app)
    
    # Register your API routes from routes.py
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    # host='0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)
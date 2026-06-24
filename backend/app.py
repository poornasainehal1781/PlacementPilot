import os
import sys

# Add parent folder of backend to sys.path to allow importing backend module when run from any folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.config import Config
from backend.database import db, init_db_fallback
from backend.routes.auth import auth_bp
from backend.routes.resume import resume_bp
from backend.routes.analysis import analysis_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.chat import chat_bp

def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure SQLAlchemy URI from env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/ai_resume_analyzer")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_override:
        app.config.update(config_override)

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize JWT Manager
    jwt = JWTManager(app)
    
    # Register JWT error handlers for clean API responses
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "The token has expired", "sub_status": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Signature verification failed", "sub_status": "token_invalid"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Request does not contain an access token", "sub_status": "token_missing"}), 401

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resume_bp, url_prefix='/api/resumes')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    # Initialize Database with automatic creation & SQLite fallback
    init_db_fallback(app)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "database": app.config['SQLALCHEMY_DATABASE_URI'].split("://")[0]}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    # Standard run
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)

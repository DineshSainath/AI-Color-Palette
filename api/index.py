import os
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for DATABASE_URL and log connection type
database_url = os.getenv('DATABASE_URL', '')
if database_url:
    # Replace postgres:// with postgresql:// if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        os.environ['DATABASE_URL'] = database_url
    
    # Check if using Supavisor
    parsed_url = urlparse(database_url)
    hostname = parsed_url.hostname
    is_supavisor = 'pooler.supabase.com' in hostname if hostname else False
    
    logger.info(f"Database connection configured. Using Supavisor: {is_supavisor}")
    logger.info(f"Database host: {hostname}")
else:
    logger.warning("No DATABASE_URL environment variable found")

try:
    from app import app as flask_app
    logger.info("Flask app imported successfully")
except Exception as e:
    logger.error(f"Error importing Flask app: {str(e)}")
    # Create a minimal app for error reporting
    from flask import Flask, jsonify
    flask_app = Flask(__name__)
    
    @flask_app.route('/', defaults={'path': ''})
    @flask_app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            "status": "error",
            "message": "Application initialization failed",
            "error": str(e),
            "database_configured": bool(database_url),
            "using_supavisor": is_supavisor if 'is_supavisor' in locals() else False
        }), 500

# Set debug to False for production
flask_app.debug = False

# Initialize the API handler
app = flask_app
logger.info("API handler initialized") 
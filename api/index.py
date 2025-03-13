import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix PostgreSQL connection string if needed
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    os.environ['DATABASE_URL'] = database_url.replace('postgres://', 'postgresql://', 1)

# Import the Flask app
from app import app

# This is necessary for Vercel serverless functions
app.debug = False

# Export the app as a handler for Vercel 
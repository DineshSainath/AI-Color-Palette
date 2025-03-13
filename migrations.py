import os
from flask_migrate import Migrate, init, migrate, upgrade
from app import app, db
from models import User, Palette

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    # Check if migrations directory exists
    if not os.path.exists('migrations'):
        print("Initializing migrations directory...")
        with app.app_context():
            init()
    
    # Generate migration
    print("Generating migration...")
    with app.app_context():
        migrate()
    
    # Apply migration
    print("Applying migration...")
    with app.app_context():
        upgrade()
    
    print("Migration complete!") 
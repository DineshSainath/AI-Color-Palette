import os
from dotenv import load_dotenv
from app import app, db
from models import User, Palette

# Load environment variables
load_dotenv()

# Check if DATABASE_URL is set
if not os.getenv('DATABASE_URL'):
    print("Error: DATABASE_URL environment variable is not set.")
    print("Please set it to your Supabase connection string.")
    exit(1)

print("Connecting to database...")
print(f"Database URL: {os.getenv('DATABASE_URL')[:20]}...")

# Create all tables
with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    # List all tables
    print("\nCreated tables:")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        
print("\nDatabase setup complete!") 
#!/bin/bash

echo "Running Vercel build script..."

# Install dependencies
pip install -r requirements.txt

# Run database setup
python setup_db.py

echo "Build script completed." 
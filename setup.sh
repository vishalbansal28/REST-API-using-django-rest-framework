#!/bin/bash

# Setup script for initializing the project

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Run the server
echo "Running the server..."
python manage.py runserver

from app import create_app
import os

# Create Flask app using your existing factory function
app = create_app()

# Vercel requires the WSGI application to be named 'app'
app = app
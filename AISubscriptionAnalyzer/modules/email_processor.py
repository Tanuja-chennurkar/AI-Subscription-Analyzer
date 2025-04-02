import os
import cv2
import pytesseract
from flask import current_app
from google.oauth2 import service_account

def process_screen_time(email):
    # Implementation from your email_api.py
    # Modified to use current_app.config for credentials
    # Returns dict: {'Netflix': 120, 'Spotify': 50...}
    
    # Sample implementation
    return {
        'Netflix': 120,
        'Spotify': 50,
        'Swiggy': 0,
        'WhatsApp': 90
    }
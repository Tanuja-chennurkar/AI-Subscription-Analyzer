import imaplib
import email
import re
import pandas as pd
from bs4 import BeautifulSoup
from flask import current_app

def fetch_subscriptions(user_email):
    # Implementation from Subscription_Extraction.py
    # Modified to use app config for credentials
    # Returns raw subscription data
    
    # Sample implementation
    return [
        {
            'Platform': 'Netflix',
            'Total (INR)': 199,
            'Usage': 120,
            'Duration': 'Monthly'
        },
        {
            'Platform': 'Spotify',
            'Total (INR)': 59,
            'Usage': 50,
            'Duration': 'Monthly'
        }
    ]
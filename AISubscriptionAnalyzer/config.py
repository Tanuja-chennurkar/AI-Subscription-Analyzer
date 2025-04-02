import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

# Mail configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'anweshaghoshisthebest@gmail.com'
MAIL_PASSWORD = 'tnauwuanztjpjvjb'
MAIL_DEFAULT_SENDER = 'anweshaghoshisthebest@gmail.com'
import os
from dotenv import load_dotenv
from .base import base

load_dotenv()

class development(base):
    DEBUG = os.environ.get('FLASK_DEBUG')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///dev.db'
    

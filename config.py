from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Float, TEXT

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///books.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

IMAGE_DIR = 'static/images/covers'

INDEX_PAGE_TITLE = "Mrunal's Book Tracker"
INDEX_PAGE_HEADER = "Mrunal's Books"

# Google Books API key
with open("googlebooksapikey", "r") as f:
    GOOGLE_API_KEY = f.read().strip()

BOOK_STATUSES = {
    'Currently Reading': 'Currently Reading',
    'Planning to Read': 'Planning to Read',
    'Read': 'Read'
}

DISABLED = ['intro_vid']

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Fields to capture
FIELDS = {
    "title": String(150),
    "authors": String(150),
    "cover": String(400),
    "cover_path": String(400),
    "status": String(50),
    "current_page": Integer,
    "pageCount": Integer,
    "averageRating": Float,
    "industryIdentifiers": TEXT,
    "is_favorite": Integer,
    "is_enabled": Integer,
    "description": String(500)
}

import os
import json
import requests
from sqlalchemy import String, Integer, Float, TEXT
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session
from config import (db,
                    GOOGLE_API_KEY,
                    BOOK_STATUSES,
                    FIELDS,
                    INDEX_PAGE_TITLE,
                    INDEX_PAGE_HEADER,
                    DISABLED,
                    IMAGE_DIR
                    )

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"
app.config['PERMANENT_SESSION_LIFETIME'] = True
# Initialize the SQLAlchemy app context and make IMG dir
db.init_app(app)
os.makedirs(IMAGE_DIR, exist_ok=True)


# Create the Book model dynamically
def create_book_model():
    # Create a dictionary for the fields to be used in the model
    book_fields = {
        'id': db.Column(db.Integer, primary_key=True)
    }

    # Add fields defined in the FIELDS dictionary
    for field_name, field_type in FIELDS.items():
        book_fields[field_name] = db.Column(field_type, nullable=True)

    # Create a dynamic class for the Book model
    Book = type('Book', (db.Model,), book_fields)

    return Book


# Create the model
Book = create_book_model()

# Create the database tables
with app.app_context():
    db.create_all()


# TODO: Improve Handling and make this work
@app.route('/books/api/intro_vid')
def serve_intro_video():
    # Disabled for now
    if 'intro_vid' in DISABLED:
        return ''
    if not session.get("video_played"):
        print("Video not played - serving intro video.")
        return send_from_directory('static', 'intro.mp4')
    else:
        print("Video already played - not serving video.")
        return '', 204


@app.route('/books/api/export_db')
def export_db():
    return send_from_directory('instance', 'books.db')


# Route for getting book cover
@app.route('/books/api/get_book_cover/<int:book_id>', methods=['GET', 'POST'])
def get_book_cover(book_id):
    get_all_covers()
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    cover_path = book.cover_path if book.cover_path else book.cover

    if cover_path and os.path.exists(cover_path):
        return send_from_directory(IMAGE_DIR, f"{book_id}.png")
    else:
        file_path = os.path.join(IMAGE_DIR, f"{book.id}.png")
        if save_cover_image(book.cover, file_path):
            return send_from_directory(IMAGE_DIR, f"{book_id}.png")
        else:
            return jsonify({"error": "Cover image not found"}), 404


@app.route("/books/api/video_played", methods=["POST"])
def video_played():
    session["video_played"] = True
    session.modified = True
    return '', 204


@app.route('/books')
def index():
    get_all_covers()
    show_video = not session.get("video_played", False)

    # Fetch and categorize books by status
    categorized_books = {
        status: Book.query.filter_by(status=status, is_enabled=1).all()
        for status in BOOK_STATUSES.values()
    }

    # Fetch favorite books
    fav_books = Book.query.filter_by(is_favorite=1, is_enabled=1).all()

    return render_template(
        'index.html',
        categorized_books=categorized_books,
        statuses=BOOK_STATUSES,
        page_title=INDEX_PAGE_TITLE,
        page_header=INDEX_PAGE_HEADER,
        fav_books=fav_books,
        show_video=show_video
    )


# Define a function to handle value casting
def cast_value(value, field_type):
    # Check the type using equality comparison
    if field_type == String:
        return str(value) if value is not None else None
    elif field_type == Integer:
        return int(value) if value is not None else None
    elif field_type == Float:
        return float(value) if value is not None else None
    elif field_type == TEXT:
        if isinstance(value, list):
            return json.dumps(value)
        return str(value) if value is not None else None
    return value  # Default return if type doesn't match


# Route for adding a book
@app.route('/books/api/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        status = request.form.get('status')

        # Search for the book using Google Books API
        books_info = search_google_books(title)

        if books_info:
            return render_template('select_book.html', books=books_info, status=status)

    return render_template('add_book.html', statuses=BOOK_STATUSES)


@app.route('/books/api/confirm_add_book', methods=['POST'])
def confirm_add_book():
    # Get the book information from the form, which is passed as JSON
    book_info = request.form.get('book_info')
    status = request.form.get('status')

    # Load book info from the JSON string
    book_info = json.loads(book_info)

    # Create a new book with dynamic fields

    new_book = Book(status=status)
    new_book.is_enabled = 1

    # Populate the book fields dynamically from the book_info
    for field, field_type in FIELDS.items():
        if field in book_info:
            value = book_info[field]
            value = cast_value(value, field_type)
            setattr(new_book, field, value)

    db.session.add(new_book)
    db.session.commit()
    get_all_covers()
    return redirect(url_for('index'))


# Route for updating a book's fields
@app.route('/books/api/update/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        # Update the book's fields from the form dynamically
        for field in FIELDS.keys():
            current_value = getattr(book, field)
            new_value = cast_value(request.form.get(field), type(current_value))
            # Only update if the value has changed
            if new_value != current_value:
                print(f"Updated: {field} {new_value}")
                setattr(book, field, new_value)
            if new_value == "":
                new_value = None
        # Handle the cover image upload
        cover_image = request.files.get('cover_image')
        if cover_image and (cover_image.filename.endswith('.png') or cover_image.filename.endswith('.jpg') or cover_image.filename.endswith('.jpeg')):
            cover_path = os.path.join(IMAGE_DIR, f"{book_id}.png")
            cover_image.save(cover_path)
            book.cover_path = cover_path

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update_book.html', book=book, statuses=BOOK_STATUSES)



@app.route('/books/api/toggle_favorite/<int:book_id>', methods=['POST'])
def toggle_favorite(book_id):
    book = Book.query.get_or_404(book_id)
    book.is_favorite = 1 if book.is_favorite == 0 else 0  # Toggle favorite status
    db.session.commit()
    return jsonify(success=True, is_favorite=book.is_favorite)


@app.route('/books/api/get_info')
def get_info():
    book = request.args.get('book')
    if book:
        return search_google_books(book, True)
    else:
        return 'No book parameter provided.'


# Google Books API search function
def search_google_books(title, raw_json=False):
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if raw_json:
            return data
        if 'items' in data:
            books_info = []
            # Build the book info dictionary dynamically for each book
            for item in data['items']:
                book = item['volumeInfo']
                book_info = {}
                for field in FIELDS.keys():
                    if field == "authors":
                        book_info[field] = ', '.join(book.get("authors", []))
                    elif field == "cover":
                        image_links = book.get("imageLinks", {})
                        book_info[field] = image_links.get("thumbnail")
                        if book_info[field] is not None:
                            book_info[field] = book_info[field].replace("zoom=1", "zoom=10")
                            book_info[field] = book_info[field].replace("http:", "https:")
                        print(book_info[field])
                    elif field in book:
                        book_info[field] = book[field]
                books_info.append(book_info)
            return books_info
    return None


@app.route('/books/api/test')
def testresponsetime():
    return "Here"


def get_all_covers():
    books_missing_covers = Book.query.filter(Book.cover_path == None, Book.cover != None).all()
    print(books_missing_covers)
    for book in books_missing_covers:
        cover_url = book.cover
        # Ensure cover URL exists
        if cover_url:
            # Construct file path with the book ID
            file_path = os.path.join(IMAGE_DIR, f"{book.id}.png")
            # Attempt to save the cover image and update cover_path if successful
            if save_cover_image(cover_url, file_path):
                book.cover_path = file_path
                db.session.add(book)
                print(f"Cover downloaded for book ID {book.id} at {file_path}")
            else:
                print(f"Failed to download cover for book ID {book.id}")

    db.session.commit()
    print("Cover paths updated for all books with missing covers.")


def save_cover_image(cover_url, file_path):
    response = requests.get(cover_url)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
        return False


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7777)

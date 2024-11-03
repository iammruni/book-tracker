# Book Tracker

Welcome to my Book Tracker! This simple tool helps me keep track of my reading journey, even if I sometimes spend more time on it than actually reading the books!

## Features

- **Search for Books**: Utilize the Google Books API to find and add your preferred titles.
- **Custom Book Covers**: Personalize your collection by adding custom book covers.
- **Reading Progress**: Keep track of the current page you're reading.
- **Favorites**: Mark your favorite books.
- **Custom Categories**: Organize your books into categories that suit your needs.
- **Easy Integration**: Add new fields from the Google Books API with minimal effort.
- **Customization**: Easily modify the layout and features to fit your preferences.

## Installation

1. **Get an API Key**: Sign up for a Google Books API key (they offer 1,000 free requests per day). Save this key in a file named `googlebooksapikey` (place it next to `app.py` without an extension).
2. **Install Requirements**: Install the necessary packages:
   - `flask`
   - `flask_sqlalchemy`
   - `sqlalchemy`
   - `requests`
3. **Customize Your App**: Modify the web page's title, header, and categories in `config.py`:
   ![Front Page](/README_IMGS/6.png)
4. **Run the Application**: That's it! Start the app by running `app.py`.

## Screenshots

![Front Page](/README_IMGS/1.png)
*Snippet of the main page*

![Categories](/README_IMGS/2.png)
*The main page displays all your books in their respective categories, like "Planning to Read" shown here.*  
*Psst! You can create custom categories by simply adding them in the `config.py` file.*

![Adding a New Book](/README_IMGS/3.png)
*Interface for adding a new book*

![Select a Book](/README_IMGS/4.png)
*After searching for a book on the "Add New Book" screen, you’ll see a list of options to choose from for adding to your database.*

![Updating Book Info](/README_IMGS/5.png)
*Easily update a book's information when needed*

## Miscellaneous
![Adding Extra Fields](/README_IMGS/7.png)
*This dictionary contains custom fields along with fields from the [Google Books API response](https://developers.google.com/books/docs/v1/reference/volumes). When adding a new field here, make sure it is also defined in the database. This ensures that it will be captured and stored in the database each time a new book is added.*

from flask import Flask, render_template, request, session, redirect
from pymongo import MongoClient
import os


app = Flask(__name__)
app.secret_key = "your-secret-key"  # Set a secret key for session management

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['library_management']
users_collection = db['users']
books_collection = db['books']

# Define route for home page
@app.route('/')
def home():
    return render_template('index.html')


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        uploaded_id = None
        if 'id' in request.files:
            id_file = request.files['id']
            if id_file.filename != '':
                uploaded_id = id_file.read()
        
        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'uploaded_id': uploaded_id
        }
        
        users_collection.insert_one(user_data)
        return redirect('/login')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username and password are valid
        # (Replace this with your own authentication logic)
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = username
            return redirect('/books')  # Redirect to books page after successful login
        
        # If the username and password are not valid, show an error message
        error_message = 'Invalid username or password'
        return render_template('login.html', error_message=error_message)
    
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/login')




# Route for adding new books
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        
        book_data = {
            'title': title,
            'author': author,
            'available': True
        }
        
        books_collection.insert_one(book_data)
        return redirect('/books')
    
    return render_template('add_book.html')


# Route for issuing a book
@app.route('/issue_book', methods=['POST'])
def issue_book():
    book_title = request.form['book_title']
    user_id = request.form['user_id']
    
    book = books_collection.find_one({'title': book_title})
    if book and book['available']:
        books_collection.update_one({'title': book_title}, {'$set': {'available': False, 'issued_to': user_id}})
    
    return redirect('/books')

# Route for returning a book
@app.route('/return_book', methods=['POST'])
def return_book():
    book_title = request.form['book_title']
    
    book = books_collection.find_one({'title': book_title})
    if book and not book['available']:
        books_collection.update_one({'title': book_title}, {'$set': {'available': True, 'issued_to': None}})
    
    return redirect('/books')



# Route for searching books
@app.route('/search', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        book_title = request.form['book_title']
        book = books_collection.find_one({'title': book_title})
        if book:
            if book['available']:
                message = 'Book is available'
            else:
                message = 'Book is checked out'
        else:
            message = 'Book not found'
        return render_template('search.html', message=message)
    
    return render_template('search.html')



# Route for updating a user
@app.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.form['user_id']
    new_username = request.form['new_username']
    new_email = request.form['new_email']
    
    users_collection.update_one({'_id': user_id}, {'$set': {'username': new_username, 'email': new_email}})
    return redirect('/users')

# Route for removing a user
@app.route('/remove_user', methods=['POST'])
def remove_user():
    user_id = request.form['user_id']
    users_collection.delete_one({'_id': user_id})
    return redirect('/users')

# Route for updating a book
@app.route('/update_book', methods=['POST'])
def update_book():
    book_title = request.form['book_title']
    new_title = request.form['new_title']
    new_author = request.form['new_author']
    
    books_collection.update_one({'title': book_title}, {'$set': {'title': new_title, 'author': new_author}})
    return redirect('/books')

# Route for removing a book
@app.route('/remove_book', methods=['POST'])
def remove_book():
    book_title = request.form['book_title']
    books_collection.delete_one({'title': book_title})
    return redirect('/books')


# Route for viewing users
@app.route('/users')
def view_users():
    users = users_collection.find()
    return render_template('view_users.html', users=users)

# Route for viewing books
@app.route('/books')
def view_books():
    books = books_collection.find()
    return render_template('view_books.html', books=books)




if __name__ == '__main__':
    app.run(debug=True)

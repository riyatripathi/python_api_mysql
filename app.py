from flask_jwt_extended import JWTManager
from flask import Flask, request, jsonify
import datetime
import mysql.connector
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from jwt.exceptions import InvalidTokenError as JWTError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdef'  # Change this to a strong secret key
jwt = JWTManager(app)

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='python_api'
)
cursor = db.cursor()

@app.errorhandler(JWTError)
def handle_invalid_token(error):
    response = {
        'message': 'Invalid token',
        'error': str(error)
    }
    return jsonify(response), 401


# Login API
@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    # Validate email existence in the database
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'Invalid email or password'}), 401

    # Perform password validation (you may want to use a more secure method like hashing and salting)
    if user[2] != password:
        return jsonify({'message': 'Invalid email or password'}), 401

    # Generate a JWT token
    access_token = create_access_token(identity={"email": email, "userId": user[0]})
    return jsonify(access_token = access_token), 200
    
    # return jsonify({'token': token.decode('UTF-8')}), 200


# List of Books API
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    token = request.headers.get('Authorization')
    token = token.split(' ')[1]

    if not token:
        return jsonify({'message': 'Missing token'}), 401

    current_user_id = get_jwt_identity()
    print(current_user_id)
    email = current_user_id['email']
    userId = current_user_id['userId']

    print(email, userId)

    # Perform database query to fetch the list of books
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()

    book_list = []
    for book in books:
        book_dict = {
            'id': book[0],
            'title': book[1],
            'author': book[2]
        }
        book_list.append(book_dict)

    return jsonify({'books': book_list}), 200


if __name__ == '__main__':
    app.run()

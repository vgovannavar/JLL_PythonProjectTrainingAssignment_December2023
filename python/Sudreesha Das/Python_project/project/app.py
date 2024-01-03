from flask import Flask, render_template, request, jsonify
import csv
import json
from fpdf import FPDF
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sudreesha@21'
app.config['MYSQL_DB'] = 'PythonProject'
mysql = MySQL(app)
# Route for the registration form
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Get the form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
        data = {
            'name': username,
            'email': email,
            'password': password
            # ... add other form fields
        }
        json_data = json.dumps(data)

        # Write JSON data to a file
        with open('data.json', 'w') as file:
            file.write(json_data)

        return 'Registration Successful'
    return render_template('register.html', msg = msg)
        
        # Convert the data to JSON
        

# Route for the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Get the form data
        username = request.form['username']
        password = request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'

        return 'Login Successful'
    return render_template('login.html', msg = msg)

# Route to generate PDF from JSON or CSV data
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Get the data from the file
    with open('data.json', 'r') as file:
        json_data = json.load(file)

    # Generate PDF using FPDF library
    pdf = FPDF()
    pdf.add_page()
    # ... your PDF template and content generation logic here
    pdf.output('bill.pdf')

    return 'PDF generated'

if __name__ == '__main__':
    app.run()
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'g@ceta' 

def get_db_connection():
    conn = sqlite3.connect('SIMS.db')
    conn.row_factory = sqlite3.Row  
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['password']

        conn = get_db_connection()
        users = conn.execute("SELECT * FROM USERS WHERE uname = ? AND password = ?", (uname, password)).fetchone()
        conn.close()

        if users:
            session['uname'] = users['uname']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        idno = request.form['idno']
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        midname = request.form['midname']
        course = request.form['course']
        yearlvl = request.form['yearlvl']
        email = request.form['email']
        uname = request.form['uname']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM USERS WHERE uname = ?", (uname,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))
        
        # Insert user into database
        cursor.execute("""
            INSERT INTO USERS (userId, lastname, firstname, midname, course, yearlvl, email, uname, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (idno, lastname, firstname, midname, course, yearlvl, email, uname, password))
        conn.commit()
        conn.close()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/')
@app.route('/index')
def index():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    return render_template('index.html')  # Load the main dashboard


if __name__ == "__main__":
    app.run(debug=True)

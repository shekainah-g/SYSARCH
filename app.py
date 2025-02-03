import sqlite3, os

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        users = conn.execute("SELECT * FROM USERS WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        
        if users:
            session['user_id'] = users['id']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # if 'user_id' in session:
    #     session.pop('user_id', None)
    #     flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

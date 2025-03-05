from flask import Flask, render_template, request, redirect, url_for, session, flash
import dbhelper

app = Flask(__name__)
app.secret_key = 'g@ceta' 


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['password']

        user = dbhelper.get_users(uname, password) 
        
        if user:
            print(f"User {user['uname']} logged in successfully!") 
            session['uname'] = user['uname']
            return redirect(url_for('information'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/logout", methods=["POST"])
def logout():
    """Secure logout route using POST request"""
    session.clear()  # Clears all session data
    return redirect(url_for("login"))  # Redirect to the login page


@app.route('/dashboard')
def dashboard():
    if 'uname' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))  # Redirect if not logged in

    user = dbhelper.get_user_details(session['uname'])  # Get user details

    if not user:
        flash("User not found!", "error")
        return redirect(url_for("login"))

    return render_template('dashboard.html', user=user)


@app.route('/information')
def information():
    if 'uname' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))  


    user = dbhelper.get_user_info(session['uname'])  

    if not user:
        flash("User not found!", "error")
        return redirect(url_for("login"))

    return render_template('information.html', user=user) 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userId = request.form['idno']
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        midname = request.form['midname']
        course = request.form['course']
        yearlvl = request.form['yearlvl']
        email = request.form['email']
        uname = request.form['uname']
        password = request.form['password']
        

        default_profile_pic = "profile.jpg"  

        
        existing_user = dbhelper.register_user(
            userId, lastname, firstname, midname, course, yearlvl, email, uname, password, default_profile_pic
        )
        
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/labrules')
def labrules():
    
    return render_template('labrules.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'uname' not in session:
        return redirect(url_for('login'))
    
    user = dbhelper.get_user_info(session['uname'])  # Fetch user details from the database

    if request.method == 'POST':
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        midname = request.form.get('midname', '')  # Optional field
        course = request.form['course']
        yearlvl = request.form['yearlvl']
        email = request.form['email']
        password = request.form.get('password', '') 
        
        file = request.files.get("profile_pic")  # Use .get() to avoid errors

        filename = user['profile_pic']  # Default to existing profile pic

        if file and file.filename != "":  
            filename = file.filename  
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))  # Save file in static/uploads/

        # Update the database with new filename
        dbhelper.update_user(session['uname'], lastname, firstname, midname, 
                             course, yearlvl, email, password, filename)

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('information'))

    return render_template('edit.html', user=user)

    

@app.route('/index')
def index():
    if 'uname' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))  

    return render_template('index.html') 


if __name__ == "__main__":
    app.run(debug=True)

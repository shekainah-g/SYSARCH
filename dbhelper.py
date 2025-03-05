import sqlite3

DATABASE = "SIMS.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn   

def get_users(uname, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM USERS WHERE uname = ? AND password = ?", (uname, password)).fetchone() 
    conn.close()
    
    print("DEBUG: Retrieved user ->", user) 
    return user  

def register_user(userId, lastname, firstname, midname, course, yearlvl, email, uname, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    existing_user = cursor.execute("SELECT * FROM USERS WHERE uname = ?", (uname,)).fetchone()
    
    if existing_user:
        conn.close()
        return True 
    
    cursor.execute("""
                INSERT INTO USERS (userId, lastname, firstname, midname, course, yearlvl, email, uname, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (userId, lastname, firstname, midname, course, yearlvl, email, uname, password))
    conn.commit()
    conn.close()
    
    return False

def get_user_info(uname):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE uname = ?", (uname,)).fetchone()
    conn.close()
    return user

def update_user(uname, lastname, firstname, midname, course, yearlvl, email, password, profile_pic):
    conn = get_db_connection()
    cursor = conn.cursor()

    if password:
        cursor.execute("""
            UPDATE users 
            SET lastname = ?, firstname = ?, midname = ?, course = ?, 
                yearlvl = ?, email = ?, password = ?, profile_pic = ?
            WHERE uname = ?
        """, (lastname, firstname, midname, course, yearlvl, email, password, profile_pic, uname))
    else:
        cursor.execute("""
            UPDATE users 
            SET lastname = ?, firstname = ?, midname = ?, course = ?, 
                yearlvl = ?, email = ?, profile_pic = ?
            WHERE uname = ?
        """, (lastname, firstname, midname, course, yearlvl, email, profile_pic, uname))

    conn.commit()
    conn.close()
    return True


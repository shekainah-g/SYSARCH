import sqlite3
from datetime import datetime, timedelta

DATABASE = "SIMS.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn   

def get_users(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the user is an admin
        cursor.execute("""
            SELECT admin_id, username, role 
            FROM admins 
            WHERE username = ? AND password = ?
        """, (username, password))
        admin = cursor.fetchone()
        
        if admin:
            conn.close()
            return {
                "role": "admin",
                "data": {
                    "id": admin[0],
                    "username": admin[1],
                    "role": admin[2]
                }
            }
        
        # Check if the user is a student
        cursor.execute("""
            SELECT id, username, firstname, lastname, role, 
                   remaining_sessions, course, yearlvl
            FROM users 
            WHERE username = ? AND password = ?
        """, (username, password))
        student = cursor.fetchone()
        
        conn.close()
        
        if student:
            return {
                "role": "student",
                "data": {
                    "id": student[0],
                    "username": student[1],
                    "firstname": student[2],
                    "lastname": student[3],
                    "role": student[4],
                    "remaining_sessions": student[5],
                    "course": student[6],
                    "yearlvl": student[7]
                }
            }
        return None
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        return None

def register_user(id, username, password, firstname, lastname, midname, email, role, course, yearlvl):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            if existing_user[0] == username:
                return "Username already exists"
            else:
                return "Email already exists"
        
        # Set initial sessions based on course
        initial_sessions = 30 if course == "BSIT" else 15
        
        # Insert new user with both username and id
        cursor.execute("""
            INSERT INTO users (
                id, password, firstname, lastname, midname, username, email, role, 
                remaining_sessions, course, yearlvl, profile_pic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
        """, (id, password, firstname, lastname, midname, username, email, role, 
              initial_sessions, course, yearlvl, "profile.jpg"))
        
        conn.commit()
        conn.close()
        return "Registration successful"
    except Exception as e:
        print(f"Error in register_user: {e}")
        return "Registration failed"

def get_user_info(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to find user by ID first
        cursor.execute("""
            SELECT id, username, firstname, lastname, email, course, yearlvl, remaining_sessions, profile_pic
            FROM users 
            WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        
        # If not found by ID, try username
        if not user:
            cursor.execute("""
                SELECT id, username, firstname, lastname, email, course, yearlvl, remaining_sessions, profile_pic
                FROM users 
                WHERE username = ?
            """, (user_id,))
            user = cursor.fetchone()
        
        conn.close()
        
        if user:
            # If profile_pic is None or empty, use default profile picture
            profile_pic = user[8] if user[8] and user[8] != "profile.jpg" else "profile.jpg"
            
            return {
                "id": user[0],
                "username": user[1],
                "firstname": user[2],
                "lastname": user[3],
                "email": user[4],
                "course": user[5],
                "yearlvl": user[6],
                "remaining_sessions": user[7],
                "profile_pic": profile_pic
            }
        return None
    except Exception as e:
        print(f"Error in get_user_info: {str(e)}")
        return None

def student_record(uname):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, firstname, lastname, email, role, 
                   remaining_sessions, course, yearlvl, profile_pic
            FROM users 
            WHERE username = ?
        """, (uname,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'firstname': user[2],
                'lastname': user[3],
                'email': user[4],
                'role': user[5],
                'remaining_sessions': user[6],
                'course': user[7],
                'yearlvl': user[8],
                'profile_pic': user[9]
            }
        return None
    except Exception as e:
        print(f"Error getting student record: {e}")
        return None

def update_user(username, lastname, firstname, midname, course, yearlvl, email, password, profile_pic=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if password:
            # Update with new password
            cursor.execute("""
                UPDATE users 
                SET lastname = ?, firstname = ?, midname = ?, 
                    course = ?, yearlvl = ?, email = ?, password = ?,
                    profile_pic = COALESCE(?, profile_pic)
                WHERE username = ?
            """, (lastname, firstname, midname, course, yearlvl, email, password, profile_pic, username))
        else:
            # Update without changing password
            cursor.execute("""
                UPDATE users 
                SET lastname = ?, firstname = ?, midname = ?, 
                    course = ?, yearlvl = ?, email = ?,
                    profile_pic = COALESCE(?, profile_pic)
                WHERE username = ?
            """, (lastname, firstname, midname, course, yearlvl, email, profile_pic, username))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in update_user: {str(e)}")
        return False

def create_announcement(announcement, date_created):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
                INSERT INTO announcements (announcement, date_created)
                VALUES (?, ?)
            """, (announcement, date_created))
    conn.commit()
    conn.close()
    
    return True

def get_announcements():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
                SELECT * FROM announcements 
                ORDER BY date_created DESC
            """)
    announcements = cursor.fetchall()
    
    conn.close()
    return announcements

def get_student_by_id_or_name(query):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"Debug - Searching for student with query: {query}")
        
        # Search by ID, username, firstname, or lastname
        cursor.execute("""
            SELECT id, username, firstname, lastname, course, yearlvl, remaining_sessions
            FROM users 
            WHERE id = ? 
               OR username LIKE ? 
               OR firstname LIKE ? 
               OR lastname LIKE ?
            LIMIT 1
        """, (query, f'%{query}%', f'%{query}%', f'%{query}%'))
        
        student = cursor.fetchone()
        conn.close()
        
        if student:
            print(f"Debug - Found student: ID={student[0]}, Name={student[2]} {student[3]}, Sessions={student[6]}")
            return {
                "id": student[0],
                "username": student[1],
                "name": f"{student[2]} {student[3]}",
                "course": student[4],
                "yearlvl": student[5],
                "remaining_sessions": student[6]
            }
        print(f"Debug - No student found for query: {query}")
        return None
    except Exception as e:
        print(f"Error in get_student_by_id_or_name: {str(e)}")
        return None

def log_in_student(user_id, purpose, laboratory):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First get the student's full info to verify
        cursor.execute("""
            SELECT id, firstname, lastname, remaining_sessions 
            FROM users 
            WHERE CAST(id AS TEXT) = CAST(? AS TEXT)
        """, (user_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"Debug - Student not found with ID: {user_id}")
            return False, "Student not found"
            
        print(f"Debug - Student found: {student[1]} {student[2]} with {student[3]} sessions")
        
        if student[3] < 1:
            print(f"Debug - Student has insufficient sessions: {student[3]}")
            return False, "No remaining sessions"
        
        # Check if student is already logged in
        cursor.execute("SELECT id FROM current_sitins WHERE CAST(user_id AS TEXT) = CAST(? AS TEXT)", (user_id,))
        if cursor.fetchone():
            print(f"Debug - Student is already logged in")
            return False, "Student is already logged in"
        
        # Log in the student
        cursor.execute("""
            INSERT INTO current_sitins (user_id, time_in, purpose, laboratory)
            VALUES (?, datetime('now', 'localtime'), ?, ?)
        """, (user_id, purpose, laboratory))
        
        conn.commit()
        conn.close()
        return True, "Logged in successfully"
    except Exception as e:
        print(f"Error logging in student: {e}")
        return False, "Error logging in"

def log_out_student(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Debug: Print the user_id being logged out
        print(f"Logging out user_id: {user_id}")
        
        # Get the current sit-in record
        cursor.execute("""
            SELECT time_in, purpose, laboratory 
            FROM current_sitins 
            WHERE user_id = ? 
            ORDER BY time_in DESC 
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            print(f"No active session found for user_id: {user_id}")
            return False, "No active session found"
        
        time_in, purpose, laboratory = result
        print(f"Found active session - Time in: {time_in}, Purpose: {purpose}, Laboratory: {laboratory}")
        
        # Record the session in history
        cursor.execute("""
            INSERT INTO sit_in_history (user_id, time_in, time_out, purpose, laboratory)
            VALUES (?, ?, datetime('now', 'localtime'), ?, ?)
        """, (user_id, time_in, purpose, laboratory))
        
        # Debug: Print the last inserted row ID
        print(f"Recorded history with ID: {cursor.lastrowid}")
        
        # Remove from current sit-ins
        cursor.execute("DELETE FROM current_sitins WHERE user_id = ?", (user_id,))
        
        # Deduct one session
        cursor.execute("""
            UPDATE users 
            SET remaining_sessions = remaining_sessions - 1 
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        return True, "Logged out successfully"
    except Exception as e:
        print(f"Error logging out student: {e}")
        return False, "Error logging out"

def get_current_sitins():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                cs.user_id,
                u.firstname || ' ' || u.lastname as name,
                cs.purpose,
                cs.laboratory,
                strftime('%Y-%m-%d %H:%M:%S', cs.time_in) as time_in,
                u.points
            FROM current_sitins cs
            JOIN users u ON cs.user_id = u.id
            ORDER BY cs.time_in DESC
        """)
        
        sitins = cursor.fetchall()
        conn.close()
        
        return [{
            "student_id": sitin[0],
            "name": sitin[1],
            "purpose": sitin[2],
            "laboratory": sitin[3],
            "time_in": sitin[4],
            "points": sitin[5] if sitin[5] is not None else 0
        } for sitin in sitins]
    except Exception as e:
        print(f"Error in get_current_sitins: {e}")
        return []

def get_sit_in_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sh.user_id,
                u.firstname || ' ' || u.lastname as student_name,
                sh.purpose,
                sh.laboratory,
                strftime('%Y-%m-%d %H:%M:%S', sh.time_in) as time_in,
                strftime('%Y-%m-%d %H:%M:%S', sh.time_out) as time_out,
                f.feedback
            FROM sit_in_history sh
            JOIN users u ON sh.user_id = u.id
            LEFT JOIN feedbacks f ON sh.id = f.sitin_id
            ORDER BY sh.time_out DESC
        """)
        
        history = cursor.fetchall()
        conn.close()
        
        return [{
            "student_id": record[0],
            "student_name": record[1],
            "purpose": record[2],
            "laboratory": record[3],
            "time_in": record[4],
            "time_out": record[5],
            "feedback": record[6]
        } for record in history]
    except Exception as e:
        print(f"Error in get_sit_in_history: {e}")
        return []

def get_today_sit_in_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get today's sit-in history with student names and points from users table
        cursor.execute("""
            SELECT 
                h.id,
                u.id as student_id,
                u.firstname || ' ' || u.lastname as student_name,
                h.purpose,
                h.laboratory,
                h.time_in,
                h.time_out,
                u.points
            FROM sit_in_history h
            JOIN users u ON h.user_id = u.id
            WHERE DATE(h.time_out) = DATE('now', 'localtime')
            ORDER BY h.time_out DESC
        """)
        
        history = cursor.fetchall()
        
        # Format the results
        formatted_history = []
        for record in history:
            formatted_history.append({
                'id': record[0],
                'student_id': record[1],
                'student_name': record[2],
                'purpose': record[3],
                'laboratory': record[4],
                'time_in': record[5],
                'time_out': record[6],
                'points': record[7] if record[7] is not None else 0
            })
        
        conn.close()
        return formatted_history
        
    except Exception as e:
        print(f"Error getting today's history: {e}")
        return []

def get_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total students
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
        total_students = cursor.fetchone()[0]
        
        # Get active students (currently logged in)
        cursor.execute("SELECT COUNT(*) FROM current_sitins")
        active_students = cursor.fetchone()[0]
        
        # Get total sessions today
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sit_in_history 
            WHERE DATE(time_out) = DATE('now', 'localtime')
        """)
        total_sessions_today = cursor.fetchone()[0]

        # Get purpose-based statistics
        cursor.execute("""
            SELECT purpose, COUNT(*) as count 
            FROM current_sitins 
            GROUP BY purpose
        """)
        purpose_stats = cursor.fetchall()

        # Convert purpose stats to dictionary
        purpose_counts = {row[0]: row[1] for row in purpose_stats}
        
        # Get all possible purposes
        cursor.execute("SELECT DISTINCT purpose FROM current_sitins")
        all_purposes = [row[0] for row in cursor.fetchall()]
        
        # If no purposes found, use default categories
        if not all_purposes:
            all_purposes = ['Python', 'C#', 'Web Development', 'Other']
            purpose_counts = {purpose: 0 for purpose in all_purposes}

        conn.close()
        
        return {
            'total_students': total_students,
            'active_students': active_students,
            'total_sessions_today': total_sessions_today,
            'purpose_stats': purpose_counts,
            'all_purposes': all_purposes
        }
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_students': 0,
            'active_students': 0,
            'total_sessions_today': 0,
            'purpose_stats': {},
            'all_purposes': []
        }

def create_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create admins table first (no foreign key dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'admin'
            )
        ''')
        
        # Create users table (no foreign key dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                remaining_sessions INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                course TEXT,
                yearlvl TEXT,
                profile_pic TEXT
            )
        ''')
        
        # Insert default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO admins (username, password, role)
                VALUES (?, ?, ?)
            """, ('admin', 'admin123', 'admin'))
            print("Created default admin account")
        
        # Create computers table (no foreign key dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS computers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                computer_number TEXT NOT NULL,
                laboratory TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                UNIQUE(computer_number, laboratory)
            )
        ''')
        
        # Create current_sitins table (depends on users and computers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS current_sitins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                time_in DATETIME NOT NULL,
                purpose TEXT NOT NULL,
                laboratory TEXT NOT NULL,
                computer_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (computer_id) REFERENCES computers (id)
            )
        ''')
        
        # Create sit_in_history table (depends on users and computers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sit_in_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                time_in DATETIME NOT NULL,
                time_out DATETIME NOT NULL,
                purpose TEXT NOT NULL,
                laboratory TEXT NOT NULL,
                computer_id INTEGER,
                points INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (computer_id) REFERENCES computers (id)
            )
        ''')
        
        # Create reservations table (depends on users and computers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                laboratory TEXT NOT NULL,
                purpose TEXT NOT NULL,
                reservation_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                computer_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (computer_id) REFERENCES computers (id)
            )
        ''')
        
        # Create feedbacks table (depends on sit_in_history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sitin_id INTEGER NOT NULL,
                feedback TEXT NOT NULL,
                FOREIGN KEY (sitin_id) REFERENCES sit_in_history (id)
            )
        ''')
        
        # Create announcements table (no foreign key dependencies)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                announcement TEXT NOT NULL,
                date_created DATETIME NOT NULL
            )
        ''')
        
        # Create lab_schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lab_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                laboratory TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                subject TEXT NOT NULL,
                instructor TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                date_uploaded DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'reservation',
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Initialize computers if table is empty
        cursor.execute("SELECT COUNT(*) FROM computers")
        if cursor.fetchone()[0] == 0:
            print("Initializing computers...")
            laboratories = ['530', '540', '544', '542', '526']
            for lab in laboratories:
                print(f"Adding computers for laboratory {lab}")
                for i in range(1, 51):
                    computer_number = f"PC{i:02d}"
                    try:
                        cursor.execute("""
                            INSERT INTO computers (computer_number, laboratory, status)
                            VALUES (?, ?, 'available')
                        """, (computer_number, lab))
                        print(f"Added computer {computer_number} to laboratory {lab}")
                    except sqlite3.IntegrityError:
                        print(f"Computer {computer_number} already exists in laboratory {lab}")
                        continue
        
        conn.commit()
        conn.close()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise e

def get_all_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("""
            SELECT id, username, firstname, lastname, email, role, 
                   remaining_sessions, course, yearlvl, profile_pic
            FROM users 
            WHERE role = 'student'
            ORDER BY id DESC
        """)
        
        users = cursor.fetchall()
        
        # Get statistics for charts
        # Year level distribution
        cursor.execute("""
            SELECT yearlvl, COUNT(*) as count
            FROM users
            WHERE role = 'student'
            GROUP BY yearlvl
        """)
        year_stats = cursor.fetchall()
        
        # Course distribution
        cursor.execute("""
            SELECT course, COUNT(*) as count
            FROM users
            WHERE role = 'student'
            GROUP BY course
        """)
        course_stats = cursor.fetchall()
        
        # Purpose distribution from current sit-ins
        cursor.execute("""
            SELECT purpose, COUNT(*) as count
            FROM current_sitins
            GROUP BY purpose
        """)
        purpose_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "users": [{
                "id": user[0],
                "username": user[1],
                "firstname": user[2],
                "lastname": user[3],
                "email": user[4],
                "role": user[5],
                "remaining_sessions": user[6],
                "course": user[7],
                "yearlvl": user[8],
                "profile_pic": user[9]
            } for user in users],
            "year_stats": [{"year": stat[0], "count": stat[1]} for stat in year_stats],
            "course_stats": [{"course": stat[0], "count": stat[1]} for stat in course_stats],
            "purpose_stats": [{"purpose": stat[0], "count": stat[1]} for stat in purpose_stats]
        }
    except Exception as e:
        print(f"Error in get_all_users: {e}")
        return {"users": [], "year_stats": [], "course_stats": [], "purpose_stats": []}

def create_reservations_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                laboratory TEXT NOT NULL,
                purpose TEXT NOT NULL,
                reservation_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Reservations table created successfully")
    except Exception as e:
        print(f"Error creating reservations table: {e}")

def create_reservation(user_id, laboratory, purpose, reservation_date, start_time, end_time, computer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if computer is available
        cursor.execute("""
            SELECT status
            FROM computers
            WHERE id = ?
        """, (computer_id,))
        
        computer = cursor.fetchone()
        if not computer or computer[0] != 'available':
            return False, "Selected computer is not available"
        
        # Check for overlapping reservations
        cursor.execute("""
            SELECT COUNT(*) FROM reservations 
            WHERE laboratory = ? 
            AND reservation_date = ? 
            AND computer_id = ?
            AND (
                (start_time <= ? AND end_time > ?) OR
                (start_time < ? AND end_time >= ?) OR
                (start_time >= ? AND end_time <= ?)
            )
            AND status != 'rejected'
        """, (laboratory, reservation_date, computer_id, start_time, start_time, end_time, end_time, start_time, end_time))
        
        if cursor.fetchone()[0] > 0:
            return False, "Time slot already reserved for this computer"
        
        # Create new reservation
        cursor.execute("""
            INSERT INTO reservations (user_id, laboratory, purpose, reservation_date, start_time, end_time, computer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, laboratory, purpose, reservation_date, start_time, end_time, computer_id))
        
        conn.commit()
        conn.close()
        return True, "Reservation created successfully"
    except Exception as e:
        print(f"Error creating reservation: {e}")
        return False, "Error creating reservation"

def get_student_reservations(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, u.firstname, u.lastname, c.computer_number
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN computers c ON r.computer_id = c.id
            WHERE r.user_id = ?
            ORDER BY r.reservation_date DESC, r.start_time DESC
        """, (user_id,))
        
        reservations = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "laboratory": r[2],
            "purpose": r[3],
            "reservation_date": r[4],
            "start_time": r[5],
            "end_time": r[6],
            "computer_id": r[7],
            "status": r[8],
            "created_at": r[9],
            "student_name": f"{r[10]} {r[11]}",
            "computer_number": r[12] if r[12] else 'Not assigned'
        } for r in reservations]
    except Exception as e:
        print(f"Error getting student reservations: {e}")
        return []

def get_pending_reservations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, u.firstname, u.lastname, u.course, u.yearlvl
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE r.status = 'pending'
            ORDER BY r.created_at DESC
        """)
        
        reservations = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "user_id": r[1],
            "laboratory": r[2],
            "purpose": r[3],
            "reservation_date": r[4],
            "start_time": r[5],
            "end_time": r[6],
            "status": r[7],
            "created_at": r[8],
            "student_name": f"{r[9]} {r[10]}",
            "course": r[11],
            "yearlvl": r[12]
        } for r in reservations]
    except Exception as e:
        print(f"Error getting pending reservations: {e}")
        return []

def create_notification(user_id, message, notification_type='reservation'):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (user_id, message, type, is_read, created_at)
            VALUES (?, ?, ?, 0, datetime('now'))
        """, (user_id, message, notification_type))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        return False

def update_reservation_status(reservation_id, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get reservation details
        cursor.execute("""
            SELECT r.*, c.computer_number
            FROM reservations r
            LEFT JOIN computers c ON r.computer_id = c.id
            WHERE r.id = ?
        """, (reservation_id,))
        reservation = cursor.fetchone()
        
        if not reservation:
            return False, "Reservation not found"
        
        # Extract reservation data
        user_id = reservation[1]
        laboratory = reservation[2]
        purpose = reservation[3]
        computer_id = reservation[7]
        
        # Update reservation status
        cursor.execute("""
            UPDATE reservations
            SET status = ?
            WHERE id = ?
        """, (status, reservation_id))
        
        # If approved, add to current_sitins and update computer status
        if status == 'approved':
            # Check if student is already logged in
            cursor.execute("""
                SELECT id FROM current_sitins 
                WHERE user_id = ?
            """, (user_id,))
            
            if cursor.fetchone():
                conn.close()
                return False, "Student is already logged in"
            
            # Insert into current_sitins
            cursor.execute("""
                INSERT INTO current_sitins (user_id, time_in, purpose, laboratory, computer_id)
                VALUES (?, datetime('now', 'localtime'), ?, ?, ?)
            """, (user_id, purpose, laboratory, computer_id))
            
            # Update computer status to 'in_use'
            cursor.execute("""
                UPDATE computers
                SET status = 'in_use'
                WHERE id = ?
            """, (computer_id,))
        
        # Create notification
        computer_number = reservation[12] if len(reservation) > 12 else 'N/A'
        date = reservation[4]
        start_time = reservation[5]
        end_time = reservation[6]
        
        message = f"Your reservation for Lab {laboratory} (PC {computer_number}) on {date} from {start_time} to {end_time} has been {status}"
        if status == 'approved':
            message += " and you have been automatically logged in"
        
        cursor.execute("""
            INSERT INTO notifications (user_id, message, type, is_read, created_at)
            VALUES (?, ?, 'reservation', 0, datetime('now'))
        """, (user_id, message))
        
        conn.commit()
        conn.close()
        return True, f"Reservation {status} successfully"
    except Exception as e:
        print(f"Error updating reservation status: {e}")
        return False, str(e)

def get_available_time_slots(laboratory, date):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all reservations for the specified laboratory and date
        cursor.execute("""
            SELECT start_time, end_time 
            FROM reservations 
            WHERE laboratory = ? 
            AND reservation_date = ? 
            AND status != 'rejected'
            ORDER BY start_time
        """, (laboratory, date))
        
        reserved_slots = cursor.fetchall()
        conn.close()
        
        # Generate available time slots (assuming 8:00 AM to 5:00 PM)
        all_slots = []
        current_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")
        
        while current_time < end_time:
            slot_start = current_time.strftime("%H:%M")
            current_time = current_time + timedelta(hours=1)
            slot_end = current_time.strftime("%H:%M")
            
            # Check if this slot is available
            is_available = True
            for reserved in reserved_slots:
                reserved_start = datetime.strptime(reserved[0], "%H:%M")
                reserved_end = datetime.strptime(reserved[1], "%H:%M")
                slot_start_time = datetime.strptime(slot_start, "%H:%M")
                slot_end_time = datetime.strptime(slot_end, "%H:%M")
                
                if (slot_start_time < reserved_end and slot_end_time > reserved_start):
                    is_available = False
                    break
            
            if is_available:
                all_slots.append({
                    "start": slot_start,
                    "end": slot_end
                })
        
        return all_slots
    except Exception as e:
        print(f"Error getting available time slots: {e}")
        return []

def get_student_history(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get sit-in history with feedback and points
        cursor.execute("""
            SELECT 
                h.id,
                h.purpose,
                h.laboratory,
                h.time_in,
                h.time_out,
                h.points,
                f.feedback
            FROM sit_in_history h
            LEFT JOIN feedbacks f ON h.id = f.sitin_id
            WHERE h.user_id = ?
            ORDER BY h.time_out DESC
        """, (user_id,))
        
        history = cursor.fetchall()
        
        # Format the results
        formatted_history = []
        for record in history:
            formatted_history.append({
                'id': record[0],
                'purpose': record[1],
                'laboratory': record[2],
                'time_in': record[3],
                'time_out': record[4],
                'points': record[5],
                'feedback': record[6]
            })
        
        conn.close()
        return formatted_history
        
    except Exception as e:
        print(f"Error getting student history: {e}")
        return []

def add_feedback(sitin_id, user_id, feedback):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify the sit-in belongs to the user
        cursor.execute("""
            SELECT id FROM sit_in_history 
            WHERE id = ? AND user_id = ?
        """, (sitin_id, user_id))
        
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Add or update feedback
        cursor.execute("""
            INSERT OR REPLACE INTO feedbacks (sitin_id, feedback)
            VALUES (?, ?)
        """, (sitin_id, feedback))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in add_feedback: {e}")
        return False

def add_points(student_id, points_to_add):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get student's current sessions, course, and points
        cursor.execute("""
            SELECT remaining_sessions, course, points 
            FROM users 
            WHERE id = ?
        """, (student_id,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            return {"success": False, "message": "Student not found"}
            
        remaining_sessions = student[0]
        course = student[1]
        current_points = student[2] if student[2] is not None else 0
        
        # Calculate session limit based on course
        session_limit = 30 if course == "BSIT" else 15
        
        # Calculate total points after adding new points
        total_points = current_points + points_to_add
        
        # Calculate how many new sessions to add (1 session per 3 points)
        new_sessions = points_to_add // 3
        remaining_points = points_to_add % 3
        
        # Check if adding new sessions would exceed the limit
        if remaining_sessions + new_sessions > session_limit:
            conn.close()
            return {"success": False, "message": f"Cannot add points. Student has reached the maximum {session_limit} sessions."}
        
        # Update the student's sessions and points
        cursor.execute("""
            UPDATE users 
            SET remaining_sessions = remaining_sessions + ?,
                points = points + ?
            WHERE id = ?
        """, (new_sessions, points_to_add, student_id))
        
        # Update points in the most recent sit-in history record
        cursor.execute("""
            SELECT id 
            FROM sit_in_history 
            WHERE user_id = ? 
            ORDER BY time_out DESC 
            LIMIT 1
        """, (student_id,))
        
        recent_sitin = cursor.fetchone()
        if recent_sitin:
            cursor.execute("""
                UPDATE sit_in_history 
                SET points = points + ? 
                WHERE id = ?
            """, (points_to_add, recent_sitin[0]))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "message": f"Added {points_to_add} points. Converted {new_sessions} points to sessions. Total points: {total_points}"
        }
        
    except Exception as e:
        print(f"Error adding points: {e}")
        return {"success": False, "message": "Error adding points"}

def get_student_points(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT points 
            FROM sit_in_history 
            WHERE user_id = ? 
            ORDER BY time_out DESC 
            LIMIT 1
        """, (student_id,))
        
        result = cursor.fetchone()
        points = result[0] if result else 0
        
        conn.close()
        return points
        
    except Exception as e:
        print(f"Error getting student points: {e}")
        return 0

def update_existing_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if points column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'points' not in columns:
            # Add points column if it doesn't exist
            cursor.execute("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0")
            conn.commit()
            print("Added points column to users table")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating users table: {e}")
        return False

def get_top_students(limit=10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                u.id,
                u.firstname || ' ' || u.lastname as name,
                u.course,
                u.yearlvl,
                u.points,
                u.remaining_sessions
            FROM users u
            WHERE u.role = 'student'
            ORDER BY u.points DESC, u.remaining_sessions DESC
            LIMIT ?
        """, (limit,))
        
        students = cursor.fetchall()
        conn.close()
        
        return [{
            "id": student[0],
            "name": student[1],
            "course": student[2],
            "yearlvl": student[3],
            "points": student[4] if student[4] is not None else 0,
            "remaining_sessions": student[5]
        } for student in students]
    except Exception as e:
        print(f"Error getting top students: {e}")
        return []

def get_daily_sitins_stats(days=7):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(time_out) as date,
                COUNT(*) as count
            FROM sit_in_history
            WHERE DATE(time_out) >= DATE('now', ? || ' days')
            GROUP BY DATE(time_out)
            ORDER BY date ASC
        """, (f"-{days}",))
        
        stats = cursor.fetchall()
        conn.close()
        
        # Format dates and counts
        dates = []
        counts = []
        for stat in stats:
            dates.append(stat[0])
            counts.append(stat[1])
        
        return {
            "dates": dates,
            "counts": counts
        }
    except Exception as e:
        print(f"Error getting daily sit-ins stats: {e}")
        return {"dates": [], "counts": []}

def get_available_computers(laboratory, date, start_time, end_time):
    try:
        print(f"Debug - Getting available computers for lab {laboratory}, date {date}, time {start_time}-{end_time}")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert date to day of week
        cursor.execute("SELECT strftime('%w', ?)", (date,))
        day_number = cursor.fetchone()[0]
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        day_of_week = days[int(day_number)]
        
        print(f"Debug - Date {date} falls on {day_of_week}")
        
        # Check if the lab is scheduled for this time on this specific day of the week
        cursor.execute("""
            SELECT subject, instructor, start_time, end_time 
            FROM lab_schedules 
            WHERE laboratory = ? 
            AND day_of_week = ?
            AND (
                (start_time <= ? AND end_time > ?) OR
                (start_time < ? AND end_time >= ?) OR
                (start_time >= ? AND end_time <= ?)
            )
        """, (laboratory, day_of_week, start_time, start_time, end_time, end_time, start_time, end_time))
        
        schedule_conflict = cursor.fetchone()
        if schedule_conflict:
            conn.close()
            return {
                'available': False,
                'message': f"Lab {laboratory} is scheduled for {schedule_conflict[0]} with {schedule_conflict[1]} from {schedule_conflict[2]} to {schedule_conflict[3]} on {day_of_week}",
                'computers': []
            }
        
        # Get all computers in the laboratory
        cursor.execute("""
            SELECT id, computer_number, status
            FROM computers
            WHERE laboratory = ?
            ORDER BY computer_number
        """, (laboratory,))
        
        computers = cursor.fetchall()
        print(f"Debug - Found {len(computers)} computers in laboratory {laboratory}")
        
        # Get reserved computers for the time slot
        cursor.execute("""
            SELECT computer_id
            FROM reservations
            WHERE laboratory = ?
            AND reservation_date = ?
            AND (
                (start_time <= ? AND end_time > ?) OR
                (start_time < ? AND end_time >= ?) OR
                (start_time >= ? AND end_time <= ?)
            )
            AND status != 'rejected'
        """, (laboratory, date, start_time, start_time, end_time, end_time, start_time, end_time))
        
        reserved_computers = [row[0] for row in cursor.fetchall()]
        print(f"Debug - Found {len(reserved_computers)} reserved computers")
        
        # Get currently occupied computers
        cursor.execute("""
            SELECT computer_id
            FROM current_sitins
            WHERE laboratory = ?
        """, (laboratory,))
        
        occupied_computers = [row[0] for row in cursor.fetchall()]
        print(f"Debug - Found {len(occupied_computers)} occupied computers")
        
        # Format the result
        available_computers = []
        for computer in computers:
            is_available = (
                computer[0] not in reserved_computers and
                computer[0] not in occupied_computers and
                computer[2] == 'available'
            )
            available_computers.append({
                'id': computer[0],
                'computer_number': computer[1],
                'available': is_available
            })
        
        conn.close()
        print(f"Debug - Returning {len(available_computers)} computers")
        return {
            'available': len(available_computers) > 0,
            'message': f"Found {len(available_computers)} available computers" if available_computers else "No computers available for the selected time slot",
            'computers': available_computers
        }
    except Exception as e:
        print(f"Error in get_available_computers: {e}")
        return {
            'available': False,
            'message': f"Error checking availability: {str(e)}",
            'computers': []
        }

def create_lab_schedules_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                laboratory TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                subject TEXT NOT NULL,
                instructor TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating lab_schedules table: {e}")
        return False

def add_lab_schedule(laboratory, days, start_time, end_time, subject, instructor, description=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for schedule conflicts for each selected day
        for day in days:
            # Check conflicts with other lab schedules
            cursor.execute("""
                SELECT * FROM lab_schedules 
                WHERE laboratory = ? 
                AND day_of_week = ?
                AND (
                    (start_time <= ? AND end_time > ?) OR
                    (start_time < ? AND end_time >= ?) OR
                    (start_time >= ? AND end_time <= ?)
                )
            """, (laboratory, day, start_time, start_time, end_time, end_time, start_time, end_time))
            
            if cursor.fetchone():
                conn.close()
                return False, f"Schedule conflict detected with another lab schedule for {day}"
            
            # Check conflicts with existing reservations
            cursor.execute("""
                SELECT * FROM reservations 
                WHERE laboratory = ? 
                AND reservation_date = ?
                AND (
                    (start_time <= ? AND end_time > ?) OR
                    (start_time < ? AND end_time >= ?) OR
                    (start_time >= ? AND end_time <= ?)
                )
                AND status != 'rejected'
            """, (laboratory, day, start_time, start_time, end_time, end_time, start_time, end_time))
            
            if cursor.fetchone():
                conn.close()
                return False, f"Schedule conflict detected with existing reservations for {day}"
        
        # Add schedule for each selected day
        for day in days:
            cursor.execute("""
                INSERT INTO lab_schedules 
                (laboratory, day_of_week, start_time, end_time, subject, instructor, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (laboratory, day, start_time, end_time, subject, instructor, description))
        
        conn.commit()
        conn.close()
        return True, "Schedule added successfully"
    except Exception as e:
        print(f"Error adding lab schedule: {e}")
        return False, str(e)

def get_lab_schedules():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM lab_schedules 
            ORDER BY 
                CASE day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                END,
                start_time
        """)
        
        schedules = cursor.fetchall()
        conn.close()
        
        return [{
            'id': schedule[0],
            'laboratory': schedule[1],
            'day_of_week': schedule[2],
            'start_time': schedule[3],
            'end_time': schedule[4],
            'subject': schedule[5],
            'instructor': schedule[6],
            'description': schedule[7],
            'created_at': schedule[8]
        } for schedule in schedules]
    except Exception as e:
        print(f"Error getting lab schedules: {e}")
        return []

def delete_lab_schedule(schedule_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM lab_schedules WHERE id = ?", (schedule_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting lab schedule: {e}")
        return False

def is_lab_available(laboratory, day_of_week, time):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM lab_schedules 
            WHERE laboratory = ? 
            AND day_of_week = ?
            AND start_time <= ?
            AND end_time > ?
        """, (laboratory, day_of_week, time, time))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is None
    except Exception as e:
        print(f"Error checking lab availability: {e}")
        return False

def add_resource(title, description, filename, file_type):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resources (title, description, filename, file_type, date_uploaded)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (title, description, filename, file_type))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding resource: {e}")
        return False

def get_resources():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM resources
            ORDER BY date_uploaded DESC
        ''')
        resources = cursor.fetchall()
        conn.close()
        return resources
    except Exception as e:
        print(f"Error getting resources: {e}")
        return []
    
def get_resource_by_id(resource_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resources WHERE id = ?', (resource_id,))
        resource = cursor.fetchone()
        conn.close()
        return resource
    except Exception as e:
        print(f"Error fetching resource: {e}")
        return None

def delete_resource(resource_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM resources WHERE id = ?', (resource_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting resource: {e}")
        return False

def add_notification(user_id, message, type):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (user_id, message, type)
            VALUES (?, ?, ?)
        """, (user_id, message, type))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding notification: {e}")
        return False

def get_user_notifications(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, message, is_read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        notifications = cursor.fetchall()
        conn.close()
        
        return [{
            'id': n[0],
            'message': n[1],
            'read': bool(n[2]),
            'created_at': n[3]
        } for n in notifications]
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []

def mark_notification_read(notification_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = ?
        """, (notification_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return False

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'reservation',
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

def get_reservation_logs(filter_type='all', filter_value=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
        query = """
            SELECT 
                r.id,
                r.user_id,
                u.firstname || ' ' || u.lastname as student_name,
                u.course,
                u.yearlvl,
                r.laboratory,
                r.purpose,
                r.reservation_date,
                r.start_time,
                r.end_time,
                r.status,
                r.created_at,
                c.computer_number
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN computers c ON r.computer_id = c.id
            WHERE r.status = 'approved'
        """
        
        params = []
        
        # Add filters based on filter_type
        if filter_type == 'day' and filter_value:
            query += " AND DATE(r.reservation_date) = DATE(?)"
            params.append(filter_value)
        elif filter_type == 'month' and filter_value:
            query += " AND strftime('%Y-%m', r.reservation_date) = strftime('%Y-%m', ?)"
            params.append(filter_value)
        elif filter_type == 'year' and filter_value:
            query += " AND strftime('%Y', r.reservation_date) = strftime('%Y', ?)"
            params.append(filter_value)
        
        query += " ORDER BY r.reservation_date DESC, r.start_time DESC"
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        
        # Convert the results to a list of dictionaries
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'id': log[0],
                'user_id': log[1],
                'student_name': log[2],
                'course': log[3],
                'yearlvl': log[4],
                'laboratory': log[5],
                'purpose': log[6],
                'reservation_date': log[7],
                'start_time': log[8],
                'end_time': log[9],
                'status': log[10],
                'created_at': log[11],
                'computer_number': log[12] if log[12] else 'N/A'
            })
        
        return formatted_logs
    except Exception as e:
        print(f"Error getting reservation logs: {e}")
        return []

def get_filtered_schedules(laboratory=None, day=None, time=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
        query = """
            SELECT 
                laboratory,
                day_of_week,
                start_time,
                end_time,
                subject,
                instructor,
                description
            FROM lab_schedules
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if laboratory:
            query += " AND laboratory = ?"
            params.append(laboratory)
        
        if day:
            query += " AND day_of_week = ?"
            params.append(day)
        
        if time:
            if time == 'morning':
                query += " AND start_time >= '08:00' AND start_time < '12:00'"
            elif time == 'afternoon':
                query += " AND start_time >= '13:00' AND start_time < '17:00'"
        
        # Order by day and time
        query += """
            ORDER BY 
                CASE day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                END,
                start_time
        """
        
        cursor.execute(query, params)
        schedules = cursor.fetchall()
        conn.close()
        
        return [{
            'laboratory': schedule[0],
            'day_of_week': schedule[1],
            'start_time': schedule[2],
            'end_time': schedule[3],
            'subject': schedule[4],
            'instructor': schedule[5],
            'description': schedule[6]
        } for schedule in schedules]
        
    except Exception as e:
        print(f"Error getting filtered schedules: {e}")
        return []

def approve_reservation_and_sitin(reservation_id):
    """
    Approves a reservation and automatically creates a current sit-in record
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get reservation details with user and computer info
        cursor.execute("""
            SELECT r.*, u.firstname, u.lastname, c.computer_number, c.laboratory
            FROM reservations r 
            JOIN user u ON r.user_id = u.id 
            LEFT JOIN computers c ON r.computer_id = c.id 
            WHERE r.id = ? AND r.status = 'pending'
        """, (reservation_id,))
        
        reservation = cursor.fetchone()
        if not reservation:
            return {'success': False, 'message': 'Reservation not found or already processed'}
        
        # Extract data from reservation
        user_id = reservation[1]
        laboratory = reservation[2]
        purpose = reservation[3]
        computer_id = reservation[7]
        firstname = reservation[11]
        lastname = reservation[12]
        computer_number = reservation[13]
        student_name = f"{firstname} {lastname}"
        
        # Get current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Update reservation status to approved
        cursor.execute("""
            UPDATE reservations 
            SET status = 'approved' 
            WHERE id = ?
        """, (reservation_id,))
        
        # 2. Create current sit-in record in sitin_history
        cursor.execute("""
            INSERT INTO sitin_history (user_id, student_name, purpose, laboratory, time_in, computer_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, student_name, purpose, laboratory, current_time, computer_id))
        
        # 3. INSERT INTO current_sitins table
        cursor.execute("""
            INSERT INTO current_sitins (user_id, student_name, purpose, laboratory, time_in, computer_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, student_name, purpose, laboratory, current_time, computer_id))
        print("Inserted into current_sitins:", user_id, student_name, purpose, laboratory, current_time, computer_id)
        
        # 4. Update computer status to 'in_use' and set current user
        cursor.execute("""
            UPDATE computers 
            SET status = 'in_use', current_user = ?
            WHERE id = ?
        """, (student_name, computer_id))
        
        # 5. Deduct one session from user's remaining sessions
        cursor.execute("""
            UPDATE user 
            SET remaining_sessions = remaining_sessions - 1 
            WHERE id = ? AND remaining_sessions > 0
        """, (user_id,))
        
        # 6. Create notification for the student
        if 'create_notification' in globals():
            create_notification(user_id, 
                f"Your reservation for Lab {laboratory} PC {computer_number} has been approved and you have been automatically sat-in!", 
                'reservation_approved')
        
        conn.commit()
        return {
            'success': True, 
            'message': f'Reservation approved and student {student_name} automatically sat-in to Lab {laboratory} PC {computer_number}'
        }
        
    except Exception as e:
        print(f"Error in approve_reservation_and_sitin: {e}")
        conn.rollback()
        return {'success': False, 'message': f'Error processing reservation: {str(e)}'}
    finally:
        conn.close()

# Call this function after creating tables
create_tables()
update_existing_users()
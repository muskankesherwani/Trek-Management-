from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import date
from functools import wraps



# Role Based Access Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "staff":
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "user":
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



app = Flask(__name__)
app.secret_key = 'trek_management_secret_key'



connection = sqlite3.connect("trekking.db")
cursor = connection.cursor()

#TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trek_id INTEGER NOT NULL,
    booking_date TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(trek_id) REFERENCES trek(id)
)
""")
connection.commit()
connection.close()



# Login form
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection = sqlite3.connect("trekking.db")
        cursor = connection.cursor()
        #ADMIN LOGIN 
        if email == "admin@gmail.com" and password == "admin123":
            session["admin_id"] = 1
            session["role"] = "admin"
            connection.close()
            flash("Welcome Admin!", "success")
            return redirect("/admin/dashboard")
        #USER LOGIN
        cursor.execute("""
            SELECT id, password, status
            FROM user
            WHERE email = ?
        """, (email,))
        user = cursor.fetchone()
        if user and user[1] == password:
            if user[2] == "Blacklisted":
                connection.close()
                flash("Your account has been blacklisted.", "danger")
                return redirect("/login")
            session["user_id"] = user[0]
            session["role"] = "user"
            connection.close()
            flash("Login Successful!", "success")
            return redirect("/user/dashboard")
        # STAFF LOGIN 
        cursor.execute("""
            SELECT id, password, status
            FROM staff
            WHERE email = ?
        """, (email,))
        staff = cursor.fetchone()
        connection.close()
        if staff and staff[1] == password:
            if staff[2] == "Pending":
                flash("Your account is waiting for admin approval.", "warning")
                return redirect("/login")
            elif staff[2] == "Blacklisted":
                flash("Your account has been blacklisted.", "danger")
                return redirect("/login")
            else:
                session["staff_id"] = staff[0]
                session["role"] = "staff"
                flash("Welcome Staff!", "success")
                return redirect("/staff/dashboard")
#INVALID LOGIN
        flash("Invalid Email or Password.", "danger")
        return redirect("/login")
    return render_template("login.html")


          

#registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        address = request.form["address"]
        role = request.form["role"]
        connection = sqlite3.connect("trekking.db")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id
            FROM user
            WHERE email = ?
        """, (email,))
        user_exists = cursor.fetchone()
        cursor.execute("""
            SELECT id
            FROM staff
            WHERE email = ?
        """, (email,))
        staff_exists = cursor.fetchone()
        if user_exists or staff_exists:
            connection.close()
            return render_template(
                "register.html",
                error="This email is already registered."
            )
        if role == "User":
            cursor.execute("""
                INSERT INTO user
                (name, email, password, phone, address, status)
                VALUES (?, ?, ?, ?, ?, 'Active')
            """, (
                name,
                email,
                password,
                phone,
                address
            ))
        elif role == "Staff":
            cursor.execute("""
                INSERT INTO staff
                (name, email, password, phone, address, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (
                name,
                email,
                password,
                phone,
                address
            ))
        connection.commit()
        connection.close()
        return redirect("/login")
    return render_template("register.html")




#home
@app.route("/")
def home():
    return render_template("home.html")


#about
@app.route("/about")
def about():
    return render_template("about.html")


#contact
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        connection = sqlite3.connect("trekking.db")
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO contact_messages
            (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            subject,
            message
        ))
        connection.commit()
        connection.close()
        flash("Message sent successfully!", "success")
        return redirect("/contact")
    return render_template("contact.html")


#admin dashboard
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM staff")
    total_staff = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM trek")
    total_treks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM staff
        WHERE status='Pending'
    """)
    pending_staff = cursor.fetchone()[0]
    cursor.execute("""
        SELECT
            id,
            name,
            location,
            difficulty,
            status
        FROM trek
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_treks = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        pending_staff=pending_staff,
        recent_treks=recent_treks
    )


#ADMIN CONTACT
@app.route("/admin/contact-messages")
@admin_required
def admin_contact_messages():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            id,
            name,
            email,
            subject,
            message,
            created_at
        FROM contact_messages
        ORDER BY created_at DESC
    """)
    messages = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_contact_messages.html",
        messages=messages
    )


#Admin delete message route
@app.route("/admin/delete-message/<int:message_id>")
@admin_required
def delete_message(message_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM contact_messages
        WHERE id = ?
    """, (message_id,))
    connection.commit()
    connection.close()
    flash("Message deleted successfully!", "success")
    return redirect("/admin/contact-messages")


#admin treks
@app.route("/admin/treks")
@admin_required
def admin_treks():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    search = request.args.get("search")
    if search:
        cursor.execute("""
            SELECT *
            FROM trek
            WHERE
                name LIKE ?
                OR location LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))
    else:
        cursor.execute("""
            SELECT *
            FROM trek
            ORDER BY id DESC
        """)
    treks = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_treks.html",
        treks=treks
    )


#Admin users 
@app.route("/admin/users")
@admin_required
def admin_users():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            status
        FROM user
        ORDER BY id
    """)
    users = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_users.html",
        users=users
    )



#add trek
@app.route("/admin/treks/add", methods=["GET", "POST"])
@admin_required
def admin_treks_add():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        available_slots = request.form["available_slots"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        status = request.form["status"]
        description = request.form["description"]
        connection = sqlite3.connect("trekking.db")
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO trek
            (name, location, difficulty, duration, available_slots,
             start_date, end_date, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            location,
            difficulty,
            duration,
            available_slots,
            start_date,
            end_date,
            status,
            description
        ))
        connection.commit()
        print("Trek saved successfully!")
        print("Trek ID:", cursor.lastrowid)
        connection.close()
        return redirect("/admin/treks")
    return render_template("admin_treks_add.html")


#delete treks
@app.route("/admin/treks/delete/<int:id>")
@admin_required
def admin_delete_trek(id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM trek
        WHERE id = ?
    """, (id,))
    connection.commit()
    connection.close()
    return redirect("/admin/treks")


#edit trek
@app.route("/admin/edit/trek/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_trek(id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        available_slots = request.form["available_slots"]
        assigned_staff_id = request.form.get("assigned_staff_id")
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        status = request.form["status"]
        description = request.form["description"]
        cursor.execute("""
            UPDATE trek
            SET name = ?,
                location = ?,
                difficulty = ?,
                duration = ?,
                available_slots = ?,
                assigned_staff_id = ?,
                start_date = ?,
                end_date = ?,
                status = ?,
                description = ?
            WHERE id = ?
        """, (
            name,
            location,
            difficulty,
            duration,
            available_slots,
            assigned_staff_id,
            start_date,
            end_date,
            status,
            description,
            id
        ))
        connection.commit()
        connection.close()
        flash("Trek updated successfully!", "success")
        return redirect("/admin/treks")
    cursor.execute("""
        SELECT *
        FROM trek
        WHERE id = ?
    """, (id,))
    trek = cursor.fetchone()
    cursor.execute("""
        SELECT id, name
        FROM staff
        WHERE status = 'Approved'
    """)
    staff = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_edit_trek.html",
        trek=trek,
        staff=staff
    )






#blacklist
@app.route("/admin/staff/blacklist/<int:id>")
@admin_required
def blacklist_staff(id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE staff
        SET status = 'Blacklisted'
        WHERE id = ?
    """, (id,))
    connection.commit()
    connection.close()
    return redirect("/admin/staff")




# ADMIN APPROVE BOOKING
@app.route("/admin/approve/<int:booking_id>")
@admin_required
def admin_approve_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT trek_id
        FROM bookings
        WHERE id = ?
    """, (booking_id,))
    result = cursor.fetchone()
    if result is None:
        connection.close()
        flash("Booking not found.", "danger")
        return redirect("/admin/bookings")
    trek_id = result[0]
    cursor.execute("""
        UPDATE bookings
        SET status = 'Approved'
        WHERE id = ?
    """, (booking_id,))
    cursor.execute("""
        UPDATE trek
        SET available_slots = available_slots - 1
        WHERE id = ?
    """, (trek_id,))
    cursor.execute("""
        SELECT available_slots
        FROM trek
        WHERE id = ?
    """, (trek_id,))
    slots = cursor.fetchone()[0]
    if slots <= 0:
        cursor.execute("""
            UPDATE trek
            SET status = 'Closed'
            WHERE id = ?
        """, (trek_id,))

    connection.commit()
    connection.close()
    flash("Booking Approved Successfully!", "success")
    return redirect("/admin/bookings")



# ADMIN REJECT BOOKING
@app.route("/admin/reject/<int:booking_id>")
@admin_required
def admin_reject_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE bookings
        SET status = 'Rejected'
        WHERE id = ?
    """, (booking_id,))
    connection.commit()
    connection.close()
    flash("Booking Rejected.", "warning")
    return redirect("/admin/bookings")



# ADMIN COMPLETE BOOKING
@app.route("/admin/complete/<int:booking_id>")
@admin_required
def admin_complete_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE bookings
        SET status = 'Completed'
        WHERE id = ?
    """, (booking_id,))
    connection.commit()
    connection.close()
    flash("Booking Completed Successfully!", "success")
    return redirect("/admin/bookings")




#approve staff
@app.route("/admin/staff/approve/<int:id>")
@admin_required
def approve_staff(id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE staff
        SET status = 'Approved'
        WHERE id = ?
    """, (id,))
    connection.commit()
    connection.close()
    return redirect("/admin/staff")


# BLACKLIST USER
@app.route("/admin/blacklist-user/<int:user_id>")
@admin_required
def blacklist_user(user_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE user
        SET status='Blacklisted'
        WHERE id=?
    """, (user_id,))
    connection.commit()
    connection.close()
    return redirect("/admin/users")



# ACTIVATE USER
@app.route("/admin/activate-user/<int:user_id>")
@admin_required
def activate_user(user_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE user
        SET status='Active'
        WHERE id=?
    """, (user_id,))
    connection.commit()
    connection.close()
    return redirect("/admin/users")


# ADMIN MANAGE STAFF
@app.route("/admin/staff")
@admin_required
def admin_staff():
    status = request.args.get("status", "")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if status:
        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                status
            FROM staff
            WHERE status = ?
            ORDER BY id
        """, (status,))
    else:
        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                status
            FROM staff
            ORDER BY id
        """)
    staff = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_staff.html",
        staff=staff
    )




# ACTIVATE STAFF
@app.route("/admin/activate-staff/<int:staff_id>")
@admin_required
def activate_staff(staff_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE staff
        SET status='Active'
        WHERE id=?
    """, (staff_id,))
    connection.commit()
    connection.close()
    return redirect("/admin/staff")



#staff profile
@app.route("/staff/profile")
@staff_required
def staff_profile():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    staff_id = session.get("staff_id")
    if not staff_id:
        return redirect("/login")
    cursor.execute("""
        SELECT *
        FROM staff
        WHERE id = ?
    """, (staff_id,))
    staff = cursor.fetchone()
    connection.close()
    return render_template(
        "staff_profile.html",
        staff=staff
    )


# OPEN TREK
@app.route("/admin/open-trek/<int:trek_id>")
@admin_required
def open_trek(trek_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE trek
        SET status='Open'
        WHERE id=?
    """, (trek_id,))
    connection.commit()
    connection.close()
    return redirect("/admin/treks")



# CLOSE TREK
@app.route("/admin/close-trek/<int:trek_id>")
@admin_required
def close_trek(trek_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE trek
        SET status='Closed'
        WHERE id=?
    """, (trek_id,))
    connection.commit()
    connection.close()
    return redirect("/admin/treks")





#admin required 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect("/login")
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    status = request.args.get("status", "")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if status:
        cursor.execute("""
            SELECT
                bookings.id,
                user.name,
                trek.name,
                trek.location,
                bookings.booking_date,
                bookings.status
            FROM bookings
            JOIN user
                ON bookings.user_id = user.id
            JOIN trek
                ON bookings.trek_id = trek.id
            WHERE bookings.status = ?
            ORDER BY bookings.id DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT
                bookings.id,
                user.name,
                trek.name,
                trek.location,
                bookings.booking_date,
                bookings.status
            FROM bookings
            JOIN user
                ON bookings.user_id = user.id
            JOIN trek
                ON bookings.trek_id = trek.id
            ORDER BY bookings.id DESC
        """)
    bookings = cursor.fetchall()
    connection.close()
    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )




#staff dashboard
@app.route("/staff/dashboard")
@staff_required
def staff_dashboard():
    if "staff_id" not in session:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Approved'")
    approved = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Completed'")
    completed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]
    connection.close()
    return render_template(
        "staff_dashboard.html",
        pending=pending,
        approved=approved,
        completed=completed,
        rejected=rejected
    )


#staff trek
@app.route("/staff/trek")
@staff_required
def staff_trek():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM trek
        ORDER BY start_date
    """)
    treks = cursor.fetchall()
    connection.close()
    return render_template(
        "staff_trek.html",
        treks=treks
    )




# STAFF BOOKINGS
@app.route("/staff/bookings")
@staff_required
def staff_bookings():
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            bookings.id,
            user.name,
            trek.name,
            bookings.booking_date,
            bookings.status
        FROM bookings
        JOIN user
        ON bookings.user_id = user.id
        JOIN trek 
        ON bookings.trek_id = trek.id
    """)
    bookings = cursor.fetchall()
    connection.close()
    return render_template(
        "staff_bookings.html",
        bookings=bookings
    )


# STAFF APPROVE BOOKING
@app.route("/staff/approve/<int:booking_id>")
@staff_required
def approve_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE bookings
        SET status='Approved'
        WHERE id=?
    """, (booking_id,))
    # Get trek id of this booking
    cursor.execute("""
        SELECT trek_id
        FROM bookings
        WHERE id=?
    """, (booking_id,))
    trek_id = cursor.fetchone()[0]
    # Reduce available slots
    cursor.execute("""
        UPDATE trek
        SET available_slots = available_slots - 1
        WHERE id=?
    """, (trek_id,))
    # Check remaining slots
    cursor.execute("""
        SELECT available_slots
        FROM trek
        WHERE id=?
    """, (trek_id,))
    slots = cursor.fetchone()[0]
    # Close trek if no slots left
    if slots <= 0:
        cursor.execute("""
            UPDATE trek
            SET status='Closed'
            WHERE id=?
        """, (trek_id,))
    connection.commit()
    connection.close()
    flash("Booking Approved Successfully!", "success")
    return redirect("/staff/bookings")





# STAFF REJECT BOOKING
@app.route("/staff/reject/<int:booking_id>")
@staff_required
def reject_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE bookings
        SET status = 'Rejected'
        WHERE id = ?
    """, (booking_id,))
    connection.commit()
    connection.close()
    return redirect("/staff/bookings")


# STAFF COMPLETE BOOKING
@app.route("/staff/complete/<int:booking_id>")
@staff_required
def complete_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE bookings
        SET status = 'Completed'
        WHERE id = ?
    """, (booking_id,))
    connection.commit()
    connection.close()
    return redirect("/staff/bookings")

# STAFF CHANGE PASSWORD
@app.route("/staff/password-change", methods=["GET", "POST"])
@staff_required
def staff_password_change():
    staff_id = session.get("staff_id")
    if not staff_id:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        cursor.execute("""
            SELECT password
            FROM staff
            WHERE id = ?
        """, (staff_id,))
        db_password = cursor.fetchone()[0]
        if current_password != db_password:
            connection.close()
            return "Current password is incorrect."
        if new_password != confirm_password:
            connection.close()
            return "New Password and Confirm Password do not match."
        cursor.execute("""
            UPDATE staff
            SET password = ?
            WHERE id = ?
        """, (
            new_password,
            staff_id
        ))
        connection.commit()
        connection.close()
        return redirect("/staff/profile")
    connection.close()
    return render_template("staff_change_password.html")



# STAFF EDIT PROFILE
@app.route("/staff/profile/edit", methods=["GET", "POST"])
@staff_required
def edit_staff_profile():
    staff_id = session.get("staff_id")
    if not staff_id:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        cursor.execute("""
            UPDATE staff
            SET
                name = ?,
                email = ?,
                phone = ?
            WHERE id = ?
        """, (
            name,
            email,
            phone,
            staff_id
        ))
        connection.commit()
        connection.close()
        return redirect("/staff/profile")
    cursor.execute("""
        SELECT *
        FROM staff
        WHERE id = ?
    """, (staff_id,))
    staff = cursor.fetchone()
    connection.close()
    return render_template(
        "staff_edit_profile.html",
        staff=staff
    )



#user dashboard
@app.route("/user/dashboard")
@user_required
@user_required
def user_dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("user_dashboard.html")



# User trek
@app.route("/user/trek")
@user_required
def user_trek():
    search = request.args.get("search", "")
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            id,
            name,
            location,
            difficulty,
            duration,
            available_slots,
            start_date,
            end_date,
            status,
            description
        FROM trek
        WHERE name LIKE ?
        AND difficulty LIKE ?
        AND location LIKE ?
    """, (
        "%" + search + "%",
        "%" + difficulty + "%",
        "%" + location + "%"
    ))
    treks = cursor.fetchall()
    print("AVAILABLE SLOTS CHECK:")
    for trek in treks:
        print("Trek:", trek[1], "| Available Slots:", trek[5])
    connection.close()
    return render_template(
        "user_trek.html",
        treks=treks
    )



#user trek booking 
@app.route("/user/book/<int:trek_id>")
@user_required
def book_trek(trek_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    # Check whether user already booked this trek
    cursor.execute("""
        SELECT id
        FROM bookings
        WHERE user_id = ? AND trek_id = ?
    """, (session["user_id"], trek_id))
    existing_booking = cursor.fetchone()
    if existing_booking:
        connection.close()
        flash("You have already booked this trek.", "warning")
        return redirect(f"/user/trek/{trek_id}")
    # Create booking
    cursor.execute("""
        INSERT INTO bookings
        (user_id, trek_id, booking_date, status)
        VALUES (?, ?, CURRENT_TIMESTAMP, 'Pending')
    """, (session["user_id"], trek_id))
    connection.commit()
    connection.close()
    flash("Trek booked successfully!", "success")
    return redirect("/user/bookings")





# BOOKINGS HISTORY
@app.route("/user/bookings")
@user_required
def user_bookings():
    user_id = session.get("user_id")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            bookings.id,
            trek.name,
            trek.location,
            bookings.booking_date,
            trek.start_date,
            bookings.status
        FROM bookings
        JOIN trek
        ON bookings.trek_id = trek.id
        WHERE bookings.user_id = ?
        ORDER BY bookings.id DESC
    """, (user_id,))
    bookings = cursor.fetchall()
    connection.close()
    return render_template(
        "user_bookings.html",
        bookings=bookings
    )


# CANCEL USER BOOKING
@app.route("/user/cancel/<int:booking_id>")
@user_required
def cancel_booking(booking_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT trek_id
        FROM bookings
        WHERE id = ?
    """, (booking_id,))
    trek = cursor.fetchone()
    if trek:
        trek_id = trek[0]
        cursor.execute("""
            UPDATE bookings
            SET status='Cancelled'
            WHERE id=?
        """, (booking_id,))
        cursor.execute("""
            UPDATE trek
            SET available_slots = available_slots + 1
            WHERE id=?
        """, (trek_id,))
    connection.commit()
    connection.close()
    return redirect("/user/bookings")



# USER HISTORY
@app.route("/user/history")
@user_required
def user_history():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    # Total Bookings
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE user_id = ?
    """, (user_id,))
    total_bookings = cursor.fetchone()[0]
    # Completed Treks
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE user_id = ?
        AND status = 'Completed'
    """, (user_id,))
    completed = cursor.fetchone()[0]
    # Cancelled Bookings
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE user_id = ?
        AND status = 'Cancelled'
    """, (user_id,))
    cancelled = cursor.fetchone()[0]
    previous_treks = completed
    # Trekking History
    cursor.execute("""
        SELECT
            bookings.id,
            trek.name,
            trek.location,
            bookings.booking_date,
            trek.start_date,
            bookings.status
        FROM bookings
        JOIN trek
        ON bookings.trek_id = trek.id
        WHERE bookings.user_id = ?
        AND bookings.status IN ('Completed', 'Cancelled')
        ORDER BY bookings.id DESC
    """, (user_id,))
    history = cursor.fetchall()
    connection.close()
    return render_template(
        "user_history.html",
        history=history,
        total_bookings=total_bookings,
        completed=completed,
        cancelled=cancelled,
        previous_treks=previous_treks
    )


#User Profile 
@app.route("/user/profile")
@user_required
def user_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM user
        WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    connection.close()
    return render_template(
        "user_profile.html",
        user=user
    )



#edit user profile
@app.route("/user/profile/edit", methods=["GET", "POST"])
@user_required
def edit_user_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        cursor.execute("""
            UPDATE user
            SET
                name = ?,
                email = ?,
                phone = ?,
                address = ?
            WHERE id = ?
        """, (
            name,
            email,
            phone,
            address,
            user_id
        ))
        connection.commit()
        connection.close()
        return redirect("/user/profile")
    cursor.execute("""
        SELECT *
        FROM user
        WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    connection.close()
    return render_template(
        "user_edit_profile.html",
        user=user
    )


# User trek details
@app.route("/user/trek/<int:trek_id>")
@user_required
def trek_details(trek_id):
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        id,
        name,
        location,
        difficulty,
        duration,
        available_slots,
        start_date,
        end_date,
        status,
        description
    FROM trek
    WHERE id = ?
""", (trek_id,))
    trek = cursor.fetchone()
    connection.close()
    if trek is None:
        flash("Trek not found.", "danger")
        return redirect("/user/trek")
    return render_template(
        "user_trek_details.html",
        trek=trek
    )




#user password change
@app.route("/user/password-change", methods=["GET", "POST"])
@user_required
def user_password_change():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    connection = sqlite3.connect("trekking.db")
    cursor = connection.cursor()
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        cursor.execute("""
            SELECT password
            FROM user
            WHERE id = ?
        """, (user_id,))
        db_password = cursor.fetchone()[0]
        if current_password != db_password:
            connection.close()
            return "Current Password is incorrect."
        if new_password != confirm_password:
            connection.close()
            return "New Password and Confirm Password do not match."
        cursor.execute("""
            UPDATE user
            SET password = ?
            WHERE id = ?
        """, (
            new_password,
            user_id
        ))
        connection.commit()
        connection.close()
        return redirect("/user/profile")
    connection.close()
    return render_template("user_change_password.html")



#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")





#run application
if __name__ == "__main__":
    app.run(debug=True, use_reloader = False)








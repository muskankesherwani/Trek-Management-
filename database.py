import sqlite3

connection = sqlite3.connect("trekking.db")
cursor = connection.cursor()


# USER TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    role TEXT DEFAULT 'User',
    start_date DATETIME,
    end_date DATETIME,
    status TEXT DEFAULT 'Active'
)
""")

# Add status column if the old database does not have it
try:
    cursor.execute("""
    ALTER TABLE user
    ADD COLUMN status TEXT DEFAULT 'Active'
    """)
    print("User status column added.")
except sqlite3.OperationalError:
    print("User status column already exists.")

# STAFF TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    status TEXT DEFAULT 'Active'
)
""")


# TREK TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS trek (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    duration INTEGER,
    available_slots INTEGER,
    start_date DATETIME,
    end_date DATETIME,
    status TEXT,
    description TEXT,
    assigned_staff_id INTEGER,
    FOREIGN KEY (assigned_staff_id) REFERENCES staff(id)
)
""")

# Add assigned_staff_id if the old database does not have it
try:
    cursor.execute("""
    ALTER TABLE trek
    ADD COLUMN assigned_staff_id INTEGER
    """)
    print("assigned_staff_id column added.")
except sqlite3.OperationalError:
    print("assigned_staff_id column already exists.")



# BOOKINGS TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trek_id INTEGER NOT NULL,
    booking_date TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (trek_id) REFERENCES trek(id)
)
""")


# CONTACT MESSAGES TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# SAVE AND CLOSE

connection.commit()
connection.close()

print("Database created successfully!")




# Trek-Management-
the project will done by muskan kesherwani

# 🥾 Trekking Management Application

A web-based Trekking Management Application developed using **Python, Flask, SQLite, HTML, CSS, Bootstrap, and Jinja2**.

The application provides separate interfaces and role-based access for **Admin, Staff, and Users**. Users can explore treks, search and filter available treks, make bookings, and manage their profiles. Staff can manage bookings, while Admin can manage users, staff, treks, and contact messages.

---

## 📌 Features

### 👤 User

- User registration and login
- User profile management
- Browse available treks
- Search treks by name
- Filter treks by difficulty
- Search treks by location
- View detailed trek information
- Check available slots
- Book a trek
- View booking status
- Contact the trekking management team
- Logout functionality

### 🧑‍💼 Staff

- Staff registration
- Admin approval required for staff accounts
- Staff login
- Staff dashboard
- View user bookings
- Approve pending bookings
- Reject bookings
- Complete approved bookings
- View trek-related information
- Role-based access control

### 🛠️ Admin

- Admin login
- Admin dashboard
- View total users
- View total staff
- View total treks
- View total bookings
- Review pending staff registrations
- Approve staff
- Reject staff
- Manage staff accounts
- Manage users
- Manage treks
- View contact messages
- Role-based access control

---

## 🔐 Role-Based Access

The application supports three roles:

| Role | Main Responsibilities |
|------|------------------------|
| User | Browse treks and make bookings |
| Staff | Manage and process bookings |
| Admin | Manage users, staff, treks and messages |

Unauthorized users are redirected to the login page when attempting to access protected routes.

---

## 🏔️ Trek Management

Each trek contains information such as:

- Trek Name
- Location
- Difficulty
- Duration
- Available Slots
- Start Date
- End Date
- Trek Status
- Description

Trek status can be used to identify whether a trek is open or closed.

---

## 📅 Booking Management

Users can book available treks.

The booking workflow is:

```text
User makes booking
        ↓
Booking Status: Pending
        ↓
Staff reviews booking
        ↓
   ┌───────────────┐
   ↓               ↓
Approve          Reject
   ↓
Approved
   ↓
Completed


📞 Contact Management

Users can send messages through the Contact Us page.

The application stores:

Name
Email
Subject
Message
Created Date/Time

Administrators can view submitted contact messages from the Admin Dashboard.

🔎 Trek Search and Filtering

Users can search and filter treks using:

Trek Name
Difficulty
Location

A Reset option is also provided to clear the filters.


🖥️ Technology Stack
Frontend
HTML5
CSS3
Bootstrap 5
Jinja2 Templates
Backend
Python
Flask
Database
SQLite
Development Tools
Visual Studio Code
Python
Flask
SQLite

📂 Project Structure
Trek-Management/
│
├── app.py
├── database.py
├── trekking.db
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── images/
│       ├── trek1.jpg
│       ├── trek2.jpg
│       ├── trek3.jpg
│       ├── trek4.jpg
│       ├── trek5.jpg
│       └── trek6.jpg
│
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── about.html
    ├── contact.html
    │
    ├── admin_dashboard.html
    ├── admin_users.html
    ├── admin_staff.html
    ├── admin_treks.html
    ├── admin_messages.html
    │
    ├── staff_dashboard.html
    ├── staff_bookings.html
    │
    ├── user_dashboard.html
    ├── user_profile.html
    ├── user_trek.html
    ├── trek_details.html
    └── user_bookings.html

    🗄️ Database Tables

The application uses SQLite with the following main tables:

user

Stores registered user information.

id
name
email
password
phone
address
role
status

staff

Stores staff information and approval status.

id
name
email
password
phone
address
status
trek

Stores trek information.

id
name
location
difficulty
duration
available_slots
start_date
end_date
status
description
bookings

Stores trek booking information.

id
user_id
trek_id
booking_date
status

contact_messages

Stores messages submitted through the Contact page.

id
name
email
subject
message
created_at
⚙️ Installation and Setup
1. Clone or download the project

Place the project in your desired directory.

2. Open the project folder
cd Trek-Management
3. Install Flask
pip install flask
4. Create/Update the database

Run:

python database.py

The application uses:

trekking.db

as its SQLite database.

5. Run the Flask application
python app.py
6. Open the application

Open the following URL in your browser:

http://127.0.0.1:5000/
🔑 Login
Admin

The current application uses the configured administrator credentials from app.py.

For security, change the default administrator credentials before deploying the application.

User

Users can create an account through:

/register
Staff

Staff members can register through the registration page. Their account requires administrator approval before they can log in.

🔒 Security and Access Control

The application implements role-based decorators:

@admin_required
@staff_required
@user_required

These decorators restrict access to role-specific routes.

For example:

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    ...

Only authenticated administrators can access the Admin Dashboard.

🎨 User Interface

The application uses Bootstrap for responsive design.

The Home page includes:

Trekking-themed image collage
Application introduction
Login button
Learn More button
Featured trek section
Why Choose Us section
Trekker feedback section
Call-to-action section
Footer
📋 Application Workflow
                    Trekking Management Application
                              |
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
           Admin            Staff             User
             |                |                |
      Manage System     Manage Bookings    Explore Treks
             |                |                |
      Manage Users      Approve/Reject       Search
      Manage Staff       Bookings           Treks
      Manage Treks          |                |
      View Messages       Complete           Book Trek
                           Booking              |
                                              ↓
                                         Booking Pending
                                              |
                                              ↓
                                         Staff Review
                                              |
                                   ┌──────────┴──────────┐
                                   ↓                     ↓
                                Approved              Rejected
                                   |
                                   ↓
                               Completed
🚀 Future Enhancements

Possible future improvements include:

Password hashing
Email notifications
Online payment integration
Trek reviews and ratings
Trek images stored in the database
Advanced booking reports
Admin analytics and charts
Pagination for large datasets
Improved form validation
Deployment to a cloud platform
👩‍💻 Project Purpose

This project demonstrates the development of a role-based web application using Flask and SQLite.

It covers:

Web development
Database management
CRUD operations
Authentication
Role-based authorization
Search and filtering
Booking management
Form handling
Jinja2 templating
Responsive UI design
📄 License

This project is developed for educational and academic purposes.
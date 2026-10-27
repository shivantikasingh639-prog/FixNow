from flask import Flask, render_template, request, redirect, url_for, flash, session
import webbrowser
from threading import Timer
import random
import sqlite3
import os
import hmac
import hashlib
import secrets
import pandas as pd
from pathlib import Path

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATABASE = os.path.join(app.root_path, "fixnow.db")


# ================= DATABASE =================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    # Users Table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL
        )
    """)

    # Bookings Table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            technician TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            booking_date TEXT,
            booking_time TEXT,
            address TEXT NOT NULL,
            problem TEXT NOT NULL,
            vehicle TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
        # Technician Live Location Table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS technician_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL UNIQUE,
            technician_name TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            status TEXT NOT NULL DEFAULT 'Assigned',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()
# ================= PASSWORD SECURITY =================

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600000
    ).hex()

    return password_hash, salt


# ================= HOME PAGE =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return redirect(url_for("login"))

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if user:
            entered_hash, _ = hash_password(
                password,
                user["password_salt"]
            )

            if hmac.compare_digest(
                entered_hash,
                user["password_hash"]
            ):
                session.clear()
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]

                return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ================= CREATE ACCOUNT =================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm_password]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        password_hash, password_salt = hash_password(password)

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users
                (name, email, password_hash, password_salt)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, password_hash, password_salt)
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()
            flash("This email is already registered. Please log in.", "error")
            return redirect(url_for("login"))

        connection.close()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# ================= LOGOUT =================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================= DASHBOARD =================

# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User")
    )

# ================= TECHNICIANS =================

@app.route("/technicians/<service>")
def technicians(service):

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("technicians.html", service=service)


# ================= TECHNICIAN PROFILE =================

@app.route("/profile/<technician>")
def profile(technician):

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("profile.html", technician=technician)


# ================= BOOKING =================

# ================= BOOKING =================

@app.route("/booking/<technician>")
def booking(technician):

    if "user_id" not in session:
        return redirect(url_for("login"))

    from datetime import date

    # Get the selected service from the URL parameters
    service = request.args.get("service", "Service")

    # Get the logged-in user's name
    user_name = session.get("user_name", "")

    return render_template(
        "booking.html",
        technician=technician,
        service=service,
        user_name=user_name,
        today=date.today().isoformat()
    )


# ================= BOOKING CONFIRMATION =================

# ================= BOOKING CONFIRMATION =================

@app.route("/confirmation/<technician>", methods=["GET", "POST"])
def confirmation(technician):

    if "user_id" not in session:
        flash("Please log in before booking a service.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        from datetime import date

        # Booking form se details lena
        booking_id = "FXN" + secrets.token_hex(4).upper()

        service = request.form.get("service", "Service").strip()
        booking_date = request.form.get("date", "").strip()
        booking_time = request.form.get("time", "").strip()
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        address = request.form.get("address", "").strip()
        problem = request.form.get("problem", "").strip()

        # Check karna ki saari details bhari hain
        if not all([
            booking_date,
            booking_time,
            name,
            mobile,
            address,
            problem
        ]):
            flash("Please fill in all booking details.", "error")
            return redirect(
                url_for("booking", technician=technician, service=service)
            )

        # Mobile number validation
        if not mobile.isdigit() or len(mobile) != 10:
            flash("Please enter a valid 10-digit mobile number.", "error")
            return redirect(
                url_for("booking", technician=technician, service=service)
            )

        # Date validation
        if booking_date < date.today().isoformat():
            flash("Please select today or a future date.", "error")
            return redirect(
                url_for("booking", technician=technician, service=service)
            )

        # Booking ko database mein save karna
        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO bookings (
                    booking_id,
                    user_id,
                    service,
                    technician,
                    customer_name,
                    mobile,
                    booking_date,
                    booking_time,
                    address,
                    problem,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    booking_id,
                    session["user_id"],
                    service,
                    technician,
                    name,
                    mobile,
                    booking_date,
                    booking_time,
                    address,
                    problem,
                    "Pending"
                )
            )

            connection.commit()

        except sqlite3.Error:
            connection.rollback()
            app.logger.exception("Booking could not be saved.")

            flash("Booking save nahi hui. Please try again.", "error")

            return redirect(
                url_for("booking", technician=technician, service=service)
            )

        finally:
            connection.close()

        # Confirmation page par booking details dikhana
        return render_template(
            "confirmation.html",
            technician=technician,
            booking_id=booking_id,
            service=service,
            date=booking_date,
            time=booking_time,
            name=name,
            mobile=mobile,
            address=address,
            problem=problem
        )

    # Direct URL se confirmation open hone par
    return redirect(
        url_for("booking", technician=technician)
    )

# ================= TRACKING =================

@app.route("/tracking/<technician>")
def tracking(technician):

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("tracking.html", technician=technician)
# ================= TECHNICIAN LOCATION UPDATE =================

@app.route("/api/tracking/<booking_id>", methods=["POST"])
def update_technician_location(booking_id):

    if "user_id" not in session:
        return {"error": "Please log in first"}, 401

    data = request.get_json(silent=True) or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    technician_name = data.get("technician_name")
    status = data.get("status", "On the Way")

    if latitude is None or longitude is None or not technician_name:
        return {
            "error": "Latitude, longitude and technician name are required"
        }, 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return {"error": "Invalid coordinates"}, 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return {"error": "Coordinates are out of range"}, 400

    allowed_statuses = [
        "Assigned",
        "Started",
        "On the Way",
        "Arrived"
    ]

    if status not in allowed_statuses:
        return {"error": "Invalid status"}, 400

    connection = get_db_connection()

    try:
        booking = connection.execute(
            """
            SELECT booking_id, technician
            FROM bookings
            WHERE booking_id = ?
            """,
            (booking_id,)
        ).fetchone()

        if not booking:
            return {"error": "Booking not found"}, 404

        connection.execute(
            """
            INSERT INTO technician_locations
                (booking_id, technician_name, latitude, longitude, status,
                 updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(booking_id) DO UPDATE SET
                technician_name = excluded.technician_name,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                booking_id,
                technician_name,
                latitude,
                longitude,
                status
            )
        )

        connection.commit()

        return {
            "success": True,
            "message": "Technician location updated",
            "status": status
        }

    finally:
        connection.close()


# ================= CUSTOMER TRACKING API =================

@app.route("/api/tracking/<booking_id>", methods=["GET"])
def get_technician_location(booking_id):

    if "user_id" not in session:
        return {"error": "Please log in first"}, 401

    connection = get_db_connection()

    try:
        booking = connection.execute(
            """
            SELECT booking_id, user_id
            FROM bookings
            WHERE booking_id = ?
            """,
            (booking_id,)
        ).fetchone()

        if not booking:
            return {"error": "Booking not found"}, 404

        if booking["user_id"] != session["user_id"]:
            return {"error": "You cannot access this booking"}, 403

        location = connection.execute(
            """
            SELECT latitude, longitude, status, updated_at
            FROM technician_locations
            WHERE booking_id = ?
            """,
            (booking_id,)
        ).fetchone()

        if not location:
            return {
                "success": True,
                "location_available": False,
                "message": "Waiting for technician location"
            }

        return {
            "success": True,
            "location_available": True,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "status": location["status"],
            "updated_at": location["updated_at"]
        }

    finally:
        connection.close()


# ================= EMERGENCY BOOKING =================

@app.route("/emergency-booking/<path:emergency>", methods=["GET", "POST"])
def emergency_booking(emergency):

    if "user_id" not in session:
        flash("Please log in before booking an emergency service.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        vehicle = request.form.get("vehicle", "").strip()
        address = request.form.get("address", "").strip()
        problem = request.form.get("problem", "").strip()

        if not all([name, mobile, vehicle, address, problem]):
            flash("Please fill in all required booking fields.", "error")
            return redirect(
                url_for("emergency_booking", emergency=emergency)
            )

        if not mobile.isdigit() or len(mobile) != 10:
            flash("Enter a valid 10-digit mobile number.", "error")
            return redirect(
                url_for("emergency_booking", emergency=emergency)
            )

        booking_id = "FXN" + str(random.randint(100000, 999999))

        return render_template(
            "confirmation.html",
            technician="Emergency Assistance",
            booking_id=booking_id,
            service=emergency.replace("-", " ").replace("_", " "),
            name=name,
            mobile=mobile,
            vehicle=vehicle,
            address=address,
            problem=problem,
            date="Not selected",
            time="Not selected"
        )

    return render_template(
        "emergency_booking.html",
        emergency=emergency
    )


# ================= START APPLICATION =================

if __name__ == "__main__":
    init_db()

    Timer(
        1,
        lambda: webbrowser.open_new("http://127.0.0.1:5000/login")
    ).start()

    app.run(debug=True, use_reloader=False)
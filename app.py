from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"  # for sessions & flash messages

# ---------- MONGODB CONNECTION ----------
client = MongoClient("mongodb://localhost:27017/")  # connect to local MongoDB
db = client["auto_service_finder"]                  # database name
users_col = db["users"]
centers_col = db["service_centers"]

# ---------- INITIAL DATA SETUP ----------
def init_data():
    """Insert sample service centers if not already present."""
    if centers_col.count_documents({}) == 0:
        centers_col.insert_many([
            {"name": "SpeedX Bike Garage", "address": "Near Main Road, Hyderabad", "phone": "9876543210"},
            {"name": "MotoCare Service Hub", "address": "Beside Bus Stand, Vijayawada", "phone": "9123456780"},
            {"name": "FastFix Mechanics", "address": "Opp. Metro Station, Chennai", "phone": "9988776655"},
            {"name": "AutoPro Bike Clinic", "address": "Nehru Street, Bengaluru", "phone": "9876501234"},
            {"name": "WheelWorks Garage", "address": "Gandhi Road, Vizag", "phone": "9000090000"},
        ])
        print("✅ Inserted 5 sample service centers into MongoDB!")

# ---------- ROUTES ----------
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if already exists
        if users_col.find_one({"email": email}):
            flash("⚠️ Email already registered. Try logging in.", "warning")
            return redirect(url_for('login'))

        users_col.insert_one({"email": email, "password": password})
        flash("✅ Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_col.find_one({"email": email, "password": password})
        if user:
            session['user'] = email
            flash("✅ Login successful!", "success")
            return redirect(url_for('servicecenter'))
        else:
            flash("❌ Invalid email or password.", "danger")

    return render_template('login.html')


@app.route('/servicecenter')
def servicecenter():
    """Show nearby service centers after login"""
    if 'user' not in session:
        flash("Please login to view nearby service centers.", "info")
        return redirect(url_for('login'))

    centers = list(centers_col.find())
    return render_template('servicecenter.html', service_centers=centers, user=session['user'])


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


# ---------- MAIN ----------
if __name__ == '__main__':
    init_data()  # add 5 sample service centers if empty
    app.run(debug=True)


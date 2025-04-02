from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import random
import string
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.py
app.config.from_pyfile('config.py')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)

# Configure login manager
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return render_template('signup.html')

        generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = bcrypt.generate_password_hash(generated_password).decode('utf-8')

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()

            msg = Message("Your AI Subscription Analyzer Password", recipients=[email])
            msg.body = f"""Hello {first_name} {last_name},
            
Your account has been created successfully!
            
Password: {generated_password}
            
Keep it safe and change it later if needed."""
            mail.send(msg)
            flash("Sign-up successful! Check your email for the password.", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        # Process Screen Time (replace with actual implementation)
        screen_time = {"Netflix": 120, "Spotify": 50, "Swiggy": 0}
        
        # Process Subscriptions (replace with actual implementation)
        subscriptions = [
            {"Platform": "Netflix", "Total (INR)": 199, "Usage": 120},
            {"Platform": "Spotify", "Total (INR)": 59, "Usage": 50}
        ]
        
        # Generate Visualization
        plot_path = generate_usage_plot(subscriptions, current_user.id)
        
        return render_template('dashboard.html',
                            screen_time=screen_time,
                            subscriptions=subscriptions,
                            plot_path=plot_path)
    
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for('home'))

def generate_usage_plot(subscriptions, user_id):
    apps = [sub['Platform'] for sub in subscriptions]
    costs = [sub['Total (INR)'] for sub in subscriptions]
    usages = [sub['Usage'] for sub in subscriptions]

    plt.figure(figsize=(10, 6))
    plt.bar(apps, costs, alpha=0.5, label='Cost (INR)')
    plt.bar(apps, usages, alpha=0.5, label='Usage (Hours)')
    plt.xlabel('Subscription Services')
    plt.ylabel('Amount')
    plt.title('Subscription Cost vs Usage Analysis')
    plt.legend()
    
    filename = f"usage_{user_id}.png"
    plot_path = os.path.join('static', 'plots', filename)
    plt.savefig(plot_path)
    plt.close()
    
    return url_for('static', filename=f'plots/{filename}')

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if user:
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_new_password
            db.session.commit()

            try:
                msg = Message("Password Reset - AI Subscription Analyzer", recipients=[email])
                msg.body = f"Your new password: {new_password}"
                mail.send(msg)
                flash("A new password has been sent to your email.", "success")
            except Exception as e:
                flash("Password reset failed to send email.", "warning")

            return redirect(url_for("login"))
        else:
            flash("No account found with that email.", "danger")

    return render_template("forgot_password.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Create plots directory if not exists
        if not os.path.exists(os.path.join('static', 'plots')):
            os.makedirs(os.path.join('static', 'plots'))
    app.run(debug=True)
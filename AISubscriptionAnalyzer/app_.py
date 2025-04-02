from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from modules.email_processor import process_screen_time
from modules.subscription_extractor import fetch_subscriptions
from modules.subscription_analyzer import analyze_subscriptions
import os
import matplotlib
matplotlib.use('Agg')  # Required for server-side plotting
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
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

# Routes
@app.route("/")
def home():
    return render_template("home.html")

# Add these routes after the dashboard route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Your existing signup implementation
    pass

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        # Process Screen Time
        screen_time = process_screen_time(current_user.email)
        
        # Process Subscriptions
        raw_subscriptions = fetch_subscriptions(current_user.email)
        subscriptions = analyze_subscriptions(raw_subscriptions)
        
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

# (Keep existing auth routes: signup, login, logout, forgot-password)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
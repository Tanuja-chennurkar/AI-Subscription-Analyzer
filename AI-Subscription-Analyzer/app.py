from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask import session
import random
import string
from flask_mail import Mail, Message
from model import analyze_subscriptions  # Import subscription analysis function
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'anweshaghoshisthebest@gmail.com'  # Replace with your email
#app.config['MAIL_PASSWORD'] = 'fzdfuscxrkisxrgc'
app.config['MAIL_PASSWORD'] = 'tnauwuanztjpjvjb' # Replace with Google App Password
app.config['MAIL_DEFAULT_SENDER'] = 'anweshaghoshisthebest@gmail.com'

mail = Mail(app)

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
            return render_template('signup.html')  # Stays on the signup page
            # return redirect(url_for("login"))

        generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = bcrypt.generate_password_hash(generated_password).decode('utf-8')

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # if not first_name or not last_name or not email:
        #     flash("All fields are required!", "danger")
        #     return redirect(url_for("signup"))
        
        try:
            msg = Message("Your AI Subscription Analyzer Password", recipients=[email])
            msg.body = f"Hello {first_name} {last_name},\n\nYour account has been created successfully!\n\nHere is your login password: {generated_password}\n\nPlease keep it safe and change it later if needed."
            mail.send(msg)
            flash("Sign-up successful! Check your email for the password.", "success")
        except Exception as e:
            print(f"[ERROR] Failed to send email to {email}: {e}")
            flash("Sign-up successful, but the email could not be sent.", "warning")

        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user and user.password:  # Ensure password exists
            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id  # Store user session
                # login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))  # Redirect to dashboard after successful login
            else:
                flash("Email or password is wrong. Try again.", "error")
                return redirect(url_for('login'))  # Redirect back to login page
        else:
                flash("Email or password is wrong. Try again.", "error")
                return redirect(url_for('login'))  # Redirect back to login page
        
    return render_template('login.html')


    #     if user and bcrypt.check_password_hash(user.password, password):
    #         login_user(user)
    #         return redirect(url_for("dashboard"))
    #     else:
    #         flash("Invalid email or password!", "danger")

    # return render_template("login.html")

# @app.route("/dashboard")
# @login_required
# def dashboard():
#     unused_subscriptions = analyze_subscriptions(current_user.email)
#     #return render_template("dashboard.html", name=current_user.first_name)
#     return render_template("dashboard.html", name=current_user.first_name, unused_subscriptions=unused_subscriptions)

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        unused_subscriptions = analyze_subscriptions(current_user.email)
    except Exception as e:
        flash("Error analyzing subscriptions.", "danger")
        unused_subscriptions = []
    return render_template("dashboard.html", name=current_user.first_name, unused_subscriptions=unused_subscriptions)

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

            # generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            # hashed_new_password = bcrypt.generate_password_hash(generated_password).decode('utf-8')
            # user.password = hashed_new_password
            # db.session.commit()

            try:
                msg = Message("Password Reset - AI Subscription Analyzer", recipients=[email])
                msg.body = f"""
                Hello,

                Your new password is: {new_password}
                Please log in using this password and change it if needed.
                """
                mail.send(msg)
                flash("A new password has been sent to your email.", "success")
            except Exception as e:
                flash("Password reset successful, but email could not be sent.", "warning")

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
    app.run(debug=True)
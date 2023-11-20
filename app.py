from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models.User import User  # Import the User class
from models.User import db
from models.Product import Product

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


# Login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Routes
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the username is already taken
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return render_template("register.html", form=form)

        # Check if the email is already taken
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email is already taken. Please choose a different one.', 'danger')
            return render_template("register.html", form=form)

        # If both username and email are available, create the new user
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template("login.html", form=form)


@app.route("/mylogout")
@login_required
def mylogout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

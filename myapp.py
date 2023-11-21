from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy

# from models.User import User
# from models.User import db
# from models.Product import Product
from models.Forms.ProductForm import ProductForm
from models.Forms.RegistrationForm import RegistrationForm
from models.Forms.LoginForm import LoginForm
from models.Forms.SearchByCategoryForm import SearchByCategoryForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10

db = SQLAlchemy(app)
# db_session = db.scoped_session(db.sessionmaker(autocommit=False, autoflush=False, bind=db.engine))

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
        # Check if the login is for an admin
        if form.email.data == 'admin@admin.com' and form.password.data == 'admin':
            flash('Admin login successful!', 'success')
            login_user(User.query.get(1))
            return render_template("admin_dashboard.html", form=ProductForm(), products=Product.query.all())

        # Check if the login is for a regular user
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


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = SearchByCategoryForm()
    search_results = []

    if form.validate_on_submit():
        search_query = form.category.data
        print("Form submitted.")

        search_results = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()
    return render_template("profile.html", user=current_user, form=form, search_results=search_results)


################# Product ############

@app.route("/search_by_category", methods=['POST'])
@login_required
def search_by_category():
    form = ProductForm()

    if form.validate_on_submit():
        search_query = form.category.data

        search_results = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()

        return render_template("profile.html", user=current_user, form=form, search_results=search_results)

    # Redirect to the profile page if the form is not submitted correctly
    return redirect(url_for('profile'))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    form = ProductForm()
    products = Product.query.all()
    return render_template("admin_dashboard.html", form=form, products=products)


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    flash('Admin logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route("/admin/add_product", methods=['POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.category.data,
            price=form.price.data,
            description=form.description.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
    else:
        flash('Failed to add product. Please check the form.', 'danger')
    return redirect(url_for('admin_dashboard'))


################# Product ############


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

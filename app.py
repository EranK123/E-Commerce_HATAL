from flask import Flask, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from models.Forms.OrderForm import OrderForm
from models.Forms.ProductForm import ProductForm
from models.Forms.RegistrationForm import RegistrationForm
from models.Forms.LoginForm import LoginForm
from models.Forms.SearchByCategoryForm import SearchByCategoryForm
from flask import request

# from models.User import User
# from models.Product import Product
# from models.Order import Order

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


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


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    product_description = db.Column(db.Text, nullable=True)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    status = db.Column(db.String(20), default='cart', nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return render_template("register.html", form=form)

        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email is already taken. Please choose a different one.', 'danger')
            return render_template("register.html", form=form)

        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        user.password = bcrypt.generate_password_hash(user.password).decode('utf-8')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@admin.com' and form.password.data == 'admin':
            # flash('Admin login successful!', 'success')
            login_user(User.query.get(1))
            return render_template("admin_dashboard.html", form=ProductForm(), products=Product.query.all())

        user = User.query.filter_by(email=form.email.data).first()
        is_valid = bcrypt.check_password_hash(user.password, form.password.data)
        if user and is_valid:
            login_user(user)
            # flash('Login successful!', 'success')
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
    order_form = OrderForm()
    search_results = []

    if form.validate_on_submit():
        search_query = form.category.data
        search_results = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()

    if order_form.validate_on_submit():
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)

        if product:
            order = Order(
                user_id=current_user.id,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                status='cart',
                product_description=product.description)
            db.session.add(order)
            db.session.commit()

            flash('Item added to cart!', 'success')

            return render_template("profile.html", user=current_user, form=form, search_results=search_results,
                                   order_form=order_form)

    return render_template("profile.html", user=current_user, form=form, search_results=search_results,
                           order_form=order_form)


@app.route("/search_by_category", methods=['POST'])
@login_required
def search_by_category():
    form = ProductForm()

    if form.validate_on_submit():
        search_query = form.category.data
        search_results = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()
        return render_template("profile.html", user=current_user, form=form, search_results=search_results)

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
    # flash('Admin logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route("/admin/add_product", methods=['POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.category.data,
            price=form.price.data,
            description=form.description.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
    else:
        flash('Failed to add product. Please check the form.', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route("/cart")
@login_required
def cart():
    cart_items = Order.query.filter_by(user_id=current_user.id).all()
    order_form = OrderForm()
    return render_template("cart.html", user=current_user, cart_items=cart_items, order_form=order_form)


@app.route("/checkout")
@login_required
def checkout():
    cart_items = Order.query.filter_by(user_id=current_user.id).all()
    for item in cart_items:
        db.session.delete(item)
        product = Product.query.get(item.product_id)
        if product:
            db.session.delete(product)

    db.session.commit()

    flash('Checkout successful! Your orders have been processed.', 'success')
    return redirect(url_for('profile'))



@app.route("/remove_from_cart/<int:order_id>", methods=['POST'])
@login_required
def remove_from_cart(order_id):
    order = Order.query.get(order_id)

    if order and order.user_id == current_user.id:
        db.session.delete(order)
        db.session.commit()
        flash('Item removed from the cart!', 'success')
    else:
        flash('Failed to remove item from the cart.', 'danger')

    return redirect(url_for('profile'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)

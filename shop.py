from flask_login import login_required
from flask import render_template, request, redirect, url_for
from myapp import app
from models.User import db
from models.Product import Product


# Product Listing
@app.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('product_list.html', products=products)


# Product Details
@app.route('/products/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)


# Product Search
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        # Perform a simple search on the product names
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
        return render_template('search_results.html', products=products, search_query=search_query)
    return render_template('search.html')

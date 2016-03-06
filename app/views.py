from flask import render_template, redirect, url_for, flash, session
from app import app, db
from models import Product, Cart, LineItem


@app.route('/')
@app.route('/index')
def index():
    products = Product.query.all()
    return render_template('index.html',
                           title='Index',
                           products=products)


@app.route('/add/<int:product_id>')
def add(product_id):
    product = Product.query.get(product_id)
    # Checks to see if the user has already started a cart.
    cart = Cart.query.get(session['cart'])
    if cart is not None:
        # If line item does not exist, create it
        l_item = LineItem.query.get((cart.id, product.id))
        if l_item is None:
            l_item = LineItem(cart_id=cart.id, product_id=product.id, quantity=1)
        # If line item exists, just update quantity
        else:
            l_item.quantity += 1
    else:
        cart = Cart()
        session['cart'] = cart.id
        l_item = LineItem(cart_id=cart.id, product_id=product.id, quantity=1)

    product.line_item.append(l_item)
    cart.line_item.append(l_item)
    db.session.add(cart)
    db.session.add(product)
    db.session.add(l_item)
    db.session.commit()
    return str(LineItem.query.get((1, product.id)).quantity)

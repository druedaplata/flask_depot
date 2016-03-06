from flask import render_template, redirect, url_for, flash, session
from app import app, db
from models import Product, Cart, LineItem


def get_all_products():
    return Product.query.all()


def get_current_cart():
    try:
        return Cart.query.get(session['cart'])
    except:
        return None


def cart_is_empty(cart):
    return 0 if db.session.query(LineItem).filter_by(cart_id=cart.id).first() else 1


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Index',
                           products=get_all_products(),
                           cart=get_current_cart())


@app.route('/add/<int:product_id>')
def add(product_id):
    product = Product.query.get(product_id)
    # Checks to see if the user has already started a cart.
    cart = get_current_cart()
    if cart is None:
        # Create cart and add line_item
        cart = Cart()

    # Check for a line_item, if it doesn't exists create it, if it does update it.
    l_item = LineItem.query.get((cart.id, product.id))
    if l_item is None:
        l_item = LineItem(cart_id=cart.id, product_id=product.id, quantity=1)
    else:
        l_item.quantity += 1

    product.line_item.append(l_item)
    cart.line_item.append(l_item)
    db.session.add(cart)
    db.session.add(product)
    db.session.add(l_item)
    db.session.commit()
    session['cart'] = cart.id
    return redirect('index')


@app.route('/remove/<int:product_id>')
def remove(product_id):
    # Remove product and commit changes
    product = Product.query.get(product_id)
    cart = get_current_cart()
    l_item = LineItem.query.get((cart.id, product.id))
    db.session.delete(l_item)
    db.session.commit()

    # if the cart is empty, delete it
    if cart_is_empty(cart):
        session.pop('cart')
        db.session.delete(cart)
        db.session.commit()
    return redirect('index')

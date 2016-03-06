from app import app, db
from flask import url_for
from flask_admin import Admin, form
from sqlalchemy.event import listens_for
from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup
import os


class LineItem(db.Model):
    __tablename__ = 'line_items'
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    quantity = db.Column(db.Integer)


class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    line_item = db.relationship('LineItem', backref='cart',
                                primaryjoin=(id == LineItem.cart_id))


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(64), index=True, unique=True)
    description = db.Column(db.Unicode(500), index=True, unique=True)
    image_url = db.Column(db.Unicode(128))
    price = db.Column(db.Float)
    line_item = db.relationship('LineItem', backref='product',
                                primaryjoin=(id == LineItem.product_id))

    def __unicode__(self):
        return self.nombre

    def get_image(self):
        return unicode('/static/img/' + self.image_url)

    def get_price(self):
        return unicode("$ %10.2f" % self.price)


# Create directory for file fields to use
file_path = os.path.join(os.path.dirname(__file__), 'static/img')
try:
    os.mkdir(file_path)
except OSError:
    pass


@listens_for(Product, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            os.remove(os.path.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(os.path.join(file_path, form.thumbgen_filename(target.path)))
        except OSError:
            pass


class product_image(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.image_url:
            return ''
        return Markup('<img src="%s">' % url_for('static',
                                                 filename=form.thumbgen_filename('img/' + model.image_url)))

    column_formatters = {
        'image_url': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'image_url': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(50, 50, True))
    }
admin = Admin(app)
admin.add_view(product_image(Product, db.session))
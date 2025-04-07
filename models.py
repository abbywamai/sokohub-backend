from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    orders = db.relationship('Order', backref='vendor', lazy=True)
    payments = db.relationship('Payment', backref='vendor', lazy=True)
    reviews = db.relationship('Review', backref='vendor', lazy=True)


class Farmer(db.Model):
    __tablename__ = 'farmers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    whatsapp_link = db.Column(db.String(255))
    location = db.Column(db.String(100))
    kephis_certified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    produce = db.relationship('Produce', backref='farmer', lazy=True)
    orders = db.relationship('Order', backref='farmer', lazy=True)
    reviews = db.relationship('Review', backref='farmer', lazy=True)


class Produce(db.Model):  # Changed from Product to Produce
    __tablename__ = 'produce'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Added quantity to match API
    quality = db.Column(db.String(50), nullable=False)  # Added quality field
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    orders = db.relationship('Order', backref='produce', lazy=True)  # Linked to orders


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    produce_id = db.Column(db.Integer, db.ForeignKey('produce.id'), nullable=False)  # Changed to match API
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10,2), nullable=False)
    deposit_paid = db.Column(db.Boolean, default=False)
    order_status = db.Column(db.String(20), default="Pending")  # Default "Pending"
    mpesa_code = db.Column(db.String(50))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    mpesa_code = db.Column(db.String(50))
    payment_status = db.Column(db.String(20))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

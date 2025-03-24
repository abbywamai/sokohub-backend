from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from models import db, Vendor, Farmer, Produce, Order, Payment, Review


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:wamai@localhost/sokohub"
app.config["JWT_SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Authentication Routes
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    vendor = Vendor(name=data["name"], email=data["email"], password=hashed_password)
    db.session.add(vendor)
    db.session.commit()

    return jsonify({"message": "Vendor registered successfully"}), 201



@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    vendor = Vendor.query.filter_by(email=data["email"]).first()

    if vendor and bcrypt.check_password_hash(vendor.password, data["password"]):
        token = create_access_token(identity=vendor.id)
        return jsonify({"access_token": token})

    return jsonify({"message": "Invalid credentials"}), 401

# Produce Routes
@app.route("/api/produce", methods=["GET"])
def get_produce():
    produce_list = Produce.query.all()
    result = [
        {
            "id": p.id,
            "name": p.name,
            "quantity": p.quantity,
            "price": p.price,
            "quality": p.quality,
            "farmer": p.farmer.name,
        }
        for p in produce_list
    ]
    return jsonify(result)

@app.route("/api/produce/<int:produce_id>", methods=["GET"])
def get_produce_details(produce_id):
    produce = Produce.query.get_or_404(produce_id)
    return jsonify({
        "id": produce.id,
        "name": produce.name,
        "quantity": produce.quantity,
        "price": produce.price,
        "quality": produce.quality,
        "farmer": produce.farmer.name,
    })

# Order Routes
@app.route("/api/orders", methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()
    vendor_id = get_jwt_identity()
    
    produce = Produce.query.get_or_404(data["produce_id"])
    if data["quantity"] > produce.quantity:
        return jsonify({"message": "Not enough stock available"}), 400

    order = Order(
        produce_id=data["produce_id"],
        vendor_id=vendor_id,
        quantity=data["quantity"],
        status="Pending",
    )
    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Order placed successfully", "order_id": order.id})

@app.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    vendor_id = get_jwt_identity()
    orders = Order.query.filter_by(vendor_id=vendor_id).all()

    result = [
        {
            "id": o.id,
            "produce": o.produce.name,
            "quantity": o.quantity,
            "status": o.status,
        }
        for o in orders
    ]
    return jsonify(result)





if __name__ == "__main__":
    app.run()
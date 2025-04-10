from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from models import db, Vendor, Farmer, Produce, Order, Payment, Review
from mpesa import lipa_na_mpesa_pochi
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:wamai@localhost/sokohub"
app.config["JWT_SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Farmer Authentication Routes
@app.route("/api/farmer/register", methods=["POST"])
def farmer_register():
    data = request.get_json()

    # Check if the farmer already exists
    existing_farmer = Farmer.query.filter_by(email=data["email"]).first()
    if existing_farmer:
        return jsonify({"message": "Farmer already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    farmer = Farmer(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        mpesa=data["mpesa"],
        whatsapp_link=data.get("whatsapp_link"),
        location=data.get("location"),
        kephis_certified=data.get("kephis_certified", False)
    )
    db.session.add(farmer)
    db.session.commit()

    return jsonify({"message": "Farmer registered successfully"}), 201

@app.route("/api/farmer/login", methods=["POST"])
def farmer_login():
    data = request.get_json()
    farmer = Farmer.query.filter_by(email=data["email"]).first()

    if farmer and bcrypt.check_password_hash(farmer.password, data["password"]):
        token = create_access_token(identity=farmer.id)
        return jsonify({"access_token": token})

    return jsonify({"message": "Invalid credentials"}), 401

# Post Produce Route
@app.route("/api/farmer/produce", methods=["POST"])
@jwt_required()
def post_produce():
    data = request.get_json()
    farmer_id = get_jwt_identity()

    # Check if the farmer exists
    farmer = Farmer.query.get_or_404(farmer_id)

    # Create new produce
    produce = Produce(
        name=data["name"],
        quantity=data["quantity"],
        price=data["price"],
        quality=data["quality"],
        farmer_id=farmer.id,
        created_at=datetime.utcnow()
    )
    db.session.add(produce)
    db.session.commit()

    return jsonify({"message": "Produce posted successfully", "produce_id": produce.id}), 201

# Authentication Routes for Vendor (unchanged)
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

# Produce Routes (unchanged)
@app.route('/api/produce', methods=['GET'])
def get_produce():
    category = request.args.get('category')
    
    if category:
        produce_items = Produce.query.filter_by(category=category).all()
    else:
        produce_items = Produce.query.all()
    
    result = []
    for produce in produce_items:
        result.append({
            'id': produce.id,
            'name': produce.name,
            'price': produce.price,
            'quantity': produce.quantity,
            'category': produce.category,
            'farmer_id': produce.farmer_id,
            'location': produce.location
        })
    
    return jsonify(result), 200

@app.route('/api/produce/categories', methods=['GET'])
def get_produce_categories():
    categories = db.session.query(Produce.category).distinct().all()
    category_list = [c[0] for c in categories if c[0]]  # Flatten and ignore None
    return jsonify(category_list), 200


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

# Order Routes (unchanged)
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

# M-Pesa Payment Route (unchanged)
@app.route("/api/payment/mpesa", methods=["POST"])
@jwt_required()
def mpesa_payment():
    data = request.get_json()
    vendor_id = get_jwt_identity()

    vendor = Vendor.query.get_or_404(vendor_id)
    farmer = Farmer.query.get_or_404(data["farmer_id"])

    amount = data["amount"]
    phone_number = vendor.phone  # Vendor's phone number
    farmer_number = farmer.phone  # Farmer's Pochi number (MSISDN format)

    # Initiate payment via M-Pesa
    response = lipa_na_mpesa_pochi(phone_number, amount, farmer_number)

    if response.get("ResponseCode") == "0":
        # Record the payment in the database
        payment = Payment(
            vendor_id=vendor.id,
            farmer_id=farmer.id,
            amount=amount,
            transaction_status="Pending",  # We can update this based on M-Pesa callback
            transaction_id=response.get("MerchantRequestID")
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({"message": "Payment initiated successfully", "payment_id": payment.id, "response": response}), 200
    else:
        return jsonify({"message": "Payment initiation failed", "response": response}), 400

# M-Pesa Callback Route (M-Pesa will call this URL after the transaction is processed)
@app.route("/api/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()

    # Process the callback from M-Pesa (e.g., update payment status)
    transaction_id = data.get("TransactionID")
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()

    if payment:
        payment.transaction_status = "Completed" if data.get("ResponseCode") == "0" else "Failed"
        db.session.commit()
        return jsonify({"message": "Callback processed successfully"}), 200
    else:
        return jsonify({"message": "Payment not found"}), 404


if __name__ == "__main__":
    app.run()

from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONNECTION ----------------
def connect_db():
    return sqlite3.connect("database.db")

# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    # Products table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        code INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        stock INTEGER
    )
    """)

    # Bills table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_phone TEXT,
        worker_name TEXT,
        product_code INTEGER,
        quantity INTEGER,
        total_amount REAL,
        incentive REAL
    )
    """)

    conn.commit()
    conn.close()

# ---------------- DATASET INSERT ----------------
def insert_sample_data():
    conn = connect_db()
    cur = conn.cursor()

    products = [
        (101, "Rice", 60, 100),
        (102, "Sugar", 40, 120),
        (103, "Soap", 30, 200),
        (104, "Oil", 150, 50),
        (105, "Shampoo", 120, 80)
    ]

    cur.executemany(
        "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)",
        products
    )

    conn.commit()
    conn.close()

create_tables()
insert_sample_data()

# ---------------- FETCH PRODUCT BY CODE ----------------
@app.route("/get_product/<int:code>")
def get_product(code):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT name, price, stock FROM products WHERE code=?", (code,))
    product = cur.fetchone()
    conn.close()

    if product:
        return jsonify({
            "name": product[0],
            "price": product[1],
            "stock": product[2]
        })
    else:
        return jsonify({"error": "Invalid Product Code"}), 404

# ---------------- GENERATE BILL ----------------
@app.route("/generate_bill", methods=["POST"])
def generate_bill():
    data = request.json

    phone = data["phone"]
    worker = data["worker"]
    code = int(data["code"])
    quantity = int(data["quantity"])

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT price, stock FROM products WHERE code=?", (code,))
    product = cur.fetchone()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    price, stock = product

    if quantity > stock:
        return jsonify({"error": "Insufficient stock"}), 400

    total_amount = price * quantity

    # Incentive = ₹1 per product
    incentive = quantity * 1

    # Update stock
    cur.execute(
        "UPDATE products SET stock = stock - ? WHERE code=?",
        (quantity, code)
    )

    # Save bill
    cur.execute("""
        INSERT INTO bills VALUES (NULL, ?, ?, ?, ?, ?, ?)
    """, (phone, worker, code, quantity, total_amount, incentive))

    conn.commit()
    conn.close()

    return jsonify({
        "total": total_amount,
        "incentive": incentive
    })

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
import sqlite3
import rsa
import os

app = Flask(__name__)
DB_PATH = "licenses.db"
PRIVATE_KEY_PATH = "private.pem"

# Ensure DB exists
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                machine_id TEXT UNIQUE,
                activated_on DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return rsa.PrivateKey.load_pkcs1(f.read())

@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_json()
    email = data.get("email")
    machine_id = data.get("machine_id")

    if not email or not machine_id:
        return jsonify({"status": "error", "message": "Missing email or machine ID"}), 400

    # Check if machine is already registered
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM licenses WHERE machine_id = ?", (machine_id,))
        row = cur.fetchone()

        if not row:
            cur.execute("INSERT INTO licenses (email, machine_id) VALUES (?, ?)", (email, machine_id))
            conn.commit()

    try:
        private_key = load_private_key()
        signature = rsa.sign(machine_id.encode(), private_key, 'SHA-256')
        license_token = signature.hex()
        return jsonify({"status": "ok", "license_token": license_token})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

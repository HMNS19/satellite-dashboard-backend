from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import re
import os
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
except ImportError:
    pass


app = Flask(__name__)
CORS(app)
DB = 'telemetry.db'

# Update init_db() with new schema
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS telemetry ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "timestamp TEXT, "
            "source TEXT, "  # New column to identify sensor source
            "temperature REAL, "
            "humidity REAL, "
            "latitude REAL, "
            "longitude REAL, "
            "pressure REAL, "
            "gx REAL, gy REAL, gz REAL)"
        )
        conn.commit()

# Endpoint for LoRa data (ard.py) - extract only pressure and gyro
# Modify /data endpoint to include source
@app.route("/data", methods=['POST'])
def receive_lora_data():
    try:
        data = request.json.get('data')
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        try:
            pressure_match = re.search(r"P:([\d.]+)hPa", data)
            pressure = float(pressure_match.group(1)) if pressure_match else None
            
            gx_match = re.search(r"GX:([\d.-]+)", data)
            gy_match = re.search(r"GY:([\d.-]+)", data)
            gz_match = re.search(r"GZ:([\d.-]+)", data)
            
            gx = float(gx_match.group(1)) if gx_match else None
            gy = float(gy_match.group(1)) if gy_match else None
            gz = float(gz_match.group(1)) if gz_match else None
            
            if None in [pressure, gx, gy, gz]:
                return jsonify({"error": "Missing required fields"}), 400
        except Exception:
            return jsonify({"error": "Invalid data format"}), 400
        
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO telemetry (timestamp, source, pressure, gx, gy, gz) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), "arduino", pressure, gx, gy, gz)
            )
            conn.commit()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for WiFi data (rasp.py) - extract only temp, humidity, location
# Modify /upload endpoint to include source
@app.route("/upload", methods=['POST'])
def receive_upload_data():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        try:
            # Safely handle null/missing values
            temperature = float(data.get('temperature', 0.0))
            humidity = float(data.get('humidity', 0.0))
            latitude = float(data['latitude']) if 'latitude' in data and data['latitude'] is not None else None
            longitude = float(data['longitude']) if 'longitude' in data and data['longitude'] is not None else None
        except ValueError:
            return jsonify({"error": "Invalid numeric values"}), 400
        
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO telemetry (timestamp, source, temperature, humidity, latitude, longitude) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), "GPS", temperature, humidity, latitude, longitude)
            )
            conn.commit()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= API Endpoints (for frontend) =================
@app.route("/api/telemetry")
def api_telemetry():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # Get the most recent complete set of data
        c.execute("""
            SELECT 
                (SELECT temperature FROM telemetry WHERE temperature IS NOT NULL ORDER BY timestamp DESC LIMIT 1),
                (SELECT humidity FROM telemetry WHERE humidity IS NOT NULL ORDER BY timestamp DESC LIMIT 1),
                (SELECT pressure FROM telemetry WHERE pressure IS NOT NULL ORDER BY timestamp DESC LIMIT 1),
                (SELECT latitude FROM telemetry WHERE latitude IS NOT NULL ORDER BY timestamp DESC LIMIT 1),
                (SELECT longitude FROM telemetry WHERE longitude IS NOT NULL ORDER BY timestamp DESC LIMIT 1)
        """)
        row = c.fetchone()
        
        if row:
            return jsonify({
                "temperature": row[0] if row[0] is not None else 0.0,
                "humidity": row[1] if row[1] is not None else 0.0,
                "pressure": row[2] if row[2] is not None else 0.0,
                "location": {
                    "lat": row[3] if row[3] is not None else 0.0,
                    "lon": row[4] if row[4] is not None else 0.0
                }
            })
    
    return jsonify({
        "temperature": 0.0,
        "humidity": 0.0,
        "pressure": 0.0,
        "location": {"lat": 0.0, "lon": 0.0}
    })

# Update /api/logs endpoint
@app.route("/api/logs")
def api_logs():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT 
                id, 
                timestamp,
                source,
                temperature,
                humidity,
                pressure,
                latitude,
                longitude,
                gx, gy, gz
            FROM telemetry 
            ORDER BY timestamp DESC 
            LIMIT 300
        """)
        logs = c.fetchall()
    
    return jsonify([{
        "id": row[0],
        "timestamp": row[1],
        "source": row[2],
        "temperature": row[3] if row[3] is not None else "N/A",
        "humidity": row[4] if row[4] is not None else "N/A",
        "pressure": row[5] if row[5] is not None else "N/A",
        "latitude": row[6] if row[6] is not None else "N/A",
        "longitude": row[7] if row[7] is not None else "N/A",
        "gx": row[8] if row[8] is not None else "N/A",
        "gy": row[9] if row[9] is not None else "N/A",
        "gz": row[10] if row[10] is not None else "N/A"
    } for row in logs])

@app.route("/api/gyro")
def api_gyro():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT gx, gy, gz 
            FROM telemetry 
            WHERE gx IS NOT NULL AND gy IS NOT NULL AND gz IS NOT NULL
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        row = c.fetchone()
        
        if row:
            return jsonify({
                "roll": row[0],   # gx → roll
                "pitch": row[1],  # gy → pitch
                "yaw": row[2]     # gz → yaw
            })
    
    return jsonify({
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": 0.0
    })

# Login endpoint remains unchanged
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
        return jsonify({"success": True, "token": "demo-token"})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
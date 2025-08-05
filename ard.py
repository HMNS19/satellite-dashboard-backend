import requests
import random
import time
import os
import sys  # Added this import
from dotenv import load_dotenv

load_dotenv()
# Server configuration - with fallback options
DEFAULT_SERVER = "http://localhost:5000/data"
SERVER_URL = os.getenv("SERVER_BASE_URL", "http://localhost:5000") + "/data"
HEADERS = {"Content-Type": "application/json"}

def generate_sensor_data():
    """Generates data identical to your LoRa receiver's format"""
    return (
        f"T:{random.uniform(15.0, 35.0):.2f}C, "
        f"P:{random.uniform(500.0, 1500.0):.2f}hPa, "
        f"AX:{random.uniform(-1.0, 1.0):.2f}, "
        f"AY:{random.uniform(-1.0, 1.0):.2f}, "
        f"AZ:{random.uniform(-1.0, 1.0):.2f}, "
        f"GX:{random.uniform(-90, 90):.2f}, "
        f"GY:{random.uniform(-180, 180):.2f}, "
        f"GZ:{random.uniform(-180, 180):.2f}, "
        f"MX:{random.uniform(-0.5, 0.5):.2f}, "
        f"MY:{random.uniform(-0.5, 0.5):.2f}, "
        f"MZ:{random.uniform(-0.5, 0.5):.2f}"
    )

def send_to_server(data, server_url):
    """Improved HTTP POST handling with server URL parameter"""
    try:
        response = requests.post(
            server_url,
            json={"data": data},
            headers=HEADERS,
            timeout=5
        )
        print(f"➡️ Data sent to {server_url}: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {server_url}: {str(e)}")
        return False

def loop():
    """Main loop with fallback server logic"""
    try:
        while True:
            data = generate_sensor_data()
            print(f"Generated: {data}")
            
            # Try primary server first
            success = send_to_server(data, SERVER_URL)
            
            # If primary fails, try fallback to localhost
            if not success and SERVER_URL != DEFAULT_SERVER:
                print(f"⚠️ Trying fallback server: {DEFAULT_SERVER}")
                send_to_server(data, DEFAULT_SERVER)
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Termination signal received - Shutting down simulator")
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {str(e)}")
    finally:
        print("⭕ Simulation session ended")
        sys.exit(0)

if __name__ == "__main__":
    print(f"✅ Starting simulator (target server: {SERVER_URL}, fallback: {DEFAULT_SERVER})")
    print("Press Ctrl+C to stop...")
    loop()
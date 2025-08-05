import requests
import random
import time
import os
from datetime import datetime

# Configuration with environment variable fallback
DEFAULT_SERVER = "http://localhost:5000/upload"
SERVER_URL = os.getenv("SERVER_BASE_URL", "http://localhost:5000") + "/upload"
SEND_INTERVAL = 1  # seconds between transmissions

def generate_sensor_data():
    """Generate random sensor data similar to your device output"""
    data = {
        "temperature": round(random.uniform(20.0, 35.0), 1),
        "humidity": round(random.uniform(30.0, 80.0), 1),
        "latitude": round(random.uniform(0.000000, 50.000000), 6),
        "longitude": round(random.uniform(5.000000, 80.000000), 6),
        "timestamp": datetime.now().isoformat()
    }
    
    # Simulate occasional null values
    if random.random() < 0.1:
        data["temperature"] = None
        print("🌡️ Temperature sensor reading failed (simulated)")
    if random.random() < 0.1:
        data["humidity"] = None
        print("💧 Humidity sensor reading failed (simulated)")
    if random.random() < 0.3:
        data["latitude"] = None
        data["longitude"] = None
        print("🛰️ GPS signal lost (simulated)")
    
    return data

def send_data_to_server(data, server_url):
    """Send the simulated data to specified server"""
    try:
        headers = {'Content-Type': 'application/json'}
        print(f"📤 Preparing to send data to {server_url}...")
        response = requests.post(server_url, json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Data sent successfully!")
            print(f"   Server response: {response.text}")
        else:
            print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Server returned status {response.status_code}")
            print(f"   Response details: {response.text}")
            
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Connection failed - Server unreachable")
        return False
    except Exception as e:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Unexpected error: {str(e)}")
        return False

def main():
    print(f"🚀 Starting LoRa Data Simulator")
    print(f"   Primary server: {SERVER_URL}")
    print(f"   Fallback server: {DEFAULT_SERVER}")
    print(f"   Transmission interval: {SEND_INTERVAL} seconds")
    print("🛑 Press Ctrl+C to stop simulation\n")
    
    try:
        while True:
            print("\n" + "="*50)
            print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Generating new sensor data...")
            sensor_data = generate_sensor_data()
            print(f"📊 Generated data package:")
            print(f"   Temperature: {sensor_data['temperature']}°C")
            print(f"   Humidity: {sensor_data['humidity']}%")
            print(f"   Coordinates: ({sensor_data['latitude']}, {sensor_data['longitude']})")
            
            # Try primary server first
            success = send_data_to_server(sensor_data, SERVER_URL)
            
            # If primary fails, try fallback
            if not success and SERVER_URL != DEFAULT_SERVER:
                print(f"⚠️ Primary server failed, trying fallback: {DEFAULT_SERVER}")
                success = send_data_to_server(sensor_data, DEFAULT_SERVER)
                if not success:
                    print("🔴 Failed after fallback attempt - skipping this transmission")
            
            print(f"⏳ Next transmission in {SEND_INTERVAL} seconds...")
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Received termination signal")
    finally:
        print("\n🔴 Simulation session ended")
        print("✅ All systems shutdown cleanly")

if __name__ == "__main__":
    main()
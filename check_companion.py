#!/usr/bin/env python3
"""
Simple companion and CORS checker
"""

import requests
import json

def check_ports():
    ports = [8001, 8002, 8003, 8080]
    
    print("Checking companion on all ports...")
    print("=" * 40)
    
    working_ports = []
    
    for port in ports:
        try:
            url = f"http://127.0.0.1:{port}/health"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                print(f"PORT {port}: WORKING - {data.get('service', 'Active')}")
                
                # Check CORS
                cors = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
                print(f"  CORS: {cors}")
                
                working_ports.append(port)
                
        except Exception as e:
            print(f"PORT {port}: FAILED - {type(e).__name__}")
    
    print("=" * 40)
    
    if working_ports:
        print(f"WORKING PORTS: {working_ports}")
        print(f"USE PORT: {working_ports[0]}")
        print("")
        print("CHROME EXTENSION FIX:")
        print("1. Open chrome://extensions/")
        print("2. Click 'Inspect views: service worker'")
        print("3. In console run:")
        print(f"serviceWorker.localCompanionUrl = 'http://127.0.0.1:{working_ports[0]}';")
        print("4. Test connection:")
        print(f"fetch('http://127.0.0.1:{working_ports[0]}/health').then(r=>r.json()).then(console.log)")
    else:
        print("NO COMPANION FOUND!")
        print("Start with: python companion.py")

if __name__ == "__main__":
    check_ports()
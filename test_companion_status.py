#!/usr/bin/env python3
"""
Quick test to check companion status and CORS
"""

import requests
import json

def test_companion_ports():
    """Test all possible ports for the companion"""
    
    ports = [8001, 8002, 8003, 8080]
    found_ports = []
    
    print("🔍 Testing companion on all ports...")
    print("=" * 50)
    
    for port in ports:
        try:
            url = f"http://127.0.0.1:{port}/health"
            print(f"📡 Testing port {port}...")
            
            # Test basic GET request
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Port {port}: {data.get('service', data.get('status', 'Active'))}")
                
                # Check CORS headers
                cors_headers = {k: v for k, v in response.headers.items() 
                               if 'access-control' in k.lower()}
                
                if cors_headers:
                    print(f"   📋 CORS Headers: {json.dumps(cors_headers, indent=6)}")
                    found_ports.append(port)
                else:
                    print(f"   ⚠️  No CORS headers found")
                
                print()
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Port {port}: {type(e).__name__} - {e}")
    
    print("=" * 50)
    
    if found_ports:
        print(f"✅ Found working companion(s) on port(s): {found_ports}")
        print(f"💡 Extension should use port {found_ports[0]}")
        
        # Test CORS specifically
        test_port = found_ports[0]
        test_cors_specifically(test_port)
        
    else:
        print("❌ No working companion found!")
        print("🚨 Make sure to run: python companion.py")
    
    return found_ports

def test_cors_specifically(port):
    """Test CORS with Chrome extension headers"""
    
    print(f"\n🌐 Testing CORS for Chrome Extension on port {port}...")
    
    url = f"http://127.0.0.1:{port}/health"
    
    try:
        # Simulate Chrome extension request
        headers = {
            'Origin': 'chrome-extension://test',
            'User-Agent': 'Mozilla/5.0 Chrome Extension'
        }
        
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            print("✅ CORS test successful")
            
            # Check specific CORS headers
            origin_header = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
            methods_header = response.headers.get('Access-Control-Allow-Methods', 'NOT SET')
            
            print(f"   Access-Control-Allow-Origin: {origin_header}")
            print(f"   Access-Control-Allow-Methods: {methods_header}")
            
            if origin_header == '*':
                print("🎉 CORS correctly configured for all origins!")
            else:
                print("⚠️  CORS might not work for Chrome extensions")
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

if __name__ == "__main__":
    print("🧪 Companion Status & CORS Test")
    ports = test_companion_ports()
    
    if ports:
        print(f"\n🔧 TO FIX THE CHROME EXTENSION:")
        print(f"1. Open Chrome Extensions: chrome://extensions/")
        print(f"2. Click 'Inspect views: service worker' on Indeed extension")
        print(f"3. In console, run:")
        print(f"   serviceWorker.localCompanionUrl = 'http://127.0.0.1:{ports[0]}';")
        print(f"4. Test: fetch('http://127.0.0.1:{ports[0]}/health').then(r=>r.json()).then(console.log)")
    else:
        print(f"\n🚨 NO COMPANION RUNNING!")
        print(f"Start it with: python companion.py")
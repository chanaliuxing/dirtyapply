#!/usr/bin/env python3
"""
Port checker and companion launcher
"""

import socket
import os
import sys

def check_port(port, host='127.0.0.1'):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # True if available, False if in use
    except Exception:
        return False

def find_available_ports(start=8001, count=10):
    """Find available ports"""
    available = []
    for port in range(start, start + 20):
        if check_port(port):
            available.append(port)
            if len(available) >= count:
                break
    return available

def main():
    print("🔍 Indeed Automation - Port Checker")
    print("=" * 40)
    
    # Check common ports
    common_ports = [8001, 8080, 8000, 3000, 5000]
    
    print("Common ports status:")
    for port in common_ports:
        status = "✅ Available" if check_port(port) else "❌ In Use"
        print(f"  Port {port}: {status}")
    
    print("\nFinding available ports...")
    available = find_available_ports(8001, 5)
    
    if available:
        print("Available ports:")
        for port in available:
            print(f"  ✅ Port {port}")
        
        # Suggest using the first available port
        suggested_port = available[0]
        print(f"\n💡 Recommended: Use port {suggested_port}")
        print(f"   You can modify companion.py line with port=8001 to port={suggested_port}")
        
        # Offer to run companion on the suggested port
        if input(f"\n🚀 Run companion on port {suggested_port}? (y/n): ").lower() == 'y':
            # Check if companion.py exists
            if os.path.exists('companion.py'):
                # Read the file
                with open('companion.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the port
                modified_content = content.replace('port=8001', f'port={suggested_port}')
                
                # Write to a temporary file
                with open('companion_temp.py', 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                print(f"✅ Created companion_temp.py with port {suggested_port}")
                print("🔥 Run with: python companion_temp.py")
                
            else:
                print("❌ companion.py not found in current directory")
    
    else:
        print("❌ No available ports found in range 8001-8020")
        print("💡 Try closing other applications or restarting")

if __name__ == "__main__":
    main()
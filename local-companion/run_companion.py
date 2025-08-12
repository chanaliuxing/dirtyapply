#!/usr/bin/env python3
"""
Alternative launcher for the local companion with automatic port detection
"""

import socket
import subprocess
import sys
import time

def find_free_port(start_port=8001, max_port=8020):
    """Find a free port starting from start_port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def main():
    print("🚀 Starting Indeed Automation Local Companion...")
    
    # Find a free port
    free_port = find_free_port()
    if not free_port:
        print("❌ ERROR: No free ports available between 8001-8020")
        print("💡 Try closing other applications or restarting your computer")
        return 1
    
    print(f"✅ Using port: {free_port}")
    
    # Check if companion.py exists
    import os
    if not os.path.exists("companion.py"):
        print("❌ ERROR: companion.py not found in current directory")
        print("💡 Make sure you're in the local-companion folder")
        return 1
    
    # Start the companion with the free port
    try:
        # Modify the port in the command
        cmd = [
            sys.executable, "-c", 
            f"""
import sys
sys.path.insert(0, '.')

# Read companion.py and modify port
with open('companion.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the port
code = code.replace('port=8001', 'port={free_port}')

# Execute the modified code
exec(code)
"""
        ]
        
        print(f"🔥 Local Companion starting on http://127.0.0.1:{free_port}")
        print("📝 Available endpoints:")
        print(f"   • Health check: GET http://127.0.0.1:{free_port}/health")
        print(f"   • Click: POST http://127.0.0.1:{free_port}/click")
        print(f"   • Type: POST http://127.0.0.1:{free_port}/type")
        print(f"   • Screenshot: POST http://127.0.0.1:{free_port}/screenshot")
        print("⚠️  Press Ctrl+C to stop")
        print("-" * 50)
        
        # Run the companion
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping Local Companion...")
        return 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("💡 Try running: python companion.py directly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
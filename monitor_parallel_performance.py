#!/usr/bin/env python3
"""
Real-time Performance Monitor for Parallel Processing
Monitors queue status and system performance in real-time
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
STATUS_ENDPOINT = "/api/v1/status/queue"

def get_queue_status():
    """Get current queue status"""
    try:
        response = requests.get(f"{BASE_URL}{STATUS_ENDPOINT}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def format_queue_status(status_data):
    """Format queue status for display"""
    if "error" in status_data:
        return f"❌ Error: {status_data['error']}"
    
    queue_info = status_data.get("queue_info", {})
    
    lines = [
        f"🔄 Queue Size: {queue_info.get('queue_size', 'N/A')}/{queue_info.get('max_queue_size', 'N/A')}",
        f"👷 Active Workers: {queue_info.get('running_tasks', 'N/A')}/{queue_info.get('max_workers', 'N/A')}",
        f"✅ Completed: {queue_info.get('completed_tasks', 'N/A')}",
        f"❌ Failed: {queue_info.get('failed_tasks', 'N/A')}",
        f"🚀 Status: {'Running' if queue_info.get('is_running') else 'Stopped'}",
        f"📊 Total Results: {queue_info.get('total_results', 'N/A')}"
    ]
    
    return " | ".join(lines)

def monitor_performance(refresh_interval=2, duration=60):
    """Monitor performance for specified duration"""
    print("🎯 Fashion AI Parallel Processing Monitor")
    print("=" * 80)
    print(f"📡 Monitoring {BASE_URL}")
    print(f"⏰ Refresh Interval: {refresh_interval}s")
    print(f"⌛ Duration: {duration}s")
    print("=" * 80)
    print()
    
    start_time = time.time()
    iteration = 0
    
    try:
        while time.time() - start_time < duration:
            iteration += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Get status
            status = get_queue_status()
            status_line = format_queue_status(status)
            
            # Clear line and print status
            print(f"\r[{current_time}] #{iteration:03d} | {status_line}", end="", flush=True)
            
            # Sleep for refresh interval
            time.sleep(refresh_interval)
            
        print("\n")
        print("✅ Monitoring completed")
        
    except KeyboardInterrupt:
        print("\n")
        print("🛑 Monitoring stopped by user")

def check_system_health():
    """Perform a quick system health check"""
    print("🏥 System Health Check")
    print("=" * 40)
    
    # Check API availability
    try:
        status = get_queue_status()
        if "error" not in status:
            print("✅ API Server: Online")
            print("✅ Queue System: Running")
            
            queue_info = status.get("queue_info", {})
            if queue_info.get("is_running"):
                print("✅ Task Workers: Active")
            else:
                print("❌ Task Workers: Stopped")
                
            if queue_info.get("max_workers", 0) > 0:
                print(f"✅ Worker Pool: {queue_info['max_workers']} workers available")
            else:
                print("⚠️ Worker Pool: No workers configured")
                
        else:
            print("❌ Queue System: Error")
            print(f"   Error: {status['error']}")
            
    except Exception as e:
        print("❌ API Server: Offline")
        print(f"   Error: {e}")
    
    print()

def show_usage():
    """Show usage instructions"""
    print("""
🔧 Fashion AI Performance Monitor Usage:

Commands:
  python monitor_parallel_performance.py health    - Quick health check
  python monitor_parallel_performance.py monitor   - Start real-time monitoring (60s)
  python monitor_parallel_performance.py watch     - Continuous monitoring
  
Examples:
  python monitor_parallel_performance.py health
  python monitor_parallel_performance.py monitor
  
Make sure your Fashion AI server is running:
  python -m uvicorn app.main:app --reload
    """)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "health":
        check_system_health()
    elif command == "monitor":
        check_system_health()
        print("Starting real-time monitoring...")
        monitor_performance(refresh_interval=2, duration=60)
    elif command == "watch":
        check_system_health()
        print("Starting continuous monitoring (Press Ctrl+C to stop)...")
        monitor_performance(refresh_interval=1, duration=float('inf'))
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()
        sys.exit(1)

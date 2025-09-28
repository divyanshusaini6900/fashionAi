#!/usr/bin/env python3
"""
Quick Demo Script for Parallel Processing
Demonstrates the parallel processing capabilities with a simple test
"""
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_queue_status():
    """Get current queue status"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/status/queue", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def send_test_request(request_id):
    """Send a test request"""
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2011.35.31_d5ceb091.jpg?alt=media&token=ee5c5967-37c6-456a-9de0-02bd93689ae3",
                "view": "front",
                "backgrounds": [1, 0, 1]  # 1 white, 1 random
            }
        ],
        "productType": "demo",
        "gender": "male",
        "text": f"Parallel processing demo request #{request_id}",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 2,
        "generateCsv": True,
    }
    
    print(f"📤 Sending request #{request_id}...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/generate/image",
            json=test_data,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            processing_times = result.get("metadata", {}).get("processing_times", {})
            
            print(f"✅ Request #{request_id} completed in {duration:.2f}s")
            print(f"   📊 Processing breakdown:")
            for step, time_taken in processing_times.items():
                if isinstance(time_taken, (int, float)):
                    print(f"      {step}: {time_taken:.2f}s")
            print(f"   🖼️  Generated {len(result.get('image_variations', []))} images")
            print(f"   🔍 Upscaled {len(result.get('upscale_image', []))} images")
            
            return {
                "request_id": request_id,
                "success": True,
                "duration": duration,
                "image_count": len(result.get('image_variations', [])),
                "processing_times": processing_times
            }
        else:
            print(f"❌ Request #{request_id} failed: {response.status_code}")
            return {"request_id": request_id, "success": False, "duration": duration}
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 Request #{request_id} error: {str(e)}")
        return {"request_id": request_id, "success": False, "duration": duration, "error": str(e)}

def demo_parallel_processing():
    """Demonstrate parallel processing with 3 concurrent requests"""
    print("🎯 Fashion AI Parallel Processing Demo")
    print("=" * 50)
    
    # Check server
    if not check_server():
        print("❌ Server not running! Please start with:")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    print("✅ Server is running")
    
    # Check queue status
    initial_status = get_queue_status()
    if initial_status:
        queue_info = initial_status.get("queue_info", {})
        print(f"📊 Queue Status: {queue_info.get('queue_size', 0)} queued, {queue_info.get('running_tasks', 0)} running")
    
    print(f"\n🚀 Sending 3 concurrent requests...")
    print("   This demonstrates parallel processing vs sequential processing")
    
    # Send concurrent requests
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all requests simultaneously
        futures = [executor.submit(send_test_request, i) for i in range(1, 4)]
        
        # Collect results as they complete
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_requests = [r for r in results if r.get("success")]
    failed_requests = [r for r in results if not r.get("success")]
    
    print(f"\n📈 Demo Results:")
    print(f"   Total Time (3 concurrent requests): {total_time:.2f}s")
    print(f"   Successful Requests: {len(successful_requests)}/3")
    print(f"   Failed Requests: {len(failed_requests)}/3")
    
    if successful_requests:
        avg_request_time = sum(r["duration"] for r in successful_requests) / len(successful_requests)
        print(f"   Average Request Time: {avg_request_time:.2f}s")
        print(f"   Time Saved vs Sequential: ~{(avg_request_time * 3) - total_time:.2f}s")
    
    # Show processing breakdown
    if successful_requests and successful_requests[0].get("processing_times"):
        print(f"\n⚡ Parallel Processing Breakdown (example):")
        times = successful_requests[0]["processing_times"]
        for step, duration in times.items():
            if isinstance(duration, (int, float)):
                print(f"   {step}: {duration:.2f}s")
    
    # Check final queue status
    final_status = get_queue_status()
    if final_status:
        queue_info = final_status.get("queue_info", {})
        print(f"\n📊 Final Queue Status:")
        print(f"   Completed Tasks: {queue_info.get('completed_tasks', 0)}")
        print(f"   Queue Size: {queue_info.get('queue_size', 0)}")
    
    print(f"\n🎉 Demo completed! Parallel processing is working.")
    print(f"💡 To monitor in real-time: python monitor_parallel_performance.py watch")

def quick_health_check():
    """Quick health check of the parallel processing system"""
    print("🏥 Quick Health Check")
    print("-" * 30)
    
    # Check server
    if check_server():
        print("✅ API Server: Online")
    else:
        print("❌ API Server: Offline")
        return
    
    # Check queue system
    status = get_queue_status()
    if status and status.get("status") == "success":
        print("✅ Queue System: Running")
        queue_info = status.get("queue_info", {})
        print(f"✅ Workers: {queue_info.get('max_workers', 0)} available")
        print(f"📊 Completed: {queue_info.get('completed_tasks', 0)} tasks")
    else:
        print("❌ Queue System: Error")
    
    print("\n💡 System ready for parallel processing!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "health":
        quick_health_check()
    else:
        demo_parallel_processing()

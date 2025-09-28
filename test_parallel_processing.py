#!/usr/bin/env python3
"""
Comprehensive Test Script for Parallel Processing
Tests the Fashion AI system with multiple concurrent requests
"""
import requests
import asyncio
import aiohttp
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
IMAGE_ENDPOINT = "/api/v1/generate/image"
STATUS_ENDPOINT = "/api/v1/status/queue"

# Test data
TEST_DATA = {
    "inputImages": [
        {
            "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2011.35.31_d5ceb091.jpg?alt=media&token=ee5c5967-37c6-456a-9de0-02bd93689ae3",
            "view": "front",
            "backgrounds": [0, 1, 1]  # 1 plain, 1 random
        }
    ],
    "productType": "general",
    "gender": "male",
    "text": "Test parallel processing",
    "isVideo": False,
    "upscale": True,
    "numberOfOutputs": 2,
    "generateCsv": True,
}

class ParallelProcessingTester:
    """Test suite for parallel processing capabilities"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.results = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=20)
        timeout = aiohttp.ClientTimeout(total=600)  # 10 minute timeout
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            async with self.session.get(f"{self.base_url}{STATUS_ENDPOINT}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status code: {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_single_request(self, request_id: int, test_data: Dict) -> Dict[str, Any]:
        """Send a single API request"""
        start_time = time.time()
        
        try:
            # Modify test data for uniqueness
            modified_data = test_data.copy()
            modified_data["text"] = f"Parallel test request #{request_id}"
            
            print(f"📤 Request {request_id}: Sending...")
            
            async with self.session.post(
                f"{self.base_url}{IMAGE_ENDPOINT}",
                json=modified_data
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Request {request_id}: Success in {response_time:.2f}s")
                    
                    return {
                        "request_id": request_id,
                        "status": "success",
                        "response_time": response_time,
                        "result": result,
                        "image_count": len(result.get("image_variations", [])),
                        "upscaled_count": len(result.get("upscale_image", [])),
                        "has_excel": bool(result.get("excel_report_url")),
                        "processing_times": result.get("metadata", {}).get("processing_times", {})
                    }
                else:
                    error_text = await response.text()
                    print(f"❌ Request {request_id}: Failed with status {response.status}")
                    
                    return {
                        "request_id": request_id,
                        "status": "failed",
                        "response_time": response_time,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            response_time = time.time() - start_time
            print(f"💥 Request {request_id}: Exception after {response_time:.2f}s - {e}")
            
            return {
                "request_id": request_id,
                "status": "exception", 
                "response_time": response_time,
                "error": str(e)
            }
    
    async def run_concurrent_test(self, num_requests: int = 5) -> Dict[str, Any]:
        """Run multiple concurrent requests"""
        print(f"\n🚀 Starting concurrent test with {num_requests} requests")
        print("=" * 60)
        
        # Check initial queue status
        initial_status = await self.get_queue_status()
        print(f"📊 Initial Queue Status: {json.dumps(initial_status, indent=2)}")
        
        # Send all requests concurrently
        start_time = time.time()
        tasks = [
            self.send_single_request(i, TEST_DATA) 
            for i in range(1, num_requests + 1)
        ]
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Process results
        successful_requests = []
        failed_requests = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_requests.append({"error": str(result)})
            elif result.get("status") == "success":
                successful_requests.append(result)
            else:
                failed_requests.append(result)
        
        # Check final queue status
        final_status = await self.get_queue_status()
        print(f"\n📊 Final Queue Status: {json.dumps(final_status, indent=2)}")
        
        return {
            "total_requests": num_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "total_time": total_time,
            "average_time": total_time / num_requests,
            "requests_per_second": num_requests / total_time,
            "successful_results": successful_requests,
            "failed_results": failed_requests,
            "initial_queue_status": initial_status,
            "final_queue_status": final_status
        }
    
    def print_detailed_results(self, test_results: Dict[str, Any]):
        """Print detailed test results"""
        print("\n" + "=" * 80)
        print("🎯 PARALLEL PROCESSING TEST RESULTS")
        print("=" * 80)
        
        # Summary
        print(f"\n📈 SUMMARY:")
        print(f"   Total Requests: {test_results['total_requests']}")
        print(f"   Successful: {test_results['successful_requests']}")
        print(f"   Failed: {test_results['failed_requests']}")
        print(f"   Success Rate: {(test_results['successful_requests'] / test_results['total_requests']) * 100:.1f}%")
        print(f"   Total Time: {test_results['total_time']:.2f}s")
        print(f"   Average Time per Request: {test_results['average_time']:.2f}s")
        print(f"   Requests per Second: {test_results['requests_per_second']:.2f}")
        
        # Detailed successful results
        if test_results['successful_results']:
            print(f"\n✅ SUCCESSFUL REQUESTS ({len(test_results['successful_results'])}):")
            for i, result in enumerate(test_results['successful_results'], 1):
                print(f"   {i}. Request #{result['request_id']}")
                print(f"      Response Time: {result['response_time']:.2f}s")
                print(f"      Images Generated: {result['image_count']}")
                print(f"      Upscaled Images: {result['upscaled_count']}")
                print(f"      Excel Report: {'✅' if result['has_excel'] else '❌'}")
                
                # Show processing times if available
                if result.get('processing_times'):
                    times = result['processing_times']
                    print(f"      Processing Breakdown:")
                    for step, duration in times.items():
                        if isinstance(duration, (int, float)):
                            print(f"        {step}: {duration:.2f}s")
                print()
        
        # Failed requests
        if test_results['failed_results']:
            print(f"\n❌ FAILED REQUESTS ({len(test_results['failed_results'])}):")
            for i, result in enumerate(test_results['failed_results'], 1):
                print(f"   {i}. Request #{result.get('request_id', 'Unknown')}")
                print(f"      Error: {result.get('error', 'Unknown error')}")
                print(f"      Response Time: {result.get('response_time', 0):.2f}s")
                print()
        
        # Queue status analysis
        initial_queue = test_results.get('initial_queue_status', {}).get('queue_info', {})
        final_queue = test_results.get('final_queue_status', {}).get('queue_info', {})
        
        if initial_queue or final_queue:
            print(f"\n🔄 QUEUE SYSTEM ANALYSIS:")
            print(f"   Initial Queue Size: {initial_queue.get('queue_size', 'N/A')}")
            print(f"   Final Queue Size: {final_queue.get('queue_size', 'N/A')}")
            print(f"   Max Workers: {initial_queue.get('max_workers', 'N/A')}")
            print(f"   Total Completed Tasks: {final_queue.get('completed_tasks', 'N/A')}")
            print(f"   Total Failed Tasks: {final_queue.get('failed_tasks', 'N/A')}")
        
        print("\n" + "=" * 80)
    
    async def run_stress_test(self, num_requests: int = 10) -> Dict[str, Any]:
        """Run stress test with many concurrent requests"""
        print(f"\n💪 STRESS TEST with {num_requests} concurrent requests")
        
        # Check system before stress test
        initial_status = await self.get_queue_status()
        
        # Run the test
        start_time = time.time()
        results = await self.run_concurrent_test(num_requests)
        
        # Calculate stress test specific metrics
        results['stress_test_metrics'] = {
            'requests_handled_concurrently': num_requests,
            'system_stability': results['successful_requests'] >= num_requests * 0.8,  # 80% success rate
            'performance_acceptable': results['average_time'] < 300,  # Less than 5 minutes average
            'queue_system_working': initial_status.get('status') == 'success'
        }
        
        return results

def run_sync_test(num_requests: int = 3):
    """Synchronous version using requests library for comparison"""
    print(f"\n🔄 SYNCHRONOUS TEST with {num_requests} requests (for comparison)")
    
    results = []
    start_time = time.time()
    
    for i in range(1, num_requests + 1):
        request_start = time.time()
        
        try:
            modified_data = TEST_DATA.copy()
            modified_data["text"] = f"Sync test request #{i}"
            
            print(f"📤 Sync Request {i}: Sending...")
            
            response = requests.post(
                f"{BASE_URL}{IMAGE_ENDPOINT}",
                json=modified_data,
                timeout=600
            )
            
            request_time = time.time() - request_start
            
            if response.status_code == 200:
                print(f"✅ Sync Request {i}: Success in {request_time:.2f}s")
                results.append({
                    "request_id": i,
                    "status": "success",
                    "response_time": request_time
                })
            else:
                print(f"❌ Sync Request {i}: Failed with status {response.status_code}")
                results.append({
                    "request_id": i,
                    "status": "failed",
                    "response_time": request_time
                })
                
        except Exception as e:
            request_time = time.time() - request_start
            print(f"💥 Sync Request {i}: Exception - {e}")
            results.append({
                "request_id": i,
                "status": "exception",
                "response_time": request_time,
                "error": str(e)
            })
    
    total_time = time.time() - start_time
    
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n📊 Synchronous Test Results:")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Successful: {successful}/{num_requests}")
    print(f"   Average Time: {total_time/num_requests:.2f}s")
    
    return results

async def main():
    """Main test function"""
    print("🧪 Fashion AI Parallel Processing Test Suite")
    print("=" * 60)
    
    # Test 1: Basic concurrent test
    async with ParallelProcessingTester(BASE_URL) as tester:
        print("\n🎯 Test 1: Basic Concurrent Processing (5 requests)")
        basic_results = await tester.run_concurrent_test(5)
        tester.print_detailed_results(basic_results)
        
        # Test 2: Stress test
        print("\n🎯 Test 2: Stress Test (8 requests)")
        stress_results = await tester.run_stress_test(8)
        tester.print_detailed_results(stress_results)
        
        # Show stress test specific results
        stress_metrics = stress_results.get('stress_test_metrics', {})
        print(f"\n💪 STRESS TEST ANALYSIS:")
        print(f"   System Stability: {'✅ PASS' if stress_metrics.get('system_stability') else '❌ FAIL'}")
        print(f"   Performance Acceptable: {'✅ PASS' if stress_metrics.get('performance_acceptable') else '❌ FAIL'}")
        print(f"   Queue System Working: {'✅ PASS' if stress_metrics.get('queue_system_working') else '❌ FAIL'}")
    
    # Test 3: Synchronous comparison (optional)
    print("\n🎯 Test 3: Synchronous Comparison")
    sync_results = run_sync_test(2)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    print("🚀 Starting Fashion AI Parallel Processing Tests...")
    print("💡 Make sure the server is running: python -m uvicorn app.main:app --reload")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()

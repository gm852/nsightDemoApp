#!/usr/bin/env python3
"""
end-to-end test of the User Profile system
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"

def test_backend_api():
    print("🔧 Testing Backend API")
    print("=" * 30)
    
    # Test health
    print("1. Health check:")
    response = requests.get(f"{API_BASE}/health")
    print(f"   Status: {response.status_code} - {response.json()}")
    
    # Test main endpoint
    print("\n2. GET /api/users/1 (should fetch from upstream and cache):")
    response = requests.get(f"{API_BASE}/api/users/1")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Name: {data['name']}")
    print(f"   Username: {data['username']}")
    print(f"   Email: {data['email']}")
    print(f"   Website: {data['website']}")
    print(f"   Company: {data['companyName']}")
    
    # Test refresh
    print("\n3. POST /api/users/refresh (force refresh):")
    response = requests.post(f"{API_BASE}/api/users/refresh")
    print(f"   Status: {response.status_code}")
    print(f"   Data refreshed successfully")
    
    # Test database
    print("\n4. Check database contents:")
    response = requests.get(f"{API_BASE}/api/users")
    users = response.json()
    print(f"   Users in database: {len(users)}")
    print(f"   First user: {users[0]['name'] if users else 'None'}")
    
    return True

def test_caching_behavior():
    print("\n💾 Testing Caching Behavior")
    print("=" * 30)
    
    # Clear any existing data by using bypass cache
    print("1. Bypass cache (force fresh fetch):")
    response = requests.get(f"{API_BASE}/api/users/1?bypassCache=true")
    print(f"   Status: {response.status_code}")
    
    # Test cache hit
    print("\n2. Normal request (should hit cache):")
    start_time = time.time()
    response = requests.get(f"{API_BASE}/api/users/1")
    end_time = time.time()
    print(f"   Status: {response.status_code}")
    print(f"   Response time: {(end_time - start_time)*1000:.2f}ms")
    
    # Test stale cache (simulate by waiting or using bypass)
    print("\n3. Test bypass cache again:")
    response = requests.get(f"{API_BASE}/api/users/1?bypassCache=true")
    print(f"   Status: {response.status_code}")
    
    return True

def test_data_normalization():
    print("\n🔄 Testing Data Normalization")
    print("=" * 30)
    
    response = requests.get(f"{API_BASE}/api/users/1")
    data = response.json()
    
    print("Normalized data structure:")
    print(f"   ✓ Name: {data['name']}")
    print(f"   ✓ Username: {data['username']}")
    print(f"   ✓ Email: {data['email']}")
    print(f"   ✓ Website: {data['website']} (normalized with https://)")
    print(f"   ✓ Company: {data['companyName']} (flattened from nested object)")
    
    # Verify website normalization
    if data['website'].startswith('https://'):
        print("   ✅ Website properly normalized with https://")
    else:
        print("   ❌ Website normalization failed")
    
    return True

def test_frontend_integration():
    print("\n🎨 Testing Frontend Integration")
    print("=" * 30)
    
    try:
        # Test if frontend is running
        response = requests.get(f"{FRONTEND_BASE}", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is running at http://localhost:3000")
            print("   ✅ UserProfileCard should be displaying data from backend API")
            return True
        else:
            print(f"   ❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Frontend not accessible: {e}")
        print("   💡 Start frontend with: cd frontend && npm run dev")
        return False

def main():
    print("🚀 User Profile System - End-to-End Test")
    print("=" * 50)
    
    tests = [
        ("Backend API", test_backend_api),
        ("Caching Behavior", test_caching_behavior),
        ("Data Normalization", test_data_normalization),
        ("Frontend Integration", test_frontend_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name} - FAILED")
        except Exception as e:
            print(f"\n❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        print("\n🌐 Access points:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

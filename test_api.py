#!/usr/bin/env python3
"""
Test script for the User Profile API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_user():
    """Test GET /api/users/1 endpoint"""
    print("Testing GET /api/users/1...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/1")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /api/users/1 passed")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ GET /api/users/1 failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /api/users/1 error: {e}")
        return False

def test_refresh_user():
    """Test POST /api/users/refresh endpoint"""
    print("Testing POST /api/users/refresh...")
    try:
        response = requests.post(f"{BASE_URL}/api/users/refresh")
        if response.status_code == 200:
            data = response.json()
            print("✅ POST /api/users/refresh passed")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ POST /api/users/refresh failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ POST /api/users/refresh error: {e}")
        return False

def test_bypass_cache():
    """Test GET /api/users/1?bypassCache=true endpoint"""
    print("Testing GET /api/users/1?bypassCache=true...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/1?bypassCache=true")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /api/users/1?bypassCache=true passed")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ GET /api/users/1?bypassCache=true failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /api/users/1?bypassCache=true error: {e}")
        return False

def main():
    print("🚀 Starting User Profile API tests...")
    print("=" * 50)
    
    tests = [
        test_health,
        test_get_user,
        test_refresh_user,
        test_bypass_cache
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())


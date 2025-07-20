#!/usr/bin/env python3
"""Test login by directly calling the login function"""
import requests
import json

def test_with_different_formats():
    """Test login with different request formats"""
    print("🧪 Testing Different Login Formats...")
    
    formats_to_test = [
        {
            "name": "JSON with Content-Type header",
            "url": "http://localhost:8000/auth/login",
            "headers": {"Content-Type": "application/json"},
            "data": json.dumps({"username": "eip@iug.net", "password": "1234Abcd!"})
        },
        {
            "name": "Raw JSON",
            "url": "http://localhost:8000/auth/login", 
            "headers": {},
            "data": '{"username": "eip@iug.net", "password": "1234Abcd!"}'
        },
        {
            "name": "Form data",
            "url": "http://localhost:8000/auth/login",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": "username=eip@iug.net&password=1234Abcd!"
        }
    ]
    
    for test_case in formats_to_test:
        print(f"\n   Testing: {test_case['name']}")
        try:
            response = requests.post(
                test_case["url"],
                headers=test_case["headers"],
                data=test_case["data"],
                timeout=5
            )
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"      Token: {data.get('token', 'Not found')[:30]}...")
                    return True
                except:
                    print(f"      Response: {response.text[:100]}")
                    return True
            else:
                print(f"      ❌ Failed")
                try:
                    error = response.json()
                    print(f"      Error: {error}")
                except:
                    print(f"      Raw: {response.text[:100]}")
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    return False

def test_user_registration():
    """Test if we can register a new user to verify the system works"""
    print("\n📝 Testing User Registration...")
    
    test_user = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "viewer"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/register",
            json=test_user,
            timeout=5
        )
        
        print(f"   Registration status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Registration successful")
            
            # Now try to login with test user
            login_response = requests.post(
                "http://localhost:8000/auth/login",
                json={"username": "test@example.com", "password": "testpass123"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Test user login status: {login_response.status_code}")
            if login_response.status_code == 200:
                print("   ✅ Test user login successful - auth system works!")
                return True
            else:
                print(f"   ❌ Test user login failed: {login_response.text}")
                return False
        else:
            try:
                error = response.json()
                print(f"   ❌ Registration failed: {error}")
            except:
                print(f"   ❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False

def main():
    """Test login functionality"""
    print("🔐 DIRECT LOGIN TESTING")
    print("=" * 50)
    
    # Test different formats
    format_success = test_with_different_formats()
    
    if not format_success:
        # Test with new user registration
        reg_success = test_user_registration()
        return reg_success
    else:
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""Test Edward's login functionality"""
import requests
import json
import bcrypt
import psycopg2

def test_password_verification():
    """Test that stored password matches what we expect"""
    print("🔍 Testing Password Verification...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="epic_v11", 
            user="epic_admin",
            password="epic_secure_pass",
            port="5432"
        )
        
        cur = conn.cursor()
        cur.execute("SELECT email, password_hash FROM users WHERE email = %s", ("eip@iug.net",))
        result = cur.fetchone()
        
        if result:
            email, stored_hash = result
            test_password = "1234Abcd!"
            
            # Check if password matches
            matches = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"   Email: {email}")
            print(f"   Stored hash: {stored_hash[:50]}...")
            print(f"   Password matches: {matches}")
            
            if not matches:
                print("   ❌ Password does not match stored hash")
                return False
            else:
                print("   ✅ Password matches stored hash")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_api_login():
    """Test API login with Edward's credentials"""
    print("\n🔐 Testing API Login...")
    
    login_data = {
        "username": "eip@iug.net",
        "password": "1234Abcd!"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful!")
            print(f"   Access token: {data.get('access_token', 'Not found')[:50]}...")
            print(f"   Token type: {data.get('token_type', 'Not found')}")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")
        return False

def test_user_status():
    """Check user account status"""
    print("\n👤 Checking User Account Status...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="epic_v11",
            user="epic_admin", 
            password="epic_secure_pass",
            port="5432"
        )
        
        cur = conn.cursor()
        cur.execute("""
            SELECT email, role, is_active, failed_login_attempts, locked_until
            FROM users WHERE email = %s
        """, ("eip@iug.net",))
        
        result = cur.fetchone()
        if result:
            email, role, is_active, failed_attempts, locked_until = result
            print(f"   Email: {email}")
            print(f"   Role: {role}")
            print(f"   Active: {is_active}")
            print(f"   Failed attempts: {failed_attempts}")
            print(f"   Locked until: {locked_until}")
            
            if not is_active:
                print("   ❌ Account is not active")
                return False
            elif locked_until:
                print("   ❌ Account is locked")
                return False
            else:
                print("   ✅ Account is active and unlocked")
                return True
        else:
            print("   ❌ User not found")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def main():
    """Run all Edward login tests"""
    print("🧪 EDWARD LOGIN TESTING")
    print("=" * 50)
    
    tests = [
        ("Password Verification", test_password_verification),
        ("User Account Status", test_user_status), 
        ("API Login", test_api_login)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Edward login fully functional!")
        return True
    else:
        print("❌ Edward login has issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
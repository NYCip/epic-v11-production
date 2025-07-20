#!/usr/bin/env python3
"""Test Edward's authentication directly"""
import sys
import os
sys.path.append('/home/epic/epic11/control_panel_backend')
sys.path.append('/home/epic/epic11/testing')

from passlib.context import CryptContext
import psycopg2

def test_password_hash():
    """Test if password hashing works"""
    print("🔐 Testing password hashing...")
    
    # Get the hash from database
    db_hash = "$2a$06$S3rMghuHvMR4mGKzTY6X2elvLDk3bKbisaZ0ciFLig06MtZkilbHS"
    test_password = "1234Abcd!"
    
    # Test with passlib
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    result = pwd_context.verify(test_password, db_hash)
    
    print(f"Password verification result: {result}")
    return result

def test_database_connection():
    """Test database connection and user lookup"""
    print("\n💾 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="epic_v11", 
            user="epic_user",
            password="epic_secure_pass",
            port="5432"
        )
        
        cur = conn.cursor()
        cur.execute("SELECT email, password_hash, role FROM users WHERE email = %s", ("eip@iug.net",))
        result = cur.fetchone()
        
        if result:
            email, password_hash, role = result
            print(f"✅ User found: {email} ({role})")
            print(f"Password hash: {password_hash[:20]}...")
            
            # Test password verification
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            pwd_ok = pwd_context.verify("1234Abcd!", password_hash)
            print(f"Password verification: {'✅ PASS' if pwd_ok else '❌ FAIL'}")
            
            conn.close()
            return True
        else:
            print("❌ User not found")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_simple_login():
    """Test login with a simple requests call"""
    print("\n👤 Testing simple login...")
    
    import requests
    
    try:
        # Try different formats
        formats = [
            {
                "method": "form",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "data": "username=eip@iug.net&password=1234Abcd!"
            },
            {
                "method": "json", 
                "headers": {"Content-Type": "application/json"},
                "data": '{"username":"eip@iug.net","password":"1234Abcd!"}'
            }
        ]
        
        for fmt in formats:
            print(f"  Trying {fmt['method']} format...")
            
            if fmt['method'] == 'form':
                response = requests.post(
                    "http://localhost:8000/auth/login",
                    headers=fmt['headers'],
                    data=fmt['data'],
                    timeout=10
                )
            else:
                response = requests.post(
                    "http://localhost:8000/auth/login", 
                    headers=fmt['headers'],
                    data=fmt['data'],
                    timeout=10
                )
            
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    print(f"    ✅ SUCCESS! Token: {data['access_token'][:30]}...")
                    return True
                else:
                    print(f"    ❌ No token in response: {data}")
            else:
                try:
                    error = response.json()
                    print(f"    ❌ Error: {error.get('detail', 'Unknown')}")
                except:
                    print(f"    ❌ Raw error: {response.text[:100]}...")
                    
    except Exception as e:
        print(f"❌ Login test error: {e}")
    
    return False

def main():
    """Main test"""
    print("🔍 EDWARD AUTHENTICATION DIAGNOSTIC")
    print("=" * 40)
    
    # Test individual components
    pwd_ok = test_password_hash()
    db_ok = test_database_connection()
    login_ok = test_simple_login()
    
    print("\n" + "=" * 40)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 40)
    print(f"Password Hashing: {'✅' if pwd_ok else '❌'}")
    print(f"Database Access: {'✅' if db_ok else '❌'}")
    print(f"Login Endpoint: {'✅' if login_ok else '❌'}")
    
    if all([pwd_ok, db_ok, login_ok]):
        print("\n🎉 All authentication components working!")
        return True
    else:
        print("\n⚠️ Some authentication issues found")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
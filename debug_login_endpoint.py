#!/usr/bin/env python3
"""Debug the login endpoint directly"""
import sys
import os
sys.path.append('/home/epic/epic11/control_panel_backend/app')

import psycopg2
from auth import verify_password
from passlib.context import CryptContext

def debug_database_connection():
    """Test direct database query like the app does"""
    print("🔍 Testing Database Query...")
    
    try:
        # Use the same connection as the app
        conn = psycopg2.connect(
            host="localhost",
            database="epic_v11",
            user="epic_user",  # App uses epic_user
            password="epic_secure_pass",
            port="5432"
        )
        
        cur = conn.cursor()
        cur.execute("SELECT email, password_hash FROM users WHERE email = %s", ("eip@iug.net",))
        result = cur.fetchone()
        
        if result:
            email, password_hash = result
            print(f"   ✅ Found user: {email}")
            print(f"   Hash: {password_hash[:50]}...")
            
            # Test verification using app's function
            test_password = "1234Abcd!"
            matches = verify_password(test_password, password_hash)
            print(f"   App verify_password result: {matches}")
            
            conn.close()
            return matches
        else:
            print("   ❌ User not found with app database connection")
            conn.close()
            return False
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("   This might be why the login is failing!")
        return False

def test_json_parsing():
    """Test JSON parsing like the endpoint does"""
    print("\n📝 Testing JSON Parsing...")
    
    import json
    from pydantic import BaseModel
    
    class UserLogin(BaseModel):
        username: str
        password: str
    
    test_json = '{"username": "eip@iug.net", "password": "1234Abcd!"}'
    
    try:
        data = json.loads(test_json)
        login_data = UserLogin(**data)
        print(f"   ✅ JSON parsed successfully")
        print(f"   Username: {login_data.username}")
        print(f"   Password: {login_data.password}")
        return True
    except Exception as e:
        print(f"   ❌ JSON parsing failed: {e}")
        return False

def main():
    """Run login debugging"""
    print("🐛 LOGIN ENDPOINT DEBUGGING")
    print("=" * 50)
    
    json_ok = test_json_parsing()
    db_ok = debug_database_connection()
    
    if json_ok and db_ok:
        print("\n✅ All components working - login should succeed")
        print("❓ Issue might be in request format or endpoint routing")
        return True
    else:
        print("\n❌ Found issues that prevent login")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
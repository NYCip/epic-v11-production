#!/usr/bin/env python3
"""Debug authentication system"""
import sys
import os
import bcrypt
import psycopg2
from passlib.context import CryptContext

def test_passlib_vs_bcrypt():
    """Test if passlib and bcrypt produce compatible hashes"""
    print("🔧 Testing Password Hash Compatibility...")
    
    password = "1234Abcd!"
    
    # Create bcrypt hash directly
    bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"   bcrypt hash: {bcrypt_hash}")
    
    # Create passlib hash (like the app uses)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    passlib_hash = pwd_context.hash(password)
    print(f"   passlib hash: {passlib_hash}")
    
    # Test verification
    bcrypt_verifies_bcrypt = bcrypt.checkpw(password.encode('utf-8'), bcrypt_hash.encode('utf-8'))
    passlib_verifies_bcrypt = pwd_context.verify(password, bcrypt_hash)
    passlib_verifies_passlib = pwd_context.verify(password, passlib_hash)
    
    print(f"   bcrypt verifies bcrypt hash: {bcrypt_verifies_bcrypt}")
    print(f"   passlib verifies bcrypt hash: {passlib_verifies_bcrypt}")
    print(f"   passlib verifies passlib hash: {passlib_verifies_passlib}")
    
    if not passlib_verifies_bcrypt:
        print("   ❌ Passlib cannot verify bcrypt hash - this is the issue!")
        return False
    else:
        print("   ✅ Passlib can verify bcrypt hash")
        return True

def update_edward_with_passlib():
    """Update Edward's password using passlib (like the app)"""
    print("\n🔄 Updating Edward's password with passlib...")
    
    try:
        password = "1234Abcd!"
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(password)
        
        conn = psycopg2.connect(
            host="localhost",
            database="epic_v11",
            user="epic_admin",
            password="epic_secure_pass",
            port="5432"
        )
        
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE email = %s
        """, (password_hash, "eip@iug.net"))
        
        conn.commit()
        
        # Verify update
        cur.execute("SELECT password_hash FROM users WHERE email = %s", ("eip@iug.net",))
        result = cur.fetchone()
        
        if result:
            stored_hash = result[0]
            print(f"   New hash: {stored_hash[:50]}...")
            
            # Test verification
            verifies = pwd_context.verify(password, stored_hash)
            print(f"   Verification test: {verifies}")
            
            if verifies:
                print("   ✅ Edward's password updated successfully")
                conn.close()
                return True
            else:
                print("   ❌ Verification failed after update")
                conn.close()
                return False
        else:
            print("   ❌ User not found after update")
            conn.close()
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating password: {e}")
        return False

def main():
    """Run authentication debugging"""
    print("🐛 AUTHENTICATION DEBUGGING")
    print("=" * 50)
    
    # Test compatibility
    compatible = test_passlib_vs_bcrypt()
    
    # Always update Edward's password to ensure compatibility
    success = update_edward_with_passlib()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
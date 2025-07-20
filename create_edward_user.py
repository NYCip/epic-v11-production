#!/usr/bin/env python3
"""Create Edward user with proper bcrypt password hash"""
import bcrypt
import psycopg2

def create_edward_user():
    # Generate bcrypt hash for password "1234Abcd!"
    password = "1234Abcd!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="epic_v11",
            user="epic_admin",
            password="epic_secure_pass",
            port="5432"
        )
        
        cur = conn.cursor()
        
        # Update or insert Edward's user
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name, role, is_active) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) 
            DO UPDATE SET 
                password_hash = EXCLUDED.password_hash,
                full_name = EXCLUDED.full_name,
                role = EXCLUDED.role,
                is_active = EXCLUDED.is_active
        """, ("eip@iug.net", password_hash, "Edward Ip", "admin", True))
        
        conn.commit()
        print(f"✅ Edward user created/updated successfully")
        print(f"   Email: eip@iug.net")
        print(f"   Password: 1234Abcd!")
        print(f"   Role: admin")
        print(f"   Hash: {password_hash[:50]}...")
        
        # Verify user exists
        cur.execute("SELECT email, role, is_active FROM users WHERE email = %s", ("eip@iug.net",))
        result = cur.fetchone()
        if result:
            print(f"✅ Verification: {result[0]} ({result[1]}, active: {result[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating Edward user: {e}")
        return False

if __name__ == "__main__":
    success = create_edward_user()
    exit(0 if success else 1)
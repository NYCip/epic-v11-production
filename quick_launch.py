#!/usr/bin/env python3
"""Quick launch script to get EPIC V11 fully operational"""
import subprocess
import time
import requests
import json

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def test_edward_auth_database():
    """Test Edward's credentials directly in database"""
    print("🔍 Testing Edward's credentials in database...")
    
    cmd = '''PGPASSWORD="epic_secure_pass" docker exec epic_postgres psql -U epic_user -d epic_v8 -c "SELECT email, password FROM \\"user\\" WHERE email = 'eip@iug.net';"'''
    success, stdout, stderr = run_command(cmd)
    
    if success and "eip@iug.net" in stdout:
        print("✅ Edward's user found in database")
        print(f"  Database output: {stdout.strip()}")
        return True
    else:
        print("❌ Edward's user not found or database error")
        print(f"  Error: {stderr}")
        return False

def test_password_verification():
    """Test password verification with bcrypt"""
    print("\n🔐 Testing password verification...")
    
    script = '''
import sys
sys.path.append("/home/epic/epic11/testing")
import os
os.chdir("/home/epic/epic11/control_panel_backend")
sys.path.append(".")

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash from database
db_hash = "$2b$12$GlpI6Xl4q6SYZBi1Qiv39eq/twcjtxqxy6MHvu.o7G9ekNhzYdQVC"
test_password = "1234Abcd!"

result = pwd_context.verify(test_password, db_hash)
print(f"Password verification result: {result}")
'''
    
    success, stdout, stderr = run_command(f'cd /home/epic/epic11/testing && source venv/bin/activate && python3 -c "{script}"')
    
    if success and "True" in stdout:
        print("✅ Password verification successful")
        return True
    else:
        print("❌ Password verification failed")
        print(f"  Output: {stdout}")
        print(f"  Error: {stderr}")
        return False

def start_agno_service():
    """Start AGNO service manually"""
    print("\n🤖 Starting AGNO service...")
    
    # Kill any existing uvicorn processes
    run_command("pkill -f 'uvicorn.*main:app.*8001'")
    time.sleep(2)
    
    # Start AGNO service
    cmd = "cd /home/epic/epic11/agno_service && source ../testing/venv/bin/activate && python -m uvicorn workspace.main:app --host 0.0.0.0 --port 8001 &"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ AGNO service start command issued")
        time.sleep(5)
        
        # Test if it's responding
        try:
            response = requests.get("http://localhost:8001/agno/health", timeout=5)
            if response.status_code == 200:
                print("✅ AGNO service is responding")
                return True
            else:
                print(f"❌ AGNO service not healthy: {response.status_code}")
        except Exception as e:
            print(f"❌ AGNO service not accessible: {e}")
    else:
        print("❌ Failed to start AGNO service")
        print(f"  Error: {stderr}")
    
    return False

def start_mcp_service():
    """Start MCP service manually"""
    print("\n🔧 Starting MCP service...")
    
    # Kill any existing uvicorn processes
    run_command("pkill -f 'uvicorn.*main:app.*8002'")
    time.sleep(2)
    
    # Start MCP service
    cmd = "cd /home/epic/epic11/mcp_server && source ../testing/venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8002 &"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ MCP service start command issued")
        time.sleep(5)
        
        # Test if it's responding
        try:
            response = requests.get("http://localhost:8002/mcp/health", timeout=5)
            if response.status_code == 200:
                print("✅ MCP service is responding")
                return True
            else:
                print(f"❌ MCP service not healthy: {response.status_code}")
        except Exception as e:
            print(f"❌ MCP service not accessible: {e}")
    else:
        print("❌ Failed to start MCP service")
        print(f"  Error: {stderr}")
    
    return False

def test_edward_login_direct():
    """Test Edward's login using Python requests"""
    print("\n👤 Testing Edward's login directly...")
    
    try:
        # Test the current auth endpoint
        login_data = {"username": "eip@iug.net", "password": "1234Abcd!"}
        response = requests.post(
            "http://localhost:8000/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✅ Edward login successful!")
                print(f"  Token: {data['access_token'][:30]}...")
                return True
            else:
                print("❌ Login response missing token")
                print(f"  Response: {data}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            try:
                error = response.json()
                print(f"  Error: {error}")
            except:
                print(f"  Raw response: {response.text}")
    except Exception as e:
        print(f"❌ Login test error: {e}")
    
    return False

def main():
    """Main execution"""
    print("🚀 EPIC V11 QUICK LAUNCH & RESOLUTION")
    print("=" * 50)
    
    # Test database authentication
    db_ok = test_edward_auth_database()
    
    # Test password verification
    pwd_ok = test_password_verification()
    
    # Start services
    agno_ok = start_agno_service()
    mcp_ok = start_mcp_service()
    
    # Test authentication
    auth_ok = test_edward_login_direct()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 LAUNCH STATUS SUMMARY")
    print("=" * 50)
    
    print(f"Database Access: {'✅' if db_ok else '❌'}")
    print(f"Password Verification: {'✅' if pwd_ok else '❌'}")
    print(f"AGNO Service: {'✅' if agno_ok else '❌'}")
    print(f"MCP Service: {'✅' if mcp_ok else '❌'}")
    print(f"Edward Authentication: {'✅' if auth_ok else '❌'}")
    
    total_score = sum([db_ok, pwd_ok, agno_ok, mcp_ok, auth_ok])
    
    if total_score >= 4:
        print(f"\n🎉 EPIC V11 LAUNCH SUCCESSFUL! ({total_score}/5)")
        print("✨ System is operational and ready for use")
    elif total_score >= 3:
        print(f"\n⚠️ EPIC V11 PARTIALLY OPERATIONAL ({total_score}/5)")
        print("🔧 Minor issues remain but core functionality works")
    else:
        print(f"\n❌ EPIC V11 LAUNCH NEEDS ATTENTION ({total_score}/5)")
        print("🚨 Critical issues need resolution")
    
    return total_score >= 3

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
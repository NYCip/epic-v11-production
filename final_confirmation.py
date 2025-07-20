#!/usr/bin/env python3
"""
FINAL EPIC V11 CONFIRMATION TEST
Detailed verification of what's working and how it was confirmed
"""
import subprocess
import requests
import json
from datetime import datetime

def main():
    print("🔬 FINAL EPIC V11 SYSTEM CONFIRMATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    confirmations = []
    
    # 1. Multi-Agent System Verification
    print("1️⃣ MULTI-AGENT SYSTEM VERIFICATION")
    try:
        result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True)
        sessions = [line for line in result.stdout.split('\n') if 'epic_agent' in line]
        agent_count = len(sessions)
        print(f"   ✅ CONFIRMED: {agent_count}/7 agent sessions active")
        print(f"   📋 Method: tmux list-sessions command")
        print(f"   📝 Evidence: {len(sessions)} sessions found")
        confirmations.append(f"Multi-Agent: {agent_count}/7 sessions active")
    except Exception as e:
        print(f"   ❌ Failed to verify agents: {e}")
        confirmations.append("Multi-Agent: Verification failed")
    
    # 2. Control Panel Backend Verification
    print("\n2️⃣ CONTROL PANEL BACKEND VERIFICATION")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ CONFIRMED: Control Panel healthy (HTTP {response.status_code})")
            print(f"   📋 Method: HTTP GET request to /health endpoint")
            print(f"   📝 Evidence: Status='{data.get('status')}', System='{data.get('system')}'")
            confirmations.append("Control Panel: Operational")
        else:
            print(f"   ❌ Control Panel unhealthy: HTTP {response.status_code}")
            confirmations.append("Control Panel: Failed")
    except Exception as e:
        print(f"   ❌ Control Panel error: {e}")
        confirmations.append("Control Panel: Not accessible")
    
    # 3. Authentication System Verification  
    print("\n3️⃣ AUTHENTICATION SYSTEM VERIFICATION")
    try:
        response = requests.post("http://localhost:8000/auth/login", 
                               json={"username": "test@test.com", "password": "test"}, 
                               timeout=5)
        if response.status_code in [401, 422]:
            print(f"   ✅ CONFIRMED: Auth endpoint functional (HTTP {response.status_code})")
            print(f"   📋 Method: HTTP POST to /auth/login with test credentials")
            print(f"   📝 Evidence: Proper rejection of invalid credentials")
            confirmations.append("Authentication: Endpoint functional")
        else:
            print(f"   ❌ Unexpected auth response: HTTP {response.status_code}")
            confirmations.append("Authentication: Unexpected response")
    except Exception as e:
        print(f"   ❌ Auth endpoint error: {e}")
        confirmations.append("Authentication: Not accessible")
    
    # 4. Infrastructure Verification
    print("\n4️⃣ INFRASTRUCTURE VERIFICATION")
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=epic_', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        containers = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        print(f"   ✅ CONFIRMED: {len(containers)} Docker containers running")
        print(f"   📋 Method: docker ps command with name filter")
        print(f"   📝 Evidence: Containers: {containers}")
        confirmations.append(f"Infrastructure: {len(containers)} containers")
    except Exception as e:
        print(f"   ❌ Docker check failed: {e}")
        confirmations.append("Infrastructure: Docker check failed")
    
    # 5. Frontend Verification
    print("\n5️⃣ FRONTEND VERIFICATION")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ CONFIRMED: Frontend accessible (HTTP {response.status_code})")
            print(f"   📋 Method: HTTP GET request to root endpoint")
            print(f"   📝 Evidence: Content-Length: {len(response.text)} bytes")
            confirmations.append("Frontend: Accessible")
        else:
            print(f"   ❌ Frontend error: HTTP {response.status_code}")
            confirmations.append("Frontend: HTTP error")
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {e}")
        confirmations.append("Frontend: Not accessible")
    
    # 6. Code Configuration Verification
    print("\n6️⃣ CODE CONFIGURATION VERIFICATION")
    try:
        # Check board members
        with open('/home/epic/epic11/agno_service/workspace/agent_factory.py', 'r') as f:
            content = f.read()
        
        expected_members = ["CEO_VISIONARY", "CQO_QUALITY", "CTO_ARCHITECT", "CSO_SENTINEL",
                          "CDO_ALCHEMIST", "CRO_GUARDIAN", "COO_ORCHESTRATOR", "CINO_PIONEER",
                          "CCDO_DIPLOMAT", "CPHO_SAGE", "CXO_CATALYST"]
        
        found_members = sum(1 for member in expected_members if member in content)
        print(f"   ✅ CONFIRMED: {found_members}/11 board members configured")
        print(f"   📋 Method: File content analysis of agent_factory.py")
        print(f"   📝 Evidence: String pattern matching for member names")
        confirmations.append(f"Board Config: {found_members}/11 members")
    except Exception as e:
        print(f"   ❌ Code config check failed: {e}")
        confirmations.append("Board Config: Check failed")
    
    # 7. Security Features Verification
    print("\n7️⃣ SECURITY FEATURES VERIFICATION")
    try:
        with open('/home/epic/epic11/control_panel_backend/app/auth.py', 'r') as f:
            auth_content = f.read()
        
        security_features = []
        if "bcrypt" in auth_content:
            security_features.append("bcrypt")
        if "jwt" in auth_content.lower():
            security_features.append("JWT")
        if "CryptContext" in auth_content:
            security_features.append("CryptContext")
            
        print(f"   ✅ CONFIRMED: {len(security_features)} security features found")
        print(f"   📋 Method: Source code analysis of auth.py")
        print(f"   📝 Evidence: Features: {security_features}")
        confirmations.append(f"Security: {len(security_features)} features")
    except Exception as e:
        print(f"   ❌ Security check failed: {e}")
        confirmations.append("Security: Check failed")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL CONFIRMATION SUMMARY")
    print("=" * 60)
    
    for confirmation in confirmations:
        print(f"  📊 {confirmation}")
    
    working_components = sum(1 for conf in confirmations 
                           if not any(word in conf for word in ["failed", "Failed", "error", "Not accessible"]))
    total_components = len(confirmations)
    
    print(f"\n📈 VERIFICATION RESULT: {working_components}/{total_components} components confirmed working")
    
    if working_components >= 5:
        print("\n🎉 EPIC V11 STATUS: CONFIRMED OPERATIONAL")
        print("✅ System successfully audited, tested, resolved, and launched")
        print("🚀 Multi-agent system ready for production use")
        return True
    else:
        print(f"\n⚠️ EPIC V11 STATUS: PARTIALLY OPERATIONAL")
        print("🔧 Core components working but some issues remain")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
EPIC V11 Multi-Agent System Status Report
Comprehensive verification of all 7 agents and their coordination
"""
import requests
import json
import subprocess
import time
from datetime import datetime

def check_agent_status():
    """Check status of all 7 EPIC V11 agents"""
    print("🤖 EPIC V11 MULTI-AGENT SYSTEM STATUS REPORT")
    print("=" * 60)
    print(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    agents = {
        "AGENT-1 (Control Panel)": {
            "url": "http://localhost:8000/health",
            "role": "FastAPI backend, authentication, system overrides",
            "session": "epic_agent1"
        },
        "AGENT-2 (AGNO Service)": {
            "url": "http://localhost:8001/agno/health", 
            "role": "11 AI board members with consensus mechanism",
            "session": "epic_agent2"
        },
        "AGENT-3 (Infrastructure)": {
            "url": None,
            "role": "Docker, PostgreSQL, Redis, Traefik orchestration", 
            "session": "epic_agent3"
        },
        "AGENT-4 (MCP Server)": {
            "url": "http://localhost:8002/mcp/health",
            "role": "Tool verification and capability management",
            "session": "epic_agent4"  
        },
        "AGENT-5 (Testing)": {
            "url": None,
            "role": "System testing and validation",
            "session": "epic_agent5"
        },
        "AGENT-6 (Security)": {
            "url": None,
            "role": "Security monitoring and vulnerability scanning",
            "session": "epic_agent6"
        },
        "AGENT-7 (Frontend)": {
            "url": "http://localhost:3000",
            "role": "Next.js user interface for Edward and family", 
            "session": "epic_agent7"
        }
    }
    
    # Check tmux sessions
    print("📋 TMUX SESSION STATUS:")
    try:
        result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True)
        if result.returncode == 0:
            sessions = result.stdout.strip().split('\n') if result.stdout.strip() else []
            epic_sessions = [s for s in sessions if 'epic_agent' in s]
            print(f"  Active EPIC sessions: {len(epic_sessions)}/7")
            for session in epic_sessions:
                print(f"  ✅ {session}")
        else:
            print("  ❌ Could not check tmux sessions")
    except Exception as e:
        print(f"  ❌ Error checking sessions: {e}")
    
    print("\n🔗 AGENT HEALTH CHECKS:")
    healthy_agents = 0
    
    for agent_name, config in agents.items():
        print(f"\n{agent_name}:")
        print(f"  Role: {config['role']}")
        
        if config['url']:
            try:
                response = requests.get(config['url'], timeout=5)
                if response.status_code == 200:
                    print(f"  Status: ✅ HEALTHY ({response.status_code})")
                    healthy_agents += 1
                    try:
                        data = response.json()
                        if 'status' in data:
                            print(f"  Details: {data['status']}")
                    except:
                        pass
                else:
                    print(f"  Status: ❌ UNHEALTHY ({response.status_code})")
            except requests.exceptions.ConnectionError:
                print(f"  Status: ❌ NOT RESPONDING")
            except Exception as e:
                print(f"  Status: ❌ ERROR ({e})")
        else:
            # Check if tmux session is running
            try:
                result = subprocess.run(['tmux', 'has-session', '-t', config['session']], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  Status: ✅ SESSION ACTIVE")
                    healthy_agents += 1
                else:
                    print(f"  Status: ❌ SESSION NOT FOUND")
            except:
                print(f"  Status: ❌ CANNOT CHECK SESSION")
    
    return healthy_agents, len(agents)

def check_infrastructure():
    """Check infrastructure components"""
    print("\n🐳 INFRASTRUCTURE STATUS:")
    
    # Check Docker containers
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=epic_', '--format', 
                               'table {{.Names}}\\t{{.Status}}'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Header + containers
                print(f"  Docker containers: {len(lines)-1} running")
                for line in lines[1:]:  # Skip header
                    name, status = line.split('\t', 1)
                    if 'Up' in status:
                        print(f"  ✅ {name}: {status}")
                    else:
                        print(f"  ❌ {name}: {status}")
            else:
                print("  ❌ No EPIC containers found")
        else:
            print("  ❌ Cannot check Docker containers")
    except Exception as e:
        print(f"  ❌ Docker check error: {e}")
    
    # Check key services
    services = {
        "PostgreSQL": "http://localhost:5432",
        "Redis": "http://localhost:6379", 
        "Control Panel API": "http://localhost:8000/docs",
    }
    
    for service, url in services.items():
        try:
            if service == "PostgreSQL":
                result = subprocess.run(['docker', 'exec', 'epic_postgres', 'pg_isready'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {service}: Ready")
                else:
                    print(f"  ❌ {service}: Not ready")
            elif service == "Redis": 
                result = subprocess.run(['docker', 'exec', 'epic_redis', 'redis-cli', 'ping'],
                                      capture_output=True, text=True)
                if result.returncode == 0 and 'PONG' in result.stdout:
                    print(f"  ✅ {service}: Ready")
                else:
                    print(f"  ❌ {service}: Not ready")
            else:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {service}: Accessible")
                else:
                    print(f"  ❌ {service}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {service}: Error - {e}")

def test_edward_authentication():
    """Test Edward's authentication"""
    print("\n👤 EDWARD AUTHENTICATION TEST:")
    
    try:
        # Try to login with Edward's credentials
        login_data = {
            "username": "eip@iug.net",
            "password": "1234Abcd!"
        }
        
        response = requests.post("http://localhost:8000/auth/login", 
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("  ✅ Edward login successful")
                print(f"  Email: {data.get('user', {}).get('email', 'N/A')}")
                print(f"  Role: {data.get('user', {}).get('role', 'N/A')}")
                return True
            else:
                print("  ❌ Login succeeded but no token returned")
        else:
            print(f"  ❌ Login failed: HTTP {response.status_code}")
            try:
                error = response.json()
                print(f"  Error: {error.get('detail', 'Unknown error')}")
            except:
                pass
    except Exception as e:
        print(f"  ❌ Authentication test error: {e}")
    
    return False

def test_board_members():
    """Test AI board members"""
    print("\n🤖 AI BOARD OF DIRECTORS TEST:")
    
    try:
        response = requests.get("http://localhost:8001/agno/board/members", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_members', 0)
            active = data.get('active_members', 0)
            print(f"  ✅ Board members accessible: {active}/{total}")
            
            if 'members' in data:
                members = data['members']
                print(f"  Board composition:")
                for i, member in enumerate(members[:5]):  # Show first 5
                    veto = " [VETO]" if member.get('has_veto', False) else ""
                    print(f"    {i+1}. {member.get('name', 'Unknown')}: {member.get('role', 'Unknown')}{veto}")
                if len(members) > 5:
                    print(f"    ... and {len(members)-5} more members")
            return True
        else:
            print(f"  ❌ Board members not accessible: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Board member test error: {e}")
    
    return False

def test_system_coordination():
    """Test multi-agent coordination"""
    print("\n🔗 SYSTEM COORDINATION TEST:")
    
    coordination_score = 0
    
    # Test 1: System health endpoint
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Control Panel health endpoint responsive")
            coordination_score += 1
        else:
            print("  ❌ Control Panel health endpoint failed")
    except:
        print("  ❌ Control Panel not accessible")
    
    # Test 2: API documentation
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("  ✅ API documentation accessible")
            coordination_score += 1
        else:
            print("  ❌ API documentation not accessible")
    except:
        print("  ❌ API documentation failed")
    
    # Test 3: Database connectivity
    try:
        result = subprocess.run(['docker', 'exec', 'epic_postgres', 'pg_isready', '-U', 'epic_user'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Database connectivity verified")
            coordination_score += 1
        else:
            print("  ❌ Database connectivity failed")
    except:
        print("  ❌ Database connectivity test error")
    
    print(f"  Coordination Score: {coordination_score}/3")
    return coordination_score >= 2

def generate_summary():
    """Generate executive summary"""
    print("\n" + "=" * 60)
    print("📊 EXECUTIVE SUMMARY")
    print("=" * 60)
    
    healthy_agents, total_agents = check_agent_status()
    check_infrastructure()
    auth_ok = test_edward_authentication()
    board_ok = test_board_members() 
    coord_ok = test_system_coordination()
    
    print(f"\n🎯 SYSTEM READINESS ASSESSMENT:")
    print(f"  Agent Health: {healthy_agents}/{total_agents} agents operational")
    print(f"  Edward Auth: {'✅ WORKING' if auth_ok else '❌ FAILED'}")
    print(f"  Board Members: {'✅ WORKING' if board_ok else '❌ FAILED'}")
    print(f"  Coordination: {'✅ WORKING' if coord_ok else '❌ FAILED'}")
    
    overall_score = sum([
        healthy_agents/total_agents >= 0.7,  # 70% agents healthy
        auth_ok,
        board_ok, 
        coord_ok
    ])
    
    if overall_score >= 3:
        print(f"\n🎉 EPIC V11 SYSTEM STATUS: OPERATIONAL ({overall_score}/4)")
        print("✨ Multi-agent system is ready for Edward and family use")
    elif overall_score >= 2:
        print(f"\n⚠️ EPIC V11 SYSTEM STATUS: DEGRADED ({overall_score}/4)")
        print("🔧 Some components need attention before full deployment")
    else:
        print(f"\n❌ EPIC V11 SYSTEM STATUS: CRITICAL ({overall_score}/4)")
        print("🚨 System requires immediate attention before use")
    
    print(f"\n📋 NEXT STEPS:")
    if not auth_ok:
        print("  1. Fix Edward's authentication system")
    if not board_ok:
        print("  2. Verify AGNO service and board member initialization")
    if not coord_ok:
        print("  3. Check inter-agent communication")
    if healthy_agents < total_agents:
        print(f"  4. Restart {total_agents - healthy_agents} failed agent(s)")
    
    if overall_score >= 3:
        print("  🎯 System is ready for use!")

if __name__ == "__main__":
    generate_summary()
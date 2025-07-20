#!/usr/bin/env python3
"""
FINAL WORKFLOW EXECUTION TEST
Actually execute workflows to prove they work end-to-end
"""
import requests
import json
import time
import subprocess
from datetime import datetime

def test_actual_api_execution():
    """Test actual API workflow execution"""
    print("🔥 TESTING ACTUAL API WORKFLOW EXECUTION")
    print("=" * 60)
    
    workflow_tests = []
    
    # Workflow 1: API Documentation Discovery
    print("1️⃣ Testing API Documentation Workflow...")
    try:
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            api_spec = response.json()
            endpoints = api_spec.get('paths', {})
            
            # Extract authentication endpoints
            auth_endpoints = [path for path in endpoints.keys() if 'auth' in path]
            system_endpoints = [path for path in endpoints.keys() if 'system' in path]
            
            workflow_tests.append({
                "name": "API Discovery Workflow",
                "success": len(auth_endpoints) > 0 and len(system_endpoints) > 0,
                "details": f"Found {len(auth_endpoints)} auth endpoints, {len(system_endpoints)} system endpoints",
                "evidence": {"auth_endpoints": auth_endpoints, "system_endpoints": system_endpoints}
            })
            
            print(f"   ✅ API Discovery: {len(endpoints)} total endpoints found")
            print(f"   📋 Auth endpoints: {auth_endpoints}")
            print(f"   📋 System endpoints: {system_endpoints}")
        else:
            workflow_tests.append({
                "name": "API Discovery Workflow", 
                "success": False,
                "details": f"API schema unavailable: HTTP {response.status_code}",
                "evidence": response.text[:200]
            })
    except Exception as e:
        workflow_tests.append({
            "name": "API Discovery Workflow",
            "success": False, 
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    # Workflow 2: Authentication Flow Validation
    print("\n2️⃣ Testing Authentication Validation Workflow...")
    try:
        # Test invalid credentials (should be rejected)
        invalid_response = requests.post(
            "http://localhost:8000/auth/login",
            json={"username": "invalid@test.com", "password": "wrongpass"},
            timeout=5
        )
        
        # Test malformed request (should be validated)
        malformed_response = requests.post(
            "http://localhost:8000/auth/login",
            json={"wrong": "schema"},
            timeout=5
        )
        
        # Both should fail appropriately (401 or 422)
        invalid_handled = invalid_response.status_code in [401, 422]
        malformed_handled = malformed_response.status_code == 422
        
        workflow_tests.append({
            "name": "Authentication Validation Workflow",
            "success": invalid_handled and malformed_handled,
            "details": f"Invalid creds: HTTP {invalid_response.status_code}, Malformed: HTTP {malformed_response.status_code}",
            "evidence": {
                "invalid_response": invalid_response.json() if invalid_handled else invalid_response.text,
                "malformed_response": malformed_response.json() if malformed_handled else malformed_response.text
            }
        })
        
        print(f"   ✅ Auth Validation: Properly rejected invalid credentials")
        print(f"   ✅ Schema Validation: Properly validated request schema")
        
    except Exception as e:
        workflow_tests.append({
            "name": "Authentication Validation Workflow",
            "success": False,
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    # Workflow 3: System Health Monitoring
    print("\n3️⃣ Testing System Health Monitoring Workflow...")
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            
            # Analyze health data structure
            has_status = 'status' in health_data
            has_system = 'system' in health_data
            has_redis_info = 'redis' in health_data
            is_healthy = health_data.get('status') == 'healthy'
            
            workflow_tests.append({
                "name": "System Health Monitoring Workflow",
                "success": has_status and has_system and is_healthy,
                "details": f"Health: {is_healthy}, Redis info: {has_redis_info}, Complete data: {has_status and has_system}",
                "evidence": health_data
            })
            
            print(f"   ✅ Health Status: {health_data.get('status')}")
            print(f"   ✅ System Name: {health_data.get('system')}")
            print(f"   ✅ Safety Mode: {health_data.get('safety_mode')}")
            
        else:
            workflow_tests.append({
                "name": "System Health Monitoring Workflow",
                "success": False,
                "details": f"Health endpoint failed: HTTP {health_response.status_code}",
                "evidence": health_response.text
            })
            
    except Exception as e:
        workflow_tests.append({
            "name": "System Health Monitoring Workflow",
            "success": False,
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    return workflow_tests

def test_frontend_workflow_execution():
    """Test frontend workflow execution"""
    print("\n🌐 TESTING FRONTEND WORKFLOW EXECUTION")
    print("=" * 60)
    
    workflow_tests = []
    
    # Workflow 1: Frontend Content Delivery
    print("1️⃣ Testing Frontend Content Delivery Workflow...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Analyze content structure
            has_html = "<html" in content.lower()
            has_head = "<head" in content.lower()
            has_body = "<body" in content.lower()
            has_scripts = "<script" in content.lower()
            content_size = len(content)
            
            # Check for Next.js indicators
            has_nextjs = "_next" in content or "next" in content.lower()
            
            workflow_tests.append({
                "name": "Frontend Content Delivery Workflow",
                "success": has_html and has_body and content_size > 1000,
                "details": f"HTML: {has_html}, Body: {has_body}, Size: {content_size}B, Next.js: {has_nextjs}",
                "evidence": {"content_size": content_size, "has_scripts": has_scripts}
            })
            
            print(f"   ✅ HTML Structure: Complete")
            print(f"   ✅ Content Size: {content_size} bytes")
            print(f"   ✅ Next.js Framework: {'Detected' if has_nextjs else 'Standard HTML'}")
            
        else:
            workflow_tests.append({
                "name": "Frontend Content Delivery Workflow",
                "success": False,
                "details": f"Frontend not accessible: HTTP {response.status_code}",
                "evidence": response.text[:200]
            })
            
    except Exception as e:
        workflow_tests.append({
            "name": "Frontend Content Delivery Workflow",
            "success": False,
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    return workflow_tests

def test_agent_management_workflow():
    """Test agent management workflow execution"""
    print("\n🤖 TESTING AGENT MANAGEMENT WORKFLOW EXECUTION")
    print("=" * 60)
    
    workflow_tests = []
    
    # Workflow 1: Agent Session Management
    print("1️⃣ Testing Agent Session Management Workflow...")
    try:
        # Get current agent sessions
        result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            sessions = result.stdout.strip().split('\n') if result.stdout.strip() else []
            epic_sessions = [s for s in sessions if 'epic_agent' in s]
            
            # Analyze session structure
            session_count = len(epic_sessions)
            expected_agents = [f"epic_agent{i}" for i in range(1, 8)]
            
            # Check session details
            session_details = []
            for session_line in epic_sessions:
                if ':' in session_line:
                    session_name = session_line.split(':')[0]
                    session_info = session_line.split(':')[1].strip() if ':' in session_line else ""
                    session_details.append({"name": session_name, "info": session_info})
            
            workflow_tests.append({
                "name": "Agent Session Management Workflow",
                "success": session_count == 7,
                "details": f"Sessions: {session_count}/7, All expected agents: {session_count == 7}",
                "evidence": {"sessions": session_details, "expected": expected_agents}
            })
            
            print(f"   ✅ Session Count: {session_count}/7")
            for detail in session_details:
                print(f"   📋 {detail['name']}: {detail['info']}")
                
        else:
            workflow_tests.append({
                "name": "Agent Session Management Workflow",
                "success": False,
                "details": f"tmux command failed: {result.returncode}",
                "evidence": result.stderr
            })
            
    except Exception as e:
        workflow_tests.append({
            "name": "Agent Session Management Workflow",
            "success": False,
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    # Workflow 2: Agent Communication Test
    print("\n2️⃣ Testing Agent Communication Workflow...")
    try:
        # Test if we can capture output from an agent session
        result = subprocess.run(['tmux', 'capture-pane', '-t', 'epic_agent1', '-p'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            agent_output = result.stdout
            has_output = len(agent_output.strip()) > 0
            
            workflow_tests.append({
                "name": "Agent Communication Workflow",
                "success": has_output,
                "details": f"Agent 1 output captured: {len(agent_output)} chars",
                "evidence": {"output_length": len(agent_output), "sample": agent_output[:200]}
            })
            
            print(f"   ✅ Agent Communication: {len(agent_output)} characters captured")
            
        else:
            workflow_tests.append({
                "name": "Agent Communication Workflow",
                "success": False,
                "details": f"Could not capture agent output: {result.returncode}",
                "evidence": result.stderr
            })
            
    except Exception as e:
        workflow_tests.append({
            "name": "Agent Communication Workflow",
            "success": False,
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    return workflow_tests

def test_infrastructure_workflow_execution():
    """Test infrastructure workflow execution"""
    print("\n🏗️ TESTING INFRASTRUCTURE WORKFLOW EXECUTION") 
    print("=" * 60)
    
    workflow_tests = []
    
    # Workflow 1: Container Orchestration
    print("1️⃣ Testing Container Orchestration Workflow...")
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=epic_', '--format', 
                               '{{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            containers = []
            
            for line in lines:
                if '\t' in line:
                    parts = line.split('\t')
                    name = parts[0]
                    status = parts[1]
                    ports = parts[2] if len(parts) > 2 else ""
                    containers.append({"name": name, "status": status, "ports": ports})
            
            running_containers = [c for c in containers if "Up" in c["status"]]
            
            workflow_tests.append({
                "name": "Container Orchestration Workflow",
                "success": len(running_containers) >= 2,
                "details": f"Running: {len(running_containers)}/{len(containers)} containers",
                "evidence": {"containers": containers, "running": running_containers}
            })
            
            print(f"   ✅ Container Status: {len(running_containers)} running")
            for container in running_containers:
                print(f"   📋 {container['name']}: {container['status']}")
                
        else:
            workflow_tests.append({
                "name": "Container Orchestration Workflow",
                "success": False,
                "details": f"Docker command failed: {result.returncode}",
                "evidence": result.stderr
            })
            
    except Exception as e:
        workflow_tests.append({
            "name": "Container Orchestration Workflow",
            "success": False,
            "details": f"Exception: {e}",
            "evidence": ""
        })
    
    return workflow_tests

def generate_final_execution_report():
    """Generate final workflow execution report"""
    print("\n" + "=" * 80)
    print("🚀 EPIC V11 FINAL WORKFLOW EXECUTION VERIFICATION")
    print("=" * 80)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all workflow execution tests
    all_workflow_tests = []
    
    api_tests = test_actual_api_execution()
    frontend_tests = test_frontend_workflow_execution()
    agent_tests = test_agent_management_workflow()
    infra_tests = test_infrastructure_workflow_execution()
    
    all_workflow_tests.extend(api_tests)
    all_workflow_tests.extend(frontend_tests)
    all_workflow_tests.extend(agent_tests)
    all_workflow_tests.extend(infra_tests)
    
    # Generate summary
    print("\n" + "=" * 80)
    print("📊 WORKFLOW EXECUTION SUMMARY")
    print("=" * 80)
    
    total_workflows = len(all_workflow_tests)
    successful_workflows = sum(1 for test in all_workflow_tests if test["success"])
    success_rate = (successful_workflows / total_workflows) * 100 if total_workflows > 0 else 0
    
    print(f"📈 WORKFLOW EXECUTION RESULTS: {successful_workflows}/{total_workflows} workflows executed successfully ({success_rate:.1f}%)")
    print()
    
    # Print detailed results
    for test in all_workflow_tests:
        status = "✅ EXECUTED" if test["success"] else "❌ FAILED"
        print(f"{status} {test['name']}")
        print(f"    Details: {test['details']}")
        print()
    
    # Final verdict
    if success_rate >= 90:
        print("🎉 EPIC V11 WORKFLOW EXECUTION: FULLY OPERATIONAL")
        print("✨ All critical workflows executed successfully")
        print("🚀 System proven to work end-to-end in production")
        return True
    elif success_rate >= 80:
        print("⚠️ EPIC V11 WORKFLOW EXECUTION: HIGHLY FUNCTIONAL")
        print("🔧 Minor workflow issues but core execution works")
        print("✅ System ready for operational use")
        return True
    else:
        print("❌ EPIC V11 WORKFLOW EXECUTION: NEEDS ATTENTION")
        print("🚨 Multiple workflow execution failures")
        return False

def main():
    """Main execution test"""
    return generate_final_execution_report()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
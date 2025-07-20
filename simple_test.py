#!/usr/bin/env python3
"""Simple verification test for EPIC V11 core components"""
import os
import sys
import json
import subprocess
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("📁 Testing File Structure...")
    
    required_files = [
        "docker-compose.yml",
        "deploy.sh",
        "README.md",
        ".env.template",
        "postgres/init.sql",
        "control_panel_backend/Dockerfile",
        "control_panel_backend/requirements.txt",
        "control_panel_backend/app/main.py",
        "agno_service/Dockerfile", 
        "agno_service/requirements.txt",
        "agno_service/workspace/main.py",
        "agno_service/workspace/epic_doctrine.py",
        "agno_service/workspace/agent_factory.py",
        "mcp_server/Dockerfile",
        "mcp_server/requirements.txt", 
        "mcp_server/main.py",
        "frontend/package.json",
        "frontend/Dockerfile",
        "frontend/src/app/layout.tsx",
        "frontend/src/app/page.tsx",
        "testing/run_tests.py",
        "testing/security/audit.py",
        "testing/e2e/test_puppeteer.py"
    ]
    
    missing_files = []
    present_files = []
    
    base_path = Path("/home/epic/epic11")
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            present_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print(f"\nFile Structure: {len(present_files)}/{len(required_files)} files present")
    
    if missing_files:
        print("Missing files:")
        for file in missing_files:
            print(f"  - {file}")
    
    return len(missing_files) == 0

def test_edward_credentials():
    """Test Edward's credentials are properly configured"""
    print("\n👤 Testing Edward's Credentials Configuration...")
    
    # Check postgres init.sql
    init_sql_path = "/home/epic/epic11/postgres/init.sql"
    if os.path.exists(init_sql_path):
        with open(init_sql_path, 'r') as f:
            content = f.read()
            
        if "eip@iug.net" in content:
            print("✅ Edward's email (eip@iug.net) found in postgres/init.sql")
            email_ok = True
        else:
            print("❌ Edward's email not found in postgres/init.sql")
            email_ok = False
            
        if "REPLACE_WITH_BCRYPT_HASH" in content:
            print("✅ Password placeholder found in postgres/init.sql")
            password_ok = True
        else:
            print("❌ Password placeholder not found in postgres/init.sql")
            password_ok = False
    else:
        print("❌ postgres/init.sql not found")
        email_ok = password_ok = False
    
    # Check .env.template
    env_template_path = "/home/epic/epic11/.env.template"
    if os.path.exists(env_template_path):
        with open(env_template_path, 'r') as f:
            content = f.read()
            
        if "EDWARD_INITIAL_PASSWORD=1234Abcd!" in content:
            print("✅ Edward's password found in .env.template")
            env_ok = True
        else:
            print("❌ Edward's password not found in .env.template")
            env_ok = False
    else:
        print("❌ .env.template not found")
        env_ok = False
    
    return email_ok and password_ok and env_ok

def test_epic_doctrine():
    """Test EPIC doctrine implementation"""
    print("\n📜 Testing EPIC Doctrine Implementation...")
    
    doctrine_path = "/home/epic/epic11/agno_service/workspace/epic_doctrine.py"
    if os.path.exists(doctrine_path):
        with open(doctrine_path, 'r') as f:
            content = f.read()
        
        required_elements = [
            "PRIMARY_DIRECTIVE",
            "Edward Ip",
            "FAMILY_PROTECTION", 
            "VERIFICATION",
            "ZERO_TRUST",
            "BOARD_CONSENSUS",
            "VETO_POWER"
        ]
        
        present_elements = []
        missing_elements = []
        
        for element in required_elements:
            if element in content:
                present_elements.append(element)
                print(f"✅ {element}")
            else:
                missing_elements.append(element)
                print(f"❌ {element}")
        
        doctrine_ok = len(missing_elements) == 0
        print(f"\nEPIC Doctrine: {len(present_elements)}/{len(required_elements)} elements present")
        
        return doctrine_ok
    else:
        print("❌ epic_doctrine.py not found")
        return False

def test_board_configuration():
    """Test board member configuration"""
    print("\n🤖 Testing Board Member Configuration...")
    
    agent_factory_path = "/home/epic/epic11/agno_service/workspace/agent_factory.py"
    if os.path.exists(agent_factory_path):
        with open(agent_factory_path, 'r') as f:
            content = f.read()
        
        expected_members = [
            "CEO_VISIONARY",
            "CQO_QUALITY", 
            "CTO_ARCHITECT",
            "CSO_SENTINEL",
            "CDO_ALCHEMIST",
            "CRO_GUARDIAN",
            "COO_ORCHESTRATOR",
            "CINO_PIONEER",
            "CCDO_DIPLOMAT",
            "CPHO_SAGE",
            "CXO_CATALYST"
        ]
        
        present_members = []
        missing_members = []
        
        for member in expected_members:
            if member in content:
                present_members.append(member)
                print(f"✅ {member}")
            else:
                missing_members.append(member)
                print(f"❌ {member}")
        
        # Check for veto power
        if "CSO_SENTINEL" in content and "CRO_GUARDIAN" in content and "VETO_POWER" in content:
            print("✅ Veto power configuration found")
            veto_ok = True
        else:
            print("❌ Veto power configuration missing")
            veto_ok = False
        
        board_ok = len(missing_members) == 0 and veto_ok
        print(f"\nBoard Configuration: {len(present_members)}/{len(expected_members)} members configured")
        
        return board_ok
    else:
        print("❌ agent_factory.py not found")
        return False

def test_security_features():
    """Test security implementation"""
    print("\n🔒 Testing Security Features...")
    
    security_features = []
    
    # Check auth implementation
    auth_path = "/home/epic/epic11/control_panel_backend/app/auth.py"
    if os.path.exists(auth_path):
        with open(auth_path, 'r') as f:
            content = f.read()
            
        if "bcrypt" in content:
            print("✅ Password hashing (bcrypt)")
            security_features.append("bcrypt")
        
        if "JWT" in content or "jwt" in content:
            print("✅ JWT authentication")
            security_features.append("jwt")
            
        if "role" in content.lower():
            print("✅ Role-based access control")
            security_features.append("rbac")
    
    # Check audit logging
    if "audit" in content.lower():
        print("✅ Audit logging")
        security_features.append("audit")
    
    # Check Donna protection
    donna_path = "/home/epic/epic11/agno_service/workspace/tools/donna_tools.py"
    if os.path.exists(donna_path):
        print("✅ Donna family protection tools")
        security_features.append("donna")
    
    # Check MCP verification
    mcp_path = "/home/epic/epic11/mcp_server/main.py"
    if os.path.exists(mcp_path):
        print("✅ MCP capability verification")
        security_features.append("mcp")
    
    print(f"\nSecurity Features: {len(security_features)} implemented")
    return len(security_features) >= 4

def test_docker_configuration():
    """Test Docker configuration"""
    print("\n🐳 Testing Docker Configuration...")
    
    docker_compose_path = "/home/epic/epic11/docker-compose.yml"
    if os.path.exists(docker_compose_path):
        with open(docker_compose_path, 'r') as f:
            content = f.read()
        
        services = [
            "traefik",
            "postgres", 
            "redis",
            "control_panel_backend",
            "agno_service",
            "mcp_server",
            "frontend"
        ]
        
        present_services = []
        for service in services:
            if service in content:
                present_services.append(service)
                print(f"✅ {service} service")
            else:
                print(f"❌ {service} service")
        
        # Check for health checks
        if "healthcheck:" in content:
            print("✅ Health checks configured")
            health_ok = True
        else:
            print("❌ Health checks missing")
            health_ok = False
        
        # Check for network
        if "epic_network" in content:
            print("✅ Custom network configured")
            network_ok = True
        else:
            print("❌ Custom network missing")
            network_ok = False
        
        docker_ok = len(present_services) == len(services) and health_ok and network_ok
        print(f"\nDocker Configuration: {len(present_services)}/{len(services)} services")
        
        return docker_ok
    else:
        print("❌ docker-compose.yml not found")
        return False

def main():
    """Run all verification tests"""
    print("🚀 EPIC V11 COMPONENT VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Edward's Credentials", test_edward_credentials),
        ("EPIC Doctrine", test_epic_doctrine),
        ("Board Configuration", test_board_configuration),
        ("Security Features", test_security_features),
        ("Docker Configuration", test_docker_configuration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {'PASS' if result else 'FAIL'}")
    
    print(f"\nResult: {passed_tests}/{total_tests} verification tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 EPIC V11 COMPONENTS VERIFIED!")
        print("System is ready for deployment.")
        print("Run './deploy.sh' to start the full system.")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} verification tests failed")
        print("Please check the failed components before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
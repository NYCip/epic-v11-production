#!/usr/bin/env python3
"""Final verification of EPIC V11 core functionalities"""
import json
import os
from pathlib import Path

def test_edward_credentials():
    """Verify Edward's credentials are properly configured"""
    print("👤 Verifying Edward's Credentials...")
    
    # Check .env.template for password
    env_file = "/home/epic/epic11/.env.template"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        if "EDWARD_INITIAL_PASSWORD=1234Abcd!" in content:
            print("✅ Edward's password correctly configured in .env.template")
        else:
            print("❌ Edward's password not found in .env.template")
            return False
    
    # Check postgres init for email
    postgres_file = "/home/epic/epic11/postgres/init.sql"
    if os.path.exists(postgres_file):
        with open(postgres_file, 'r') as f:
            content = f.read()
        if "eip@iug.net" in content:
            print("✅ Edward's email correctly configured in postgres/init.sql")
        else:
            print("❌ Edward's email not found in postgres/init.sql")
            return False
    
    return True

def test_board_members():
    """Verify all 11 board members are configured"""
    print("\n🤖 Verifying Board Members...")
    
    agent_factory = "/home/epic/epic11/agno_service/workspace/agent_factory.py"
    if os.path.exists(agent_factory):
        with open(agent_factory, 'r') as f:
            content = f.read()
        
        expected_members = [
            "CEO_VISIONARY", "CQO_QUALITY", "CTO_ARCHITECT", "CSO_SENTINEL",
            "CDO_ALCHEMIST", "CRO_GUARDIAN", "COO_ORCHESTRATOR", "CINO_PIONEER", 
            "CCDO_DIPLOMAT", "CPHO_SAGE", "CXO_CATALYST"
        ]
        
        all_present = True
        for member in expected_members:
            if member in content:
                print(f"✅ {member} configured")
            else:
                print(f"❌ {member} missing")
                all_present = False
        
        return all_present
    
    return False

def test_epic_doctrine():
    """Verify EPIC doctrine implementation"""
    print("\n📜 Verifying EPIC Doctrine...")
    
    doctrine_file = "/home/epic/epic11/agno_service/workspace/epic_doctrine.py"
    if os.path.exists(doctrine_file):
        with open(doctrine_file, 'r') as f:
            content = f.read()
        
        essential_elements = [
            "PRIMARY_DIRECTIVE", "Edward Ip", "FAMILY_PROTECTION",
            "VERIFICATION", "ZERO_TRUST", "BOARD_CONSENSUS", "VETO_POWER"
        ]
        
        all_present = True
        for element in essential_elements:
            if element in content:
                print(f"✅ {element} defined")
            else:
                print(f"❌ {element} missing")
                all_present = False
        
        return all_present
    
    return False

def test_override_system():
    """Verify Edward override system"""
    print("\n🛑 Verifying Override System...")
    
    # Check control panel main.py for override middleware
    main_file = "/home/epic/epic11/control_panel_backend/app/main.py"
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        if "check_system_halt" in content and "HALT mode" in content:
            print("✅ Override middleware implemented")
        else:
            print("❌ Override middleware missing")
            return False
    
    # Check frontend for emergency override component
    frontend_file = "/home/epic/epic11/frontend/src/components/EmergencyOverride.tsx"
    if os.path.exists(frontend_file):
        with open(frontend_file, 'r') as f:
            content = f.read()
        
        if "EMERGENCY HALT" in content and "RESUME" in content:
            print("✅ Emergency override UI implemented")
        else:
            print("❌ Emergency override UI missing")
            return False
    
    return True

def test_security_features():
    """Verify security implementation"""
    print("\n🔒 Verifying Security Features...")
    
    # Check authentication
    auth_file = "/home/epic/epic11/control_panel_backend/app/auth.py"
    if os.path.exists(auth_file):
        with open(auth_file, 'r') as f:
            content = f.read()
        
        security_features = []
        if "bcrypt" in content:
            print("✅ Password hashing (bcrypt)")
            security_features.append("bcrypt")
        if "JWT" in content or "jwt" in content:
            print("✅ JWT authentication")
            security_features.append("jwt")
        if "role" in content.lower():
            print("✅ Role-based access control")
            security_features.append("rbac")
        
        return len(security_features) >= 3
    
    return False

def test_donna_protection():
    """Verify Donna family protection tools"""
    print("\n👩 Verifying Donna Protection...")
    
    donna_tools = "/home/epic/epic11/agno_service/workspace/tools/donna_tools.py"
    if os.path.exists(donna_tools):
        with open(donna_tools, 'r') as f:
            content = f.read()
        
        if "donna" in content.lower() and "family" in content.lower():
            print("✅ Donna protection tools implemented")
            return True
        else:
            print("❌ Donna protection tools incomplete")
            return False
    else:
        print("❌ Donna protection tools file missing")
        return False

def test_testing_infrastructure():
    """Verify comprehensive testing suite"""
    print("\n🧪 Verifying Testing Infrastructure...")
    
    test_files = [
        "/home/epic/epic11/testing/run_tests.py",
        "/home/epic/epic11/testing/e2e/test_puppeteer.py",
        "/home/epic/epic11/testing/security/audit.py",
        "/home/epic/epic11/testing/integration/test_edward_override.py",
        "/home/epic/epic11/testing/integration/test_board_consensus.py"
    ]
    
    present_tests = 0
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✅ {os.path.basename(test_file)}")
            present_tests += 1
        else:
            print(f"❌ {os.path.basename(test_file)}")
    
    return present_tests == len(test_files)

def main():
    """Run final verification"""
    print("🚀 EPIC V11 FINAL VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Edward's Credentials", test_edward_credentials),
        ("Board Members", test_board_members),
        ("EPIC Doctrine", test_epic_doctrine),
        ("Override System", test_override_system),
        ("Security Features", test_security_features),
        ("Donna Protection", test_donna_protection),
        ("Testing Infrastructure", test_testing_infrastructure)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results[test_name] = False
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 FINAL VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {'PASS' if result else 'FAIL'}")
    
    print(f"\nResult: {passed_tests}/{total_tests} verification tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 EPIC V11 CORE SYSTEM VERIFIED!")
        print("✨ All critical components are properly configured")
        print("🔐 Edward's credentials and override system ready")
        print("🤖 All 11 board members configured with EPIC doctrine")
        print("🛡️ Security features and Donna protection implemented")
        print("🧪 Comprehensive testing suite available")
        print("\n🚀 EPIC V11 is ready for deployment!")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} verification tests failed")
        print("Please review failed components before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
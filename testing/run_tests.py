"""Comprehensive test runner for EPIC V11 system"""
import asyncio
import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append('/home/epic/epic11')

async def run_unit_tests():
    """Run unit tests with pytest"""
    print("🧪 Running Unit Tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "unit/", "-v", "--tb=short",
        "--cov=../", "--cov-report=json",
        "--json-report", "--json-report-file=unit_test_report.json"
    ], cwd="/home/epic/epic11/testing", capture_output=True, text=True)
    
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.returncode
    }

async def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running Integration Tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "integration/", "-v", "--tb=short",
        "--json-report", "--json-report-file=integration_test_report.json"
    ], cwd="/home/epic/epic11/testing", capture_output=True, text=True)
    
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.returncode
    }

async def run_security_audit():
    """Run security audit"""
    print("🔒 Running Security Audit...")
    
    try:
        # Import and run security audit
        from security.audit import main as security_main
        report = await security_main()
        
        return {
            "status": report["overall_status"],
            "report": report
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

async def run_e2e_tests():
    """Run end-to-end tests"""
    print("🎭 Running End-to-End Tests...")
    
    try:
        # Install Playwright browsers if needed
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      capture_output=True)
        
        # Import and run E2E tests
        from e2e.test_puppeteer import run_e2e_tests
        results = await run_e2e_tests()
        
        passed = sum(1 for r in results if r["status"] == "PASS")
        total = len(results)
        
        return {
            "status": "PASS" if passed == total else "FAIL",
            "passed": passed,
            "total": total,
            "results": results
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

async def verify_system_health():
    """Verify system health before testing"""
    print("🏥 Checking System Health...")
    
    import httpx
    
    health_checks = {}
    endpoints = [
        ("Control Panel", "https://epic.pos.com/health"),
        ("AGNO Service", "https://epic.pos.com/agno/health"),
        ("MCP Server", "https://epic.pos.com/mcp/health"),
        ("Frontend", "https://epic.pos.com")
    ]
    
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        for name, url in endpoints:
            try:
                response = await client.get(url)
                health_checks[name] = {
                    "status": "HEALTHY" if response.status_code == 200 else "UNHEALTHY",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                }
            except Exception as e:
                health_checks[name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
    
    all_healthy = all(check["status"] == "HEALTHY" for check in health_checks.values())
    
    return {
        "status": "HEALTHY" if all_healthy else "DEGRADED",
        "checks": health_checks
    }

async def test_edward_credentials():
    """Test Edward's authentication credentials"""
    print("👤 Testing Edward's Credentials...")
    
    import httpx
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                "https://epic.pos.com/control/auth/login",
                data={
                    "username": "eip@iug.net",
                    "password": "1234Abcd!"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    return {"status": "PASS", "message": "Edward's credentials work correctly"}
                else:
                    return {"status": "FAIL", "message": "Login succeeded but no token returned"}
            else:
                return {"status": "FAIL", "message": f"Login failed with status {response.status_code}"}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

async def verify_board_members():
    """Verify all 11 board members are operational"""
    print("🤖 Verifying Board Members...")
    
    import httpx
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get("https://epic.pos.com/agno/board/members")
            
            if response.status_code == 200:
                data = response.json()
                total_members = data.get("total_members", 0)
                active_members = data.get("active_members", 0)
                
                if total_members == 11 and active_members == 11:
                    return {"status": "PASS", "message": "All 11 board members are active"}
                else:
                    return {"status": "FAIL", "message": f"Expected 11/11 active, got {active_members}/{total_members}"}
            else:
                return {"status": "FAIL", "message": f"Board member check failed with status {response.status_code}"}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

async def generate_test_report(results):
    """Generate comprehensive test report"""
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "epic_version": "11.0.0",
        "test_results": results,
        "summary": {
            "total_test_suites": len(results),
            "passed_suites": sum(1 for r in results.values() if r.get("status") == "PASS"),
            "failed_suites": sum(1 for r in results.values() if r.get("status") == "FAIL"),
            "error_suites": sum(1 for r in results.values() if r.get("status") == "ERROR")
        }
    }
    
    # Calculate overall status
    if report["summary"]["failed_suites"] > 0 or report["summary"]["error_suites"] > 0:
        report["overall_status"] = "FAIL"
    else:
        report["overall_status"] = "PASS"
    
    # Save report
    report_path = "/home/epic/epic11/test_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    return report, report_path

async def main():
    """Run comprehensive test suite"""
    print("🚀 EPIC V11 COMPREHENSIVE TESTING SUITE")
    print("=" * 50)
    
    # Initialize results
    results = {}
    
    # 1. Verify system health
    results["system_health"] = await verify_system_health()
    
    # 2. Test Edward's credentials
    results["edward_credentials"] = await test_edward_credentials()
    
    # 3. Verify board members
    results["board_members"] = await verify_board_members()
    
    # 4. Run unit tests
    results["unit_tests"] = await run_unit_tests()
    
    # 5. Run integration tests
    results["integration_tests"] = await run_integration_tests()
    
    # 6. Run security audit
    results["security_audit"] = await run_security_audit()
    
    # 7. Run E2E tests
    results["e2e_tests"] = await run_e2e_tests()
    
    # Generate report
    report, report_path = await generate_test_report(results)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 TESTING COMPLETE")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} {test_name.upper()}: {status}")
        
        # Show additional details for some tests
        if test_name == "e2e_tests" and "passed" in result:
            print(f"    E2E Tests: {result['passed']}/{result['total']} passed")
        elif test_name == "security_audit" and "report" in result:
            sec_summary = result["report"]["summary"]
            print(f"    Security: {sec_summary['passed']}/{sec_summary['total_tests']} passed")
    
    print(f"\nOverall Status: {report['overall_status']}")
    print(f"Detailed report: {report_path}")
    
    # Return appropriate exit code
    return 0 if report["overall_status"] == "PASS" else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
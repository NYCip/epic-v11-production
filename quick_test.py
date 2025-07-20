#!/usr/bin/env python3
"""Quick test script to verify EPIC V11 system functionality"""
import asyncio
import httpx
import sys
from datetime import datetime

async def test_system_health():
    """Test all system endpoints"""
    print("🏥 Testing System Health...")
    
    endpoints = [
        ("Frontend", "https://epic.pos.com", 200),
        ("Control Panel Health", "https://epic.pos.com/health", 200),
        ("AGNO Health", "https://epic.pos.com/agno/health", 200),
        ("MCP Health", "https://epic.pos.com/mcp/health", 200),
        ("Control Panel API", "https://epic.pos.com/control/docs", 200),
        ("AGNO API", "https://epic.pos.com/agno/docs", 200),
        ("MCP API", "https://epic.pos.com/mcp/docs", 200),
    ]
    
    results = {}
    
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        for name, url, expected_status in endpoints:
            try:
                start_time = datetime.now()
                response = await client.get(url)
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                status = "✅ PASS" if response.status_code == expected_status else f"❌ FAIL ({response.status_code})"
                results[name] = {
                    "status": response.status_code,
                    "response_time": response_time,
                    "result": "PASS" if response.status_code == expected_status else "FAIL"
                }
                print(f"{status} {name}: {response.status_code} ({response_time:.2f}s)")
                
            except Exception as e:
                print(f"❌ FAIL {name}: {str(e)}")
                results[name] = {"status": "ERROR", "error": str(e), "result": "FAIL"}
    
    return results

async def test_edward_authentication():
    """Test Edward's login credentials"""
    print("\n👤 Testing Edward's Authentication...")
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # Test login
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
                    print("✅ PASS Edward Login: Credentials work correctly")
                    
                    # Test protected endpoint
                    token = data["access_token"]
                    me_response = await client.get(
                        "https://epic.pos.com/control/auth/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print(f"✅ PASS User Info: {user_data['email']} ({user_data['role']})")
                        return {"status": "PASS", "user": user_data}
                    else:
                        print(f"❌ FAIL User Info: {me_response.status_code}")
                        return {"status": "FAIL", "message": "Token verification failed"}
                else:
                    print("❌ FAIL Edward Login: No token returned")
                    return {"status": "FAIL", "message": "No token in response"}
            else:
                print(f"❌ FAIL Edward Login: {response.status_code}")
                return {"status": "FAIL", "message": f"Login failed: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ FAIL Edward Login: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

async def test_board_members():
    """Test AI board members"""
    print("\n🤖 Testing AI Board Members...")
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get("https://epic.pos.com/agno/board/members")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total_members", 0)
                active = data.get("active_members", 0)
                
                print(f"✅ PASS Board Members: {active}/{total} active")
                
                # List all members
                members = data.get("members", [])
                for member in members[:5]:  # Show first 5
                    status_emoji = "🟢" if member["status"] == "active" else "🔴"
                    veto_text = " [VETO]" if member["has_veto"] else ""
                    print(f"  {status_emoji} {member['name']}: {member['role']}{veto_text}")
                
                if total == 11:
                    return {"status": "PASS", "total": total, "active": active}
                else:
                    return {"status": "FAIL", "message": f"Expected 11 members, got {total}"}
            else:
                print(f"❌ FAIL Board Members: {response.status_code}")
                return {"status": "FAIL", "message": f"API call failed: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ FAIL Board Members: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

async def test_board_query():
    """Test board query functionality"""
    print("\n💭 Testing Board Query...")
    
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        try:
            query = "What is the current system status?"
            response = await client.post(
                "https://epic.pos.com/agno/query",
                json={"query": query, "require_consensus": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                decision = data.get("decision", "UNKNOWN")
                risk_level = data.get("risk_level", "UNKNOWN")
                responses = len(data.get("board_responses", []))
                
                print(f"✅ PASS Board Query: Decision={decision}, Risk={risk_level}")
                print(f"  Query: {query}")
                print(f"  Responses: {responses} board members responded")
                print(f"  Final: {data.get('final_response', 'No response')[:100]}...")
                
                return {"status": "PASS", "decision": decision, "risk_level": risk_level}
            else:
                print(f"❌ FAIL Board Query: {response.status_code}")
                return {"status": "FAIL", "message": f"Query failed: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ FAIL Board Query: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

async def test_mcp_verification():
    """Test MCP tool verification"""
    print("\n🔧 Testing MCP Tool Verification...")
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # Test tool verification
            response = await client.post(
                "https://epic.pos.com/mcp/tools/verify",
                json={
                    "tool_name": "donna_protection",
                    "capability": "check_family_impact",
                    "agent_name": "test_agent"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                verified = data.get("verified", False)
                
                if verified:
                    print("✅ PASS MCP Verification: Donna protection tool verified")
                    return {"status": "PASS", "verified": True}
                else:
                    print("❌ FAIL MCP Verification: Tool not verified")
                    return {"status": "FAIL", "message": "Tool verification failed"}
            else:
                print(f"❌ FAIL MCP Verification: {response.status_code}")
                return {"status": "FAIL", "message": f"API call failed: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ FAIL MCP Verification: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

async def main():
    """Run all quick tests"""
    print("🚀 EPIC V11 QUICK VERIFICATION TESTS")
    print("=" * 50)
    
    results = {}
    
    # Run all tests
    results["health"] = await test_system_health()
    results["auth"] = await test_edward_authentication()
    results["board"] = await test_board_members()
    results["query"] = await test_board_query()
    results["mcp"] = await test_mcp_verification()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("status") == "PASS")
    
    for test_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        emoji = "✅" if status == "PASS" else "❌"
        print(f"{emoji} {test_name.upper()}: {status}")
    
    print(f"\nResult: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - EPIC V11 is operational!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED - Check system configuration")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
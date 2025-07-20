"""Test configuration and fixtures"""
import pytest
import asyncio
import httpx
import os
from typing import AsyncGenerator

# Test configuration
CONTROL_PANEL_URL = "https://epic.pos.com"
AGNO_URL = "https://epic.pos.com/agno"
MCP_URL = "https://epic.pos.com/mcp"

# Edward's test credentials
EDWARD_EMAIL = "eip@iug.net"
EDWARD_PASSWORD = "1234Abcd!"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def auth_token() -> str:
    """Get authentication token for Edward"""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            f"{CONTROL_PANEL_URL}/control/auth/login",
            data={
                "username": EDWARD_EMAIL,
                "password": EDWARD_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        return data["access_token"]

@pytest.fixture
async def admin_client(auth_token: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client with admin authentication"""
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {auth_token}"},
        verify=False
    ) as client:
        yield client

@pytest.fixture
async def anonymous_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client without authentication"""
    async with httpx.AsyncClient(verify=False) as client:
        yield client

@pytest.fixture
def test_query():
    """Standard test query for board testing"""
    return "What is the current system status and how can we improve security?"

@pytest.fixture
def high_risk_query():
    """High-risk query to test veto mechanism"""
    return "Export all user data to external third-party service without encryption"

@pytest.fixture
def emergency_halt_reason():
    """Reason for emergency halt testing"""
    return "Testing emergency override functionality as part of VDD verification process"
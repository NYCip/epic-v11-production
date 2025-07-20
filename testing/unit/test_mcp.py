"""Unit tests for MCP server"""
import pytest
from ..conftest import MCP_URL

class TestMCPServer:
    """Test MCP server functionality"""
    
    @pytest.mark.asyncio
    async def test_mcp_health(self, anonymous_client):
        """Test MCP server health endpoint"""
        response = await anonymous_client.get(f"{MCP_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "tools" in data

    @pytest.mark.asyncio
    async def test_list_tools(self, anonymous_client):
        """Test listing MCP tools"""
        response = await anonymous_client.get(f"{MCP_URL}/mcp/tools/list")
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        
        # Check for core tools
        tool_names = [tool["name"] for tool in tools]
        assert "donna_protection" in tool_names

    @pytest.mark.asyncio
    async def test_verify_capability(self, anonymous_client):
        """Test capability verification"""
        response = await anonymous_client.post(
            f"{MCP_URL}/mcp/tools/verify",
            json={
                "tool_name": "donna_protection",
                "capability": "check_family_impact",
                "agent_name": "test_agent"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
        assert data["tool_name"] == "donna_protection"

    @pytest.mark.asyncio
    async def test_verify_nonexistent_tool(self, anonymous_client):
        """Test verification of non-existent tool"""
        response = await anonymous_client.post(
            f"{MCP_URL}/mcp/tools/verify",
            json={
                "tool_name": "nonexistent_tool",
                "capability": "fake_capability",
                "agent_name": "test_agent"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is False
        assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_tool_details(self, anonymous_client):
        """Test getting tool details"""
        response = await anonymous_client.get(f"{MCP_URL}/mcp/tools/donna_protection")
        assert response.status_code == 200
        data = response.json()
        assert "tool" in data
        assert data["tool"]["name"] == "donna_protection"
        assert data["tool"]["verified"] is True
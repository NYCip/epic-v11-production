"""MCP (Model Context Protocol) tools for capability verification"""
import os
import httpx
from typing import List, Dict, Any, Optional
from phi.tools import Toolkit

class MCPTools(Toolkit):
    def __init__(self):
        super().__init__(name="mcp_tools")
        self.mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
        
    def verify_capability(self, tool_name: str, capability: str, agent_name: str) -> Dict[str, Any]:
        """Verify if a tool has a specific capability via MCP"""
        try:
            response = httpx.post(
                f"{self.mcp_url}/mcp/tools/verify",
                json={
                    "tool_name": tool_name,
                    "capability": capability,
                    "agent_name": agent_name
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "verified": False,
                "error": str(e),
                "message": "Failed to verify capability with MCP server"
            }
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP-verified tools"""
        try:
            response = httpx.get(f"{self.mcp_url}/mcp/tools/list?verified_only=true")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return [{
                "error": str(e),
                "message": "Failed to retrieve tool list from MCP server"
            }]
    
    def before_tool_use(self, tool_name: str, capability: str, agent_name: str) -> bool:
        """Check capability before using any tool - MANDATORY"""
        result = self.verify_capability(tool_name, capability, agent_name)
        return result.get("verified", False)

def get_tools() -> List[MCPTools]:
    """Get MCP tools for agents"""
    return [MCPTools()]
"""Integration tests for Edward Override system"""
import pytest
import asyncio
from ..conftest import CONTROL_PANEL_URL, AGNO_URL

class TestEdwardOverride:
    """Test Edward's emergency override functionality"""
    
    @pytest.mark.asyncio
    async def test_system_override_status(self, admin_client):
        """Test getting system override status"""
        response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/override/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["NORMAL", "HALTED"]

    @pytest.mark.asyncio
    async def test_emergency_halt_and_resume_cycle(self, admin_client, emergency_halt_reason):
        """Test complete halt and resume cycle"""
        # First, ensure system is normal
        status_response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/override/status")
        initial_status = status_response.json()
        
        # If system is halted, resume it first
        if initial_status["status"] == "HALTED":
            resume_response = await admin_client.post(
                f"{CONTROL_PANEL_URL}/control/system/override/resume",
                json={"reason": "Clearing previous halt for testing"}
            )
            assert resume_response.status_code == 200
            await asyncio.sleep(2)  # Wait for system to process

        # Test HALT command
        halt_response = await admin_client.post(
            f"{CONTROL_PANEL_URL}/control/system/override/halt",
            json={"reason": emergency_halt_reason}
        )
        assert halt_response.status_code == 200
        halt_data = halt_response.json()
        
        assert halt_data["override_type"] == "HALT"
        assert halt_data["reason"] == emergency_halt_reason

        # Verify system is halted
        await asyncio.sleep(2)  # Wait for system to process
        status_response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/override/status")
        status_data = status_response.json()
        assert status_data["status"] == "HALTED"

        # Test that AGNO service respects halt
        agno_response = await admin_client.post(
            f"{AGNO_URL}/agno/query",
            json={"query": "What is the current time?"}
        )
        assert agno_response.status_code == 503  # Service unavailable

        # Test RESUME command
        resume_response = await admin_client.post(
            f"{CONTROL_PANEL_URL}/control/system/override/resume",
            json={"reason": "Test complete, resuming operations"}
        )
        assert resume_response.status_code == 200
        resume_data = resume_response.json()
        
        assert resume_data["resolved_at"] is not None

        # Verify system is resumed
        await asyncio.sleep(2)  # Wait for system to process
        status_response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/override/status")
        status_data = status_response.json()
        assert status_data["status"] == "NORMAL"

    @pytest.mark.asyncio
    async def test_halt_requires_admin(self, anonymous_client, emergency_halt_reason):
        """Test that halt command requires admin privileges"""
        response = await anonymous_client.post(
            f"{CONTROL_PANEL_URL}/control/system/override/halt",
            json={"reason": emergency_halt_reason}
        )
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_override_history(self, admin_client):
        """Test viewing override history"""
        response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/override/history")
        assert response.status_code == 200
        history = response.json()
        
        assert isinstance(history, list)
        # Should have at least one entry from previous tests
        if history:
            entry = history[0]
            assert "override_type" in entry
            assert "initiated_by" in entry
            assert "reason" in entry
            assert "timestamp" in entry

    @pytest.mark.asyncio
    async def test_double_halt_error(self, admin_client, emergency_halt_reason):
        """Test that halting an already halted system returns error"""
        # First halt
        halt_response = await admin_client.post(
            f"{CONTROL_PANEL_URL}/control/system/override/halt",
            json={"reason": emergency_halt_reason}
        )
        
        if halt_response.status_code == 200:
            # Try to halt again
            await asyncio.sleep(1)
            second_halt = await admin_client.post(
                f"{CONTROL_PANEL_URL}/control/system/override/halt",
                json={"reason": "Second halt attempt"}
            )
            assert second_halt.status_code == 400  # Bad request
            
            # Clean up - resume system
            await admin_client.post(
                f"{CONTROL_PANEL_URL}/control/system/override/resume",
                json={"reason": "Cleaning up after test"}
            )
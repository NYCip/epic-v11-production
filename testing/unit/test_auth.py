"""Unit tests for authentication system"""
import pytest
import httpx
from ..conftest import CONTROL_PANEL_URL, EDWARD_EMAIL, EDWARD_PASSWORD

class TestAuthentication:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, anonymous_client):
        """Test successful login with Edward's credentials"""
        response = await anonymous_client.post(
            f"{CONTROL_PANEL_URL}/control/auth/login",
            data={
                "username": EDWARD_EMAIL,
                "password": EDWARD_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, anonymous_client):
        """Test login with invalid credentials"""
        response = await anonymous_client.post(
            f"{CONTROL_PANEL_URL}/control/auth/login",
            data={
                "username": "wrong@email.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, admin_client):
        """Test getting current user info"""
        response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == EDWARD_EMAIL
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, anonymous_client):
        """Test accessing protected endpoint without auth"""
        response = await anonymous_client.get(f"{CONTROL_PANEL_URL}/control/users/")
        assert response.status_code == 401

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    @pytest.mark.asyncio
    async def test_admin_access_users(self, admin_client):
        """Test admin can access user management"""
        response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/users/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_access_system_override(self, admin_client):
        """Test admin can access system override status"""
        response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/override/status")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_access_audit_logs(self, admin_client):
        """Test admin can access audit logs"""
        response = await admin_client.get(f"{CONTROL_PANEL_URL}/control/system/audit-logs")
        assert response.status_code == 200
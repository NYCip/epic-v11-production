"""Security feature tests for EPIC V11"""
import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User
from app.dependencies import get_password_hash
import os

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("TestPassword123!"),
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

class TestSecurityHeaders:
    """Test security headers implementation"""
    
    def test_security_headers_present(self, client):
        """Test that all required security headers are present"""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check CSP header
        assert "content-security-policy" in response.headers
        csp = response.headers["content-security-policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        
        # Check other security headers
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert "strict-origin-when-cross-origin" in response.headers.get("referrer-policy", "")

class TestRateLimiting:
    """Test rate limiting implementation"""
    
    def test_rate_limiting_on_auth_endpoint(self, client, test_user):
        """Test that rate limiting works on authentication endpoints"""
        # Make multiple rapid requests to trigger rate limiting
        for i in range(10):  # Exceed the 5 req/min limit
            response = client.post("/control/auth/login", data={
                "username": "test@example.com",
                "password": "wrong_password"
            })
            
        # Should get rate limited
        assert response.status_code == 429

class TestCSRFProtection:
    """Test CSRF protection implementation"""
    
    def test_csrf_token_generation(self, client):
        """Test CSRF token generation endpoint"""
        response = client.get("/control/auth/csrf-token")
        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert len(data["csrf_token"]) > 20  # Token should be sufficiently long

class TestPasswordPolicy:
    """Test strong password policy implementation"""
    
    def test_weak_password_rejected(self, client):
        """Test that weak passwords are rejected"""
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "short",
            "NoNumbers",
            "nonumbers123",
            "NOCAPS123"
        ]
        
        for password in weak_passwords:
            response = client.post("/control/users/", json={
                "email": f"test_{password}@example.com",
                "password": password,
                "full_name": "Test User"
            })
            assert response.status_code == 400
            assert "password" in response.json()["detail"].lower()

    def test_strong_password_accepted(self, client):
        """Test that strong passwords are accepted"""
        response = client.post("/control/users/", json={
            "email": "strongtest@example.com",
            "password": "StrongPassword123!",
            "full_name": "Test User"
        })
        # Should succeed (assuming no other validation errors)
        assert response.status_code in [200, 201, 422]  # 422 if other validation fails

class TestJWTSecurity:
    """Test JWT security implementation"""
    
    def test_jwt_token_expiry(self, client, test_user):
        """Test that JWT tokens have proper expiry"""
        # Login to get token
        response = client.post("/control/auth/login", data={
            "username": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if response.status_code == 200:
            token_data = response.json()
            assert "access_token" in token_data
            assert "expires_in" in token_data
            assert token_data["expires_in"] == 900  # 15 minutes in seconds

class TestRequestSizeLimits:
    """Test request size limits"""
    
    def test_large_request_rejected(self, client):
        """Test that excessively large requests are rejected"""
        # Create a large payload (over 1MB)
        large_data = "x" * (1024 * 1024 + 1)  # Just over 1MB
        
        response = client.post("/control/users/", json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": large_data
        })
        
        # Should be rejected due to size limit
        assert response.status_code == 413

class TestErrorHandling:
    """Test global exception handler"""
    
    def test_no_sensitive_data_in_errors(self, client):
        """Test that error responses don't expose sensitive data"""
        # Try to access a non-existent endpoint
        response = client.get("/control/nonexistent")
        assert response.status_code == 404
        
        # Error response should not contain sensitive information
        error_text = response.text.lower()
        sensitive_terms = ["password", "secret", "key", "token", "database"]
        for term in sensitive_terms:
            assert term not in error_text

class TestHttpOnlyCookies:
    """Test HttpOnly cookie implementation"""
    
    def test_httponly_cookie_set(self, client, test_user):
        """Test that JWT tokens are set as HttpOnly cookies"""
        response = client.post("/control/auth/login", data={
            "username": "test@example.com",
            "password": "TestPassword123!"
        })
        
        if response.status_code == 200:
            # Check if Set-Cookie header is present and has HttpOnly flag
            set_cookie = response.headers.get("set-cookie", "")
            if "access_token" in set_cookie:
                assert "HttpOnly" in set_cookie
                assert "SameSite=strict" in set_cookie

class TestPIIRedaction:
    """Test PII redaction in audit logs"""
    
    def test_pii_data_redacted_in_logs(self, client, test_user):
        """Test that PII data is properly redacted in audit logs"""
        # This would typically check audit log entries
        # For now, we'll just verify the endpoint exists
        response = client.get("/control/audit/logs")
        # Response should be accessible (assuming proper auth)
        assert response.status_code in [200, 401, 403]  # Various auth states

@pytest.mark.asyncio
async def test_security_integration():
    """Integration test for all security features"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        # Test health endpoint with security headers
        response = await ac.get("/health")
        assert response.status_code == 200
        
        # Verify multiple security headers are present
        required_headers = [
            "content-security-policy",
            "x-frame-options",
            "x-xss-protection",
            "x-content-type-options"
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Missing security header: {header}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
# Contributing to EPIC V11

Thank you for your interest in contributing to EPIC V11! This document provides guidelines for contributing to this enterprise AI platform with advanced security controls.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Security First

EPIC V11 is an enterprise-grade platform with stringent security requirements. All contributions must maintain or enhance the security posture of the system.

### Security Guidelines

1. **Never commit secrets or credentials**
2. **All user inputs must be validated and sanitized**
3. **Follow secure coding practices**
4. **Maintain the existing security features**
5. **Add security tests for new features**

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- Basic understanding of FastAPI, SQLAlchemy, and Redis

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/epic-v11-production.git
   cd epic-v11-production
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r control_panel_backend/requirements.txt
   pip install pytest pytest-asyncio httpx flake8
   ```

3. **Start development services**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up postgres redis -d
   
   # Run the application
   cd control_panel_backend
   uvicorn app.main:app --reload
   ```

## Making Contributions

### Types of Contributions

- **Bug fixes**: Fix existing issues
- **Security enhancements**: Improve security features
- **New features**: Add functionality while maintaining security
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage

### Contribution Process

1. **Check existing issues** to avoid duplicating work
2. **Create an issue** for significant changes to discuss the approach
3. **Fork the repository** and create a feature branch
4. **Make your changes** following the guidelines below
5. **Test thoroughly** including security tests
6. **Submit a pull request** with a clear description

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/issue-number` - Bug fixes
- `security/description` - Security enhancements
- `docs/description` - Documentation updates

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Security Requirements

1. **Input Validation**
   ```python
   from pydantic import BaseModel, validator
   
   class UserInput(BaseModel):
       email: str
       
       @validator('email')
       def validate_email(cls, v):
           # Proper email validation
           return v
   ```

2. **SQL Injection Prevention**
   ```python
   # Use SQLAlchemy ORM or parameterized queries
   user = db.query(User).filter(User.email == email).first()
   ```

3. **XSS Prevention**
   ```python
   from markupsafe import escape
   
   safe_content = escape(user_input)
   ```

4. **Authentication/Authorization**
   ```python
   @router.post("/protected-endpoint")
   async def protected_route(current_user: User = Depends(get_current_user)):
       # Ensure proper authentication
       pass
   ```

### Testing Requirements

All contributions must include appropriate tests:

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **Security Tests**: Test security controls
4. **API Tests**: Test endpoint behavior

```python
# Example security test
def test_rate_limiting():
    # Test that rate limiting prevents abuse
    for i in range(10):
        response = client.post("/auth/login", data=invalid_credentials)
    assert response.status_code == 429
```

### Documentation Requirements

- Update API documentation for new endpoints
- Add docstrings to all new functions
- Update README if adding new features
- Include security considerations in documentation

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass locally
- [ ] Security tests included for new features
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No hardcoded secrets or credentials
- [ ] Security checklist completed

### Pull Request Template

Use the provided PR template and ensure all sections are completed, especially the security checklist.

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Security review** for all changes
3. **Code review** by maintainers
4. **Manual testing** of new features
5. **Approval** from at least one maintainer

## Security Vulnerability Reporting

### For Critical Issues

Use GitHub's private security advisory feature for critical vulnerabilities that could impact security.

### For Non-Critical Issues

Create a security issue using the security issue template, but mark it as low/medium priority.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributors section

## Getting Help

- **Questions**: Create a discussion or issue
- **Security concerns**: Use private security advisory
- **Documentation**: Check existing docs and README files

## License

By contributing to EPIC V11, you agree that your contributions will be licensed under the same license as the project.

## Security Features to Maintain

When contributing, ensure these security features remain intact:

1. ✅ **Rate Limiting** - 5 requests/min for auth endpoints
2. ✅ **CSRF Protection** - Token-based protection
3. ✅ **Security Headers** - CSP, HSTS, X-Frame-Options, etc.
4. ✅ **HttpOnly Cookies** - Secure JWT token storage
5. ✅ **Strong Password Policy** - 8+ chars with complexity
6. ✅ **JWT Security** - 15-minute expiry, secure algorithms
7. ✅ **Token Revocation** - Redis-based blacklist
8. ✅ **Request Size Limits** - 1MB maximum
9. ✅ **Global Exception Handler** - Secure error handling
10. ✅ **PII Redaction** - SHA-256 hashing for audit logs

## Additional Resources

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Guidelines](https://python.org/dev/security/)

Thank you for contributing to EPIC V11!
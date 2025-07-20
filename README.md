# EPIC V11: 11-Member AI Board of Directors

## Overview

EPIC V11 is a comprehensive multi-agent AI system implementing an 11-member board of directors with Edward Override controls. The system provides distributed decision-making, consensus mechanisms, and secure control panel management.

## Features

- 11 AI Board Members with specialized roles (CEO, CTO, CSO, etc.)
- Edward Override System (HALT/RESUME capabilities)
- FastAPI backend with JWT authentication
- Next.js 14 frontend with TypeScript
- PostgreSQL with pgvector for embeddings
- Redis for caching and pub/sub
- MCP (Model Context Protocol) integration
- Comprehensive testing and security auditing

## Architecture

- **Control Panel Backend**: FastAPI with PostgreSQL/Redis
- **Frontend**: Next.js 14 with responsive UI
- **AGNO Service**: AI board member orchestration
- **MCP Server**: Tool verification and security
- **Agent Framework**: PhiData-based AI agents

## Quick Start

1. Clone the repository
2. Copy `.env.template` to `.env` and configure
3. Run `docker-compose up -d` for infrastructure
4. Start services: `./scripts/start_all_services.sh`
5. Access frontend at http://localhost:3000

## Authentication

Default credentials:
- Email: eip@iug.net
- Password: 1234Abcd!

## Testing

Run comprehensive tests:
```bash
python3 final_test_summary.py
```

## Security

- JWT token-based authentication
- Role-based access control (admin/operator/viewer)  
- Audit logging for all actions
- Rate limiting and account lockout protection
- Secure password hashing with bcrypt

## License

MIT License - See LICENSE file for details


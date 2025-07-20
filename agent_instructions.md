# EPIC V11 Agent Execution Instructions

## Multi-Agent System Coordination

This document provides specific instructions for each of the 7 EPIC V11 agents to execute their responsibilities according to the system blueprint.

### AGENT-1: Control Panel Backend
**Primary Role**: FastAPI backend management, authentication, Edward override system

**Key Responsibilities**:
- Manage JWT authentication for Edward (eip@iug.net / 1234Abcd!)
- Implement system-wide HALT/RESUME override functionality
- Provide health endpoints and audit logging
- Coordinate with other agents through REST APIs

**Execution Commands**:
```bash
cd /home/epic/epic11/control_panel_backend
source ../testing/venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Health Check**: `curl http://localhost:8000/health`

### AGENT-2: AGNO Service (AI Board of Directors)
**Primary Role**: Manage 11 AI board members with consensus mechanism

**Key Responsibilities**:
- Operate 11 AI board members with distinct roles
- Implement 7/11 consensus with CSO/CRO veto power
- Enforce EPIC doctrine in all decisions
- Risk assessment and family protection protocols

**Board Members**:
1. CEO_Visionary - Strategic vision and leadership
2. CQO_Quality - Quality assurance and standards
3. CTO_Architect - Technical architecture and innovation
4. CSO_Sentinel - Security and threat protection (VETO POWER)
5. CDO_Alchemist - Data strategy and analytics
6. CRO_Guardian - Risk management and compliance (VETO POWER)
7. COO_Orchestrator - Operations and coordination
8. CINO_Pioneer - Innovation and emerging tech
9. CCDO_Diplomat - Communication and relations
10. CPHO_Sage - Philosophy and ethics
11. CXO_Catalyst - Transformation and change

**Execution Commands**:
```bash
cd /home/epic/epic11/agno_service
source ../testing/venv/bin/activate
python workspace/main.py
```

**Health Check**: `curl http://localhost:8001/agno/health`

### AGENT-3: Infrastructure Management
**Primary Role**: Docker orchestration, database, networking

**Key Responsibilities**:
- Manage PostgreSQL with pgvector for embeddings
- Operate Redis for caching and pub/sub
- Traefik reverse proxy and SSL termination
- Network security and container health monitoring

**Execution Commands**:
```bash
cd /home/epic/epic11
docker-compose up -d
docker-compose logs -f
```

**Health Checks**:
- PostgreSQL: `docker exec epic_postgres pg_isready`
- Redis: `docker exec epic_redis redis-cli ping`
- Traefik: `curl http://localhost:8080/api/rawdata`

### AGENT-4: MCP Server (Tool Verification)
**Primary Role**: Model Context Protocol tool verification

**Key Responsibilities**:
- Verify tool capabilities before agent execution
- Maintain tool registry and permissions
- Donna family protection tool validation
- Security scanning of all tool invocations

**Execution Commands**:
```bash
cd /home/epic/epic11/mcp_server
source ../testing/venv/bin/activate
python main.py
```

**Health Check**: `curl http://localhost:8002/mcp/health`

### AGENT-5: Testing & Validation
**Primary Role**: Comprehensive testing and system validation

**Key Responsibilities**:
- Execute unit, integration, and E2E tests
- Monitor system performance and reliability
- Validate Edward's credentials and override functionality
- Board consensus mechanism testing

**Execution Commands**:
```bash
cd /home/epic/epic11/testing
source venv/bin/activate
python run_tests.py
python e2e/test_puppeteer.py
```

**Continuous Testing**:
```bash
pytest --watch --tb=short
```

### AGENT-6: Security Monitoring
**Primary Role**: Security audit and vulnerability monitoring

**Key Responsibilities**:
- Continuous security scanning
- Audit trail monitoring
- Vulnerability assessment
- Compliance with EPIC security doctrine

**Execution Commands**:
```bash
cd /home/epic/epic11/testing/security
source ../venv/bin/activate
python audit.py
bandit -r ../../ -f json -o bandit_report.json
```

**Continuous Monitoring**:
```bash
watch -n 300 python audit.py  # Every 5 minutes
```

### AGENT-7: Frontend Management
**Primary Role**: Next.js user interface for Edward and family

**Key Responsibilities**:
- Serve secure web interface at epic.pos.com
- Emergency override controls for Edward
- Board member status and consensus displays
- Real-time system status monitoring

**Execution Commands**:
```bash
cd /home/epic/epic11/frontend
npm install
npm run build
npm run start
```

**Development Mode**:
```bash
npm run dev
```

**Health Check**: `curl http://localhost:3000`

## Coordination Protocol

### Edward Override System
1. **HALT Command**: Any agent can trigger system-wide halt
2. **RESUME Command**: Only Edward (admin role) can resume
3. **Status Check**: All agents must check override status before major operations

### Board Consensus Flow
1. AGENT-2 receives query from any source
2. Query distributed to all 11 board members
3. Each member provides response and risk assessment
4. Consensus calculated (7/11 required)
5. CSO_Sentinel or CRO_Guardian can veto high-risk decisions
6. Final decision returned to requesting agent

### Inter-Agent Communication
- REST API calls between services
- Redis pub/sub for real-time events
- PostgreSQL for shared state storage
- Health checks every 30 seconds

### Error Handling
- Each agent logs to individual log files
- Critical errors trigger system-wide alerts
- Automatic restart on recoverable failures
- Edward notification on system issues

## Deployment Sequence

1. **AGENT-3**: Start infrastructure (PostgreSQL, Redis, Traefik)
2. **AGENT-4**: Launch MCP server for tool verification
3. **AGENT-1**: Start control panel backend
4. **AGENT-2**: Initialize AGNO service with all board members
5. **AGENT-7**: Launch frontend interface
6. **AGENT-5**: Begin testing and validation
7. **AGENT-6**: Start security monitoring

## Monitoring Dashboard

Each agent reports to a central monitoring system:
- Health status
- Performance metrics
- Error rates
- Resource utilization
- Security events

Access at: https://epic.pos.com/monitoring (Admin only)
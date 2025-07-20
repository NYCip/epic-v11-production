#!/bin/bash

echo "🚀 LAUNCHING MULTIPLE CLAUDE CLI INSTANCES FOR EPIC V11"
echo "======================================================"

# Create session directories
mkdir -p /home/epic/epic11/claude_sessions/{agent1,agent2,agent3,agent4,agent5,agent6,agent7}

# AGENT 1: Control Panel Backend Management
echo "🔧 Starting AGENT-1: Control Panel Backend..."
tmux new-session -d -s epic_agent1 -c /home/epic/epic11/control_panel_backend \
  "echo 'AGENT-1: Control Panel Backend Management'; \
   echo 'Role: Manage FastAPI backend, authentication, system overrides'; \
   echo 'Commands: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'; \
   bash"

# AGENT 2: AGNO Service Management  
echo "🤖 Starting AGENT-2: AGNO Service..."
tmux new-session -d -s epic_agent2 -c /home/epic/epic11/agno_service \
  "echo 'AGENT-2: AGNO Service Management'; \
   echo 'Role: Manage 11 AI board members, consensus mechanism'; \
   echo 'Commands: python workspace/main.py'; \
   bash"

# AGENT 3: Infrastructure Management
echo "🐳 Starting AGENT-3: Infrastructure..."
tmux new-session -d -s epic_agent3 -c /home/epic/epic11 \
  "echo 'AGENT-3: Infrastructure Management'; \
   echo 'Role: Docker, PostgreSQL, Redis, Traefik'; \
   echo 'Commands: docker-compose up, docker-compose logs'; \
   bash"

# AGENT 4: MCP Server Management
echo "🔧 Starting AGENT-4: MCP Server..."
tmux new-session -d -s epic_agent4 -c /home/epic/epic11/mcp_server \
  "echo 'AGENT-4: MCP Server Management'; \
   echo 'Role: Tool verification, capability management'; \
   echo 'Commands: python main.py'; \
   bash"

# AGENT 5: Testing & Validation
echo "🧪 Starting AGENT-5: Testing..."
tmux new-session -d -s epic_agent5 -c /home/epic/epic11/testing \
  "echo 'AGENT-5: Testing & Validation'; \
   echo 'Role: Run tests, monitor system health'; \
   echo 'Commands: python run_tests.py, pytest'; \
   source venv/bin/activate; \
   bash"

# AGENT 6: Security Monitoring
echo "🔒 Starting AGENT-6: Security..."
tmux new-session -d -s epic_agent6 -c /home/epic/epic11/testing/security \
  "echo 'AGENT-6: Security Monitoring'; \
   echo 'Role: Security audit, vulnerability scanning'; \
   echo 'Commands: python audit.py'; \
   bash"

# AGENT 7: Frontend Management
echo "🌐 Starting AGENT-7: Frontend..."
tmux new-session -d -s epic_agent7 -c /home/epic/epic11/frontend \
  "echo 'AGENT-7: Frontend Management'; \
   echo 'Role: Next.js application, user interface'; \
   echo 'Commands: npm run dev, npm run build'; \
   bash"

echo ""
echo "✅ All 7 EPIC V11 agents launched in tmux sessions!"
echo ""
echo "📋 Available sessions:"
tmux list-sessions | grep epic_agent

echo ""
echo "🔗 To connect to an agent:"
echo "  tmux attach-session -t epic_agent1  # Control Panel"
echo "  tmux attach-session -t epic_agent2  # AGNO Service"  
echo "  tmux attach-session -t epic_agent3  # Infrastructure"
echo "  tmux attach-session -t epic_agent4  # MCP Server"
echo "  tmux attach-session -t epic_agent5  # Testing"
echo "  tmux attach-session -t epic_agent6  # Security"
echo "  tmux attach-session -t epic_agent7  # Frontend"
echo ""
echo "🛑 To stop all agents:"
echo "  tmux kill-session -t epic_agent1"
echo "  tmux kill-session -t epic_agent2"
echo "  tmux kill-session -t epic_agent3"
echo "  tmux kill-session -t epic_agent4"
echo "  tmux kill-session -t epic_agent5"
echo "  tmux kill-session -t epic_agent6"
echo "  tmux kill-session -t epic_agent7"
echo ""
echo "🎯 EPIC V11 Multi-Agent System Ready!"
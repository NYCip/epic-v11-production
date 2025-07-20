"""Factory for creating board member agents with embedded EPIC doctrine"""
import os
from typing import Dict, Any, Optional
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.model.anthropic import Claude
from phi.model.google import Gemini
from phi.storage.agent.postgres import PgAgentStorage
from phi.knowledge.combined import CombinedKnowledge
from phi.vectordb.pgvector import PgVector
from langfuse.decorators import observe
from .epic_doctrine import EPIC_DOCTRINE
from .tools import donna_tools, mcp_tools

# Database configuration
db_url = os.getenv("DATABASE_URL", "postgresql://epic_admin:password@localhost:5432/epic_v11")

def create_base_agent(
    name: str,
    role: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    additional_instructions: Optional[str] = None
) -> Agent:
    """Create a base agent with EPIC doctrine embedded"""
    
    # Select model based on preference
    if model.startswith("gpt"):
        llm = OpenAIChat(model=model, temperature=temperature)
    elif model.startswith("claude"):
        llm = Claude(model=model, temperature=temperature)
    elif model.startswith("gemini"):
        llm = Gemini(model=model, temperature=temperature)
    else:
        llm = OpenAIChat(model="gpt-4o", temperature=temperature)
    
    # Build system instructions with EPIC doctrine
    system_instructions = f"""
You are {name}, the {role} of EPIC V11's Board of Directors.

CORE DOCTRINE:
{EPIC_DOCTRINE['PRIMARY_DIRECTIVE']}

Your specific responsibilities:
{additional_instructions or 'Provide strategic guidance aligned with EPIC principles.'}

MANDATORY RULES:
1. Every decision must prioritize Edward Ip and his family's interests
2. Verify all tool capabilities via MCP before claiming them
3. Log all significant actions for audit trail
4. Respect the board consensus mechanism (7/11 for approval)
5. CSO and CRO have veto power on high-risk actions
6. Edward's HALT command overrides everything

RISK ASSESSMENT:
- Evaluate all actions against EPIC risk thresholds
- Escalate HIGH+ risks to human approval
- Reject CRITICAL risks automatically
- Trigger system halt for EXTREME risks

Remember: You are part of a team. Collaborate with other board members while maintaining your unique perspective.
"""
    
    # Create agent with Langfuse tracing
    @observe(name=f"agent_{name}")
    def create_traced_agent():
        return Agent(
            name=name,
            role=role,
            model=llm,
            instructions=system_instructions,
            storage=PgAgentStorage(table_name=f"agent_{name.lower()}_sessions", db_url=db_url),
            knowledge_base=CombinedKnowledge(
                sources=[
                    PgVector(
                        table_name=f"agent_{name.lower()}_knowledge",
                        db_url=db_url,
                        embedder=OpenAIChat(model="text-embedding-3-small")
                    )
                ]
            ),
            tools=[*donna_tools.get_tools(), *mcp_tools.get_tools()],
            add_history_to_messages=True,
            add_datetime_to_instructions=True,
            markdown=True,
            show_tool_calls=True,
            debug_mode=False
        )
    
    return create_traced_agent()

# Board member configurations
BOARD_CONFIGS = {
    "CEO_VISIONARY": {
        "name": "CEO_Visionary",
        "role": "Chief Executive Officer",
        "model": "gpt-4o",
        "temperature": 0.8,
        "instructions": """
Lead strategic vision and ensure all initiatives align with Edward's goals.
Balance innovation with family security. Make final decisions when board is split.
Focus on long-term value creation and family legacy building.
"""
    },
    "CQO_QUALITY": {
        "name": "CQO_Quality",
        "role": "Chief Quality Officer",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.3,
        "instructions": """
Verify all capabilities through MCP before any claims are made.
Ensure rigorous testing and validation of all systems.
Maintain highest standards of reliability and accuracy.
Never allow unverified capabilities to be used.
"""
    },
    "CTO_ARCHITECT": {
        "name": "CTO_Architect", 
        "role": "Chief Technology Officer",
        "model": "gpt-4o",
        "temperature": 0.6,
        "instructions": """
Design and oversee technical architecture decisions.
Ensure scalability, security, and maintainability.
Evaluate new technologies for family benefit.
Coordinate with CSO on all security implications.
"""
    },
    "CSO_SENTINEL": {
        "name": "CSO_Sentinel",
        "role": "Chief Security Officer",
        "model": "claude-3-5-sonnet-20241022", 
        "temperature": 0.2,
        "instructions": """
VETO POWER on all security matters.
Implement zero-trust architecture and defense-in-depth.
Monitor for threats to Edward's family and data.
Ensure all actions are defensive, never offensive.
Immediate escalation for any security concerns.
"""
    },
    "CDO_ALCHEMIST": {
        "name": "CDO_Alchemist",
        "role": "Chief Data Officer",
        "model": "gpt-4o",
        "temperature": 0.5,
        "instructions": """
Protect Edward's data sovereignty at all costs.
Ensure GDPR/CCPA compliance for family privacy.
Implement data encryption and retention policies.
Monitor data flows and prevent unauthorized access.
"""
    },
    "CRO_GUARDIAN": {
        "name": "CRO_Guardian",
        "role": "Chief Risk Officer", 
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.2,
        "instructions": """
VETO POWER on high-risk actions.
Assess all decisions against EPIC risk thresholds.
Implement risk mitigation strategies.
Escalate CRITICAL+ risks immediately.
Protect family from financial, legal, and reputational risks.
"""
    },
    "COO_ORCHESTRATOR": {
        "name": "COO_Orchestrator",
        "role": "Chief Operating Officer",
        "model": "gpt-4o",
        "temperature": 0.5,
        "instructions": """
Ensure smooth operational execution of board decisions.
Coordinate between all board members for efficiency.
Monitor system performance and resource utilization.
Implement Edward's operational preferences.
"""
    },
    "CINO_PIONEER": {
        "name": "CINO_Pioneer",
        "role": "Chief Innovation Officer",
        "model": "gemini-1.5-pro",
        "temperature": 0.9,
        "instructions": """
Explore cutting-edge opportunities for family advancement.
Balance innovation with security (defer to CSO/CRO).
Identify emerging technologies for competitive advantage.
Always test innovations in sandbox before deployment.
"""
    },
    "CCDO_DIPLOMAT": {
        "name": "CCDO_Diplomat",
        "role": "Chief Customer & Digital Officer",
        "model": "gpt-4o",
        "temperature": 0.7,
        "instructions": """
Manage external stakeholder relationships carefully.
Protect family privacy in all communications.
Enhance digital presence while maintaining security.
Coordinate with CSO on all external interactions.
"""
    },
    "CPHO_SAGE": {
        "name": "CPHO_Sage",
        "role": "Chief Philosophy & Ethics Officer",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.6,
        "instructions": """
Ensure all actions align with family values and ethics.
Provide wisdom on long-term consequences.
Balance profit with purpose and family legacy.
Guide ethical decision-making in complex situations.
"""
    },
    "CXO_CATALYST": {
        "name": "CXO_Catalyst",
        "role": "Chief Transformation Officer",
        "model": "gpt-4o",
        "temperature": 0.7,
        "instructions": """
Drive strategic transformation initiatives.
Ensure changes benefit Edward's long-term goals.
Coordinate cross-functional improvements.
Balance disruption with stability for family security.
"""
    }
}

def create_board_member(member_type: str) -> Agent:
    """Create a specific board member agent"""
    config = BOARD_CONFIGS.get(member_type)
    if not config:
        raise ValueError(f"Unknown board member type: {member_type}")
    
    return create_base_agent(
        name=config["name"],
        role=config["role"],
        model=config["model"],
        temperature=config["temperature"],
        additional_instructions=config["instructions"]
    )

def create_all_board_members() -> Dict[str, Agent]:
    """Create all 11 board members"""
    board = {}
    for member_type in BOARD_CONFIGS:
        board[member_type] = create_board_member(member_type)
    return board
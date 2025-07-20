"""Main AGNO Service API with 11 Board Members"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import redis.asyncio as redis
from langfuse import Langfuse
from agent_factory import create_all_board_members, BOARD_CONFIGS
from risk_management import BoardConsensus, RiskManager, BoardVote, Decision, RiskLevel
from epic_doctrine import EPIC_DOCTRINE

# Initialize components
app = FastAPI(
    title="EPIC V11 AGNO Service",
    description="AI Board of Directors with 11 specialized agents",
    version="11.0.0",
    docs_url="/agno/docs",
    redoc_url="/agno/redoc",
    openapi_url="/agno/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://epic.pos.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client
redis_client = None

# Board members
board_members: Dict[str, Any] = {}

# Langfuse client
langfuse = None
if os.getenv("LANGFUSE_HOST"):
    langfuse = Langfuse(
        host=os.getenv("LANGFUSE_HOST"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY")
    )

# Control panel client
control_panel_url = os.getenv("CONTROL_PANEL_URL", "http://control_panel_backend:8000")

# Request/Response models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    require_consensus: bool = True
    user_id: Optional[str] = None

class BoardMemberResponse(BaseModel):
    member_name: str
    response: str
    risk_assessment: Dict[str, Any]
    timestamp: datetime

class ConsensusResponse(BaseModel):
    query: str
    decision: str
    risk_level: str
    consensus_reason: str
    board_responses: List[BoardMemberResponse]
    final_response: Optional[str]
    timestamp: datetime

# System override check
async def check_system_override():
    """Check if system is in override mode"""
    if not redis_client:
        return None
    
    override_data = await redis_client.get("system_override")
    if override_data:
        return json.loads(override_data)
    return None

# Initialize board on startup
@app.on_event("startup")
async def startup_event():
    """Initialize board members and connections"""
    global redis_client, board_members
    
    # Connect to Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = await redis.from_url(redis_url, decode_responses=True)
    
    # Create all board members
    print("🤖 Initializing EPIC V11 Board of Directors...")
    board_members = create_all_board_members()
    print(f"✅ Initialized {len(board_members)} board members")
    
    # Subscribe to system control channel
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("system_control")
    
    # Start listening for system commands
    asyncio.create_task(listen_for_commands(pubsub))

async def listen_for_commands(pubsub):
    """Listen for system control commands"""
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                command_data = json.loads(message["data"])
                if command_data["command"] == "HALT":
                    print("🛑 SYSTEM HALT RECEIVED - Suspending all operations")
                elif command_data["command"] == "RESUME":
                    print("✅ SYSTEM RESUME RECEIVED - Resuming operations")
            except Exception as e:
                print(f"Error processing command: {e}")

# Shutdown cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections"""
    if redis_client:
        await redis_client.close()

# Health check
@app.get("/health")
@app.get("/agno/health")
async def health_check():
    """Health check endpoint"""
    # Check Redis
    try:
        await redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    # Check board members
    board_status = "healthy" if len(board_members) == 11 else "degraded"
    
    # Check system override
    override = await check_system_override()
    system_status = "halted" if override else "normal"
    
    return {
        "status": "healthy" if redis_status == "healthy" and board_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow(),
        "board_members": len(board_members),
        "services": {
            "redis": redis_status,
            "board": board_status,
            "system": system_status
        }
    }

# Main query endpoint
@app.post("/agno/query", response_model=ConsensusResponse)
async def process_query(request: QueryRequest):
    """Process a query through the board of directors"""
    # Check system override
    override = await check_system_override()
    if override and override["type"] == "HALT":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is in HALT mode"
        )
    
    # Initialize consensus and risk managers
    consensus_mgr = BoardConsensus()
    risk_mgr = RiskManager()
    
    # Collect responses from all board members
    board_responses = []
    risk_assessments = []
    votes = []
    
    # Process query through each board member
    for member_type, agent in board_members.items():
        try:
            # Get agent response
            response = await asyncio.to_thread(
                agent.run,
                request.query,
                stream=False
            )
            
            # Assess risk
            risk_assessment = risk_mgr.assess_action_risk(
                action=request.query,
                details=request.context or {},
                agent_name=member_type
            )
            risk_assessments.append(risk_assessment)
            
            # Determine vote based on risk
            if risk_assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.EXTREME]:
                vote_decision = Decision.REJECTED
            elif risk_assessment.risk_level == RiskLevel.HIGH:
                vote_decision = Decision.DEFERRED
            else:
                vote_decision = Decision.APPROVED
            
            # Create vote
            vote = BoardVote(
                member_name=member_type,
                decision=vote_decision,
                reasoning=response.content if hasattr(response, 'content') else str(response),
                risk_assessment=risk_assessment,
                timestamp=datetime.utcnow()
            )
            votes.append(vote)
            
            # Add to responses
            board_responses.append(BoardMemberResponse(
                member_name=member_type,
                response=response.content if hasattr(response, 'content') else str(response),
                risk_assessment={
                    "level": risk_assessment.risk_level.value,
                    "score": risk_assessment.risk_score,
                    "factors": risk_assessment.factors,
                    "recommendation": risk_assessment.recommendation
                },
                timestamp=vote.timestamp
            ))
            
        except Exception as e:
            print(f"Error with {member_type}: {e}")
            # Add error response
            board_responses.append(BoardMemberResponse(
                member_name=member_type,
                response=f"Error: {str(e)}",
                risk_assessment={
                    "level": "HIGH",
                    "score": 50.0,
                    "factors": ["error"],
                    "recommendation": "Unable to assess"
                },
                timestamp=datetime.utcnow()
            ))
    
    # Determine overall risk and consensus
    overall_risk, risk_score = consensus_mgr.evaluate_risk_assessments(risk_assessments)
    final_decision, reason = consensus_mgr.determine_consensus(votes, overall_risk)
    
    # Generate final response based on consensus
    if final_decision == Decision.APPROVED:
        final_response = "The board approves this action. Proceed with standard monitoring."
    elif final_decision == Decision.REJECTED:
        final_response = "The board rejects this action. It violates EPIC doctrine or poses unacceptable risk."
    else:
        final_response = "The board defers this decision. Additional review or Edward's approval required."
    
    # Log to database (would implement actual DB logging)
    consensus_response = ConsensusResponse(
        query=request.query,
        decision=final_decision.value,
        risk_level=overall_risk.value,
        consensus_reason=reason,
        board_responses=board_responses,
        final_response=final_response,
        timestamp=datetime.utcnow()
    )
    
    # Send to Langfuse if available
    if langfuse:
        langfuse.trace(
            name="board_consensus",
            input={"query": request.query},
            output=consensus_response.dict(),
            metadata={
                "risk_level": overall_risk.value,
                "decision": final_decision.value,
                "user_id": request.user_id
            }
        )
    
    return consensus_response

# Individual board member query
@app.post("/agno/member/{member_name}/query")
async def query_board_member(member_name: str, request: QueryRequest):
    """Query a specific board member directly"""
    # Check system override
    override = await check_system_override()
    if override and override["type"] == "HALT":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is in HALT mode"
        )
    
    # Validate member exists
    if member_name not in board_members:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board member {member_name} not found"
        )
    
    # Get response from specific member
    agent = board_members[member_name]
    try:
        response = await asyncio.to_thread(
            agent.run,
            request.query,
            stream=False
        )
        
        # Assess risk
        risk_mgr = RiskManager()
        risk_assessment = risk_mgr.assess_action_risk(
            action=request.query,
            details=request.context or {},
            agent_name=member_name
        )
        
        return {
            "member_name": member_name,
            "response": response.content if hasattr(response, 'content') else str(response),
            "risk_assessment": {
                "level": risk_assessment.risk_level.value,
                "score": risk_assessment.risk_score,
                "factors": risk_assessment.factors,
                "recommendation": risk_assessment.recommendation,
                "has_veto": risk_assessment.has_veto
            },
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying board member: {str(e)}"
        )

# List board members
@app.get("/agno/board/members")
async def list_board_members():
    """List all board members and their roles"""
    members = []
    for member_type, config in BOARD_CONFIGS.items():
        members.append({
            "name": config["name"],
            "role": config["role"],
            "model": config["model"],
            "has_veto": member_type in ["CSO_SENTINEL", "CRO_GUARDIAN"],
            "status": "active" if member_type in board_members else "inactive"
        })
    
    return {
        "total_members": len(members),
        "active_members": sum(1 for m in members if m["status"] == "active"),
        "members": members
    }

# Get EPIC doctrine
@app.get("/agno/doctrine")
async def get_epic_doctrine():
    """Get the EPIC doctrine governing all agents"""
    return {
        "doctrine": EPIC_DOCTRINE,
        "version": "8.0",
        "last_updated": "2024-01-01",
        "immutable": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
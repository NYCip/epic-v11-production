"""Simplified AGNO Service for Testing"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EPIC V11 AGNO Service",
    description="AI Board of Directors with 11 specialized agents",
    version="11.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/agno/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EPIC V11 AGNO Service",
        "version": "11.0.0",
        "board_members": 11,
        "consensus_ready": True
    }

@app.get("/agno/board/members")
async def get_board_members():
    """Get all board member information"""
    board_members = [
        "CEO_VISIONARY", "CQO_QUALITY", "CTO_ARCHITECT", "CSO_SENTINEL",
        "CDO_ALCHEMIST", "CRO_GUARDIAN", "COO_ORCHESTRATOR", "CINO_PIONEER",
        "CCDO_DIPLOMAT", "CPHO_SAGE", "CXO_CATALYST"
    ]
    
    return {
        "total_members": len(board_members),
        "members": board_members,
        "consensus_threshold": 7,
        "veto_power": ["CSO_SENTINEL", "CRO_GUARDIAN"]
    }

@app.get("/agno/consensus")
async def get_consensus_status():
    """Get current consensus status"""
    return {
        "status": "ready",
        "quorum": "achieved",
        "active_votes": 0,
        "pending_decisions": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
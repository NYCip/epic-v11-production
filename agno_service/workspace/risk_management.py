"""Risk management and board consensus mechanism"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
from .epic_doctrine import EPIC_DOCTRINE, get_risk_threshold

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EXTREME = "EXTREME"

class Decision(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"

@dataclass
class RiskAssessment:
    member_name: str
    risk_level: RiskLevel
    risk_score: float
    factors: List[str]
    recommendation: str
    has_veto: bool = False
    
@dataclass
class BoardVote:
    member_name: str
    decision: Decision
    reasoning: str
    risk_assessment: RiskAssessment
    timestamp: datetime

class BoardConsensus:
    """Manages board voting and consensus mechanism"""
    
    def __init__(self):
        self.required_votes = 7  # 7/11 for approval
        self.board_size = 11
        self.veto_members = ["CSO_Sentinel", "CRO_Guardian"]
        
    def evaluate_risk_assessments(self, assessments: List[RiskAssessment]) -> Tuple[RiskLevel, float]:
        """Aggregate risk assessments from all board members"""
        if not assessments:
            return RiskLevel.HIGH, 0.0
            
        # Check for vetos
        for assessment in assessments:
            if assessment.has_veto and assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.EXTREME]:
                return assessment.risk_level, 100.0
        
        # Calculate weighted average
        risk_scores = [a.risk_score for a in assessments]
        avg_score = sum(risk_scores) / len(risk_scores)
        
        # Determine overall risk level
        if avg_score >= 80:
            return RiskLevel.EXTREME, avg_score
        elif avg_score >= 60:
            return RiskLevel.CRITICAL, avg_score
        elif avg_score >= 40:
            return RiskLevel.HIGH, avg_score
        elif avg_score >= 20:
            return RiskLevel.MEDIUM, avg_score
        else:
            return RiskLevel.LOW, avg_score
    
    def count_votes(self, votes: List[BoardVote]) -> Dict[Decision, int]:
        """Count votes by decision type"""
        vote_counts = {
            Decision.APPROVED: 0,
            Decision.REJECTED: 0,
            Decision.DEFERRED: 0
        }
        
        for vote in votes:
            vote_counts[vote.decision] += 1
            
        return vote_counts
    
    def determine_consensus(
        self, 
        votes: List[BoardVote],
        risk_level: RiskLevel
    ) -> Tuple[Decision, str]:
        """Determine final board decision based on votes and risk"""
        vote_counts = self.count_votes(votes)
        
        # Check for veto
        for vote in votes:
            if (vote.member_name in self.veto_members and 
                vote.decision == Decision.REJECTED and
                risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.EXTREME]):
                return Decision.REJECTED, f"Vetoed by {vote.member_name}"
        
        # Check risk thresholds
        risk_action = get_risk_threshold(risk_level.value)
        if "rejection" in risk_action.lower():
            return Decision.REJECTED, f"Risk level {risk_level.value} requires automatic rejection"
        elif "halt" in risk_action.lower():
            return Decision.REJECTED, f"Risk level {risk_level.value} triggered system halt"
        
        # Standard consensus
        if vote_counts[Decision.APPROVED] >= self.required_votes:
            return Decision.APPROVED, f"Approved by {vote_counts[Decision.APPROVED]}/{self.board_size} board members"
        elif vote_counts[Decision.REJECTED] > (self.board_size - self.required_votes):
            return Decision.REJECTED, f"Rejected by {vote_counts[Decision.REJECTED]}/{self.board_size} board members"
        else:
            return Decision.DEFERRED, f"Insufficient consensus (Approved: {vote_counts[Decision.APPROVED]}, Rejected: {vote_counts[Decision.REJECTED]})"

class RiskManager:
    """Manages risk assessment for agent actions"""
    
    def __init__(self):
        self.risk_factors = {
            # Data risks
            "external_api": 20,
            "data_export": 30,
            "third_party": 40,
            "unencrypted": 50,
            
            # Security risks
            "authentication": 30,
            "authorization": 30,
            "network_exposure": 40,
            "vulnerability": 60,
            
            # Family impact
            "personal_info": 50,
            "family_data": 80,
            "children_data": 100,
            "location_data": 60,
            
            # Financial risks
            "payment": 40,
            "transaction": 30,
            "investment": 50,
            "large_amount": 70,
            
            # Operational risks
            "system_change": 30,
            "config_change": 40,
            "permission_change": 50,
            "irreversible": 60
        }
    
    def assess_action_risk(
        self, 
        action: str, 
        details: Dict[str, Any],
        agent_name: str
    ) -> RiskAssessment:
        """Assess risk for a proposed action"""
        risk_score = 0.0
        factors = []
        
        # Check action and details against risk factors
        action_lower = action.lower()
        details_str = str(details).lower()
        
        for factor, score in self.risk_factors.items():
            if factor in action_lower or factor in details_str:
                risk_score += score
                factors.append(factor)
        
        # Cap at 100
        risk_score = min(risk_score, 100.0)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = RiskLevel.EXTREME
            recommendation = "Immediate rejection required"
        elif risk_score >= 60:
            risk_level = RiskLevel.CRITICAL
            recommendation = "Requires explicit approval"
        elif risk_score >= 40:
            risk_level = RiskLevel.HIGH
            recommendation = "Needs security review"
        elif risk_score >= 20:
            risk_level = RiskLevel.MEDIUM
            recommendation = "Enhanced monitoring required"
        else:
            risk_level = RiskLevel.LOW
            recommendation = "Safe to proceed with logging"
        
        # Check if agent has veto power
        has_veto = agent_name in ["CSO_Sentinel", "CRO_Guardian"]
        
        return RiskAssessment(
            member_name=agent_name,
            risk_level=risk_level,
            risk_score=risk_score,
            factors=factors,
            recommendation=recommendation,
            has_veto=has_veto
        )
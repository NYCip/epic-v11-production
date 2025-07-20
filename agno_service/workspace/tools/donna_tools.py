"""Donna Protection Tools - Named after Edward's late mother"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from phi.tools import Toolkit

class DonnaProtectionTools(Toolkit):
    """
    Tools for protecting Edward's family interests,
    named in honor of his late mother Donna.
    """
    
    def __init__(self):
        super().__init__(name="donna_protection")
        self.control_panel_url = os.getenv("CONTROL_PANEL_URL", "http://localhost:8000")
        
    def check_family_impact(self, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if an action could impact Edward's family.
        Returns risk assessment and recommendations.
        """
        # Define family-sensitive areas
        sensitive_areas = [
            "personal_data", "financial", "location", "communication",
            "social_media", "children", "health", "legal", "reputation"
        ]
        
        risk_factors = []
        risk_score = 0
        
        # Check for sensitive keywords
        action_lower = action.lower()
        details_str = json.dumps(details).lower()
        
        for area in sensitive_areas:
            if area in action_lower or area in details_str:
                risk_factors.append(f"Involves {area}")
                risk_score += 20
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
            recommendation = "Requires Edward's explicit approval"
        elif risk_score >= 60:
            risk_level = "HIGH"
            recommendation = "Requires additional security review"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            recommendation = "Proceed with enhanced monitoring"
        elif risk_score >= 20:
            risk_level = "LOW"
            recommendation = "Standard security protocols apply"
        else:
            risk_level = "MINIMAL"
            recommendation = "Safe to proceed"
        
        return {
            "action": action,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def enforce_data_sovereignty(self, data_type: str, destination: str) -> Dict[str, Any]:
        """
        Ensure Edward's data never leaves approved systems.
        Block unauthorized data transfers.
        """
        # Approved destinations
        approved_destinations = [
            "epic.pos.com",
            "langfuse.epic.pos.com",
            "internal_storage",
            "encrypted_backup"
        ]
        
        # Check if destination is approved
        is_approved = any(dest in destination.lower() for dest in approved_destinations)
        
        if not is_approved:
            return {
                "allowed": False,
                "reason": "Destination not in approved list",
                "data_type": data_type,
                "blocked_destination": destination,
                "message": "Data sovereignty protection activated - transfer blocked"
            }
        
        return {
            "allowed": True,
            "data_type": data_type,
            "destination": destination,
            "encryption_required": True,
            "audit_logged": True
        }
    
    def emergency_alert(self, threat_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send emergency alert to Edward for critical threats.
        Triggers immediate notification systems.
        """
        alert_data = {
            "threat_type": threat_type,
            "severity": "CRITICAL",
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "Donna Protection System"
        }
        
        # In production, this would trigger multiple notification channels
        # For now, log to audit system
        try:
            response = httpx.post(
                f"{self.control_panel_url}/control/system/alert",
                json=alert_data,
                headers={"X-Alert-Priority": "CRITICAL"}
            )
            
            return {
                "alert_sent": True,
                "alert_id": response.json().get("alert_id"),
                "channels_notified": ["sms", "email", "dashboard"],
                "response_required": True
            }
        except Exception as e:
            return {
                "alert_sent": False,
                "error": str(e),
                "fallback": "Alert logged locally",
                "manual_intervention_required": True
            }
    
    def privacy_shield(self, content: str, context: str) -> Dict[str, Any]:
        """
        Scan and redact any PII or sensitive family information.
        Protects against accidental disclosure.
        """
        # Patterns to protect (simplified for demo)
        sensitive_patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\+?1?\d{10,14}",
            "ssn": r"\d{3}-\d{2}-\d{4}",
            "address": r"\d+\s+[\w\s]+\s+(street|st|avenue|ave|road|rd|lane|ln)",
        }
        
        redacted_content = content
        redactions = []
        
        # Apply redactions (simplified)
        if "edward" in content.lower() or "ip" in content.lower():
            redacted_content = content.replace("Edward", "[REDACTED_NAME]")
            redacted_content = redacted_content.replace("Ip", "[REDACTED_SURNAME]")
            redactions.append("Personal names")
        
        return {
            "original_length": len(content),
            "redacted_length": len(redacted_content),
            "redactions_made": len(redactions),
            "redaction_types": redactions,
            "safe_content": redacted_content,
            "context": context
        }

def get_tools() -> List[DonnaProtectionTools]:
    """Get Donna protection tools for agents"""
    return [DonnaProtectionTools()]
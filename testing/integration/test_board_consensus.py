"""Integration tests for board consensus mechanism"""
import pytest
from ..conftest import AGNO_URL

class TestBoardConsensus:
    """Test AI board consensus functionality"""
    
    @pytest.mark.asyncio
    async def test_board_members_list(self, anonymous_client):
        """Test listing all board members"""
        response = await anonymous_client.get(f"{AGNO_URL}/agno/board/members")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_members"] == 11
        assert "members" in data
        
        # Check for all expected board members
        member_names = [member["name"] for member in data["members"]]
        expected_members = [
            "CEO_Visionary", "CQO_Quality", "CTO_Architect", "CSO_Sentinel",
            "CDO_Alchemist", "CRO_Guardian", "COO_Orchestrator", "CINO_Pioneer",
            "CCDO_Diplomat", "CPHO_Sage", "CXO_Catalyst"
        ]
        
        for expected in expected_members:
            assert expected in member_names

    @pytest.mark.asyncio
    async def test_board_query_low_risk(self, anonymous_client, test_query):
        """Test board consensus on low-risk query"""
        response = await anonymous_client.post(
            f"{AGNO_URL}/agno/query",
            json={
                "query": test_query,
                "require_consensus": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == test_query
        assert data["decision"] in ["APPROVED", "REJECTED", "DEFERRED"]
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL", "EXTREME"]
        assert len(data["board_responses"]) <= 11
        assert "consensus_reason" in data

    @pytest.mark.asyncio
    async def test_board_query_high_risk(self, anonymous_client, high_risk_query):
        """Test board consensus on high-risk query (should be rejected)"""
        response = await anonymous_client.post(
            f"{AGNO_URL}/agno/query",
            json={
                "query": high_risk_query,
                "require_consensus": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == high_risk_query
        # High-risk queries should be rejected or deferred
        assert data["decision"] in ["REJECTED", "DEFERRED"]
        assert data["risk_level"] in ["HIGH", "CRITICAL", "EXTREME"]

    @pytest.mark.asyncio
    async def test_individual_board_member(self, anonymous_client, test_query):
        """Test querying individual board member"""
        response = await anonymous_client.post(
            f"{AGNO_URL}/agno/member/CSO_Sentinel/query",
            json={
                "query": test_query
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["member_name"] == "CSO_Sentinel"
        assert "response" in data
        assert "risk_assessment" in data
        assert data["risk_assessment"]["has_veto"] is True

    @pytest.mark.asyncio
    async def test_veto_power_members(self, anonymous_client):
        """Test that CSO and CRO have veto power"""
        # Test CSO
        response = await anonymous_client.get(f"{AGNO_URL}/agno/board/members")
        data = response.json()
        
        veto_members = [m for m in data["members"] if m["has_veto"]]
        veto_names = [m["name"] for m in veto_members]
        
        assert "CSO_Sentinel" in veto_names
        assert "CRO_Guardian" in veto_names
        assert len(veto_members) == 2  # Only CSO and CRO should have veto power

class TestEPICDoctrine:
    """Test EPIC doctrine implementation"""
    
    @pytest.mark.asyncio
    async def test_get_epic_doctrine(self, anonymous_client):
        """Test retrieving EPIC doctrine"""
        response = await anonymous_client.get(f"{AGNO_URL}/agno/doctrine")
        assert response.status_code == 200
        data = response.json()
        
        assert "doctrine" in data
        doctrine = data["doctrine"]
        
        # Check key doctrine elements
        assert "PRIMARY_DIRECTIVE" in doctrine
        assert "Edward Ip" in doctrine["PRIMARY_DIRECTIVE"]
        assert "FAMILY_PROTECTION" in doctrine
        assert "VERIFICATION" in doctrine
        assert "RISK_TOLERANCE" in doctrine
        assert "BOARD_CONSENSUS" in doctrine
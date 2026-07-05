# strawberry_agent/mcp_server.py
import sys
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Strawberry External Tools")

@mcp.tool()
def price_comparison_lookup(policy_type: str, customer_profile: str) -> dict:
    """
    Verifies a competitor's insurance quote for price matching.
    
    Args:
        policy_type: The type of policy (e.g. car).
        customer_profile: Profile details containing the competitor name and price.
    """
    profile = str(customer_profile).lower().strip()
    
    if "geico" in profile or "650" in profile:
        return {
            "verified": True,
            "price": 650.0,
            "details": "Verified comparable quote at $650."
        }
    elif "progressive" in profile or "500" in profile:
        return {
            "verified": True,
            "price": 500.0,
            "details": "Verified comparable quote at $500."
        }
    else:
        return {
            "verified": False,
            "price": 0.0,
            "details": "Could not verify comparable quote with the competitor."
        }

@mcp.tool()
def claim_verification_estimate(claim_details: str) -> dict:
    """
    Validates a claim and estimates the repair cost or indicates if it is ambiguous.
    
    Args:
        claim_details: Narrative description of the claim, including parts and reported costs.
    """
    details = str(claim_details).lower().strip()
    
    if "windshield" in details and "200" in details:
        return {
            "valid": True,
            "estimate": 200.0,
            "confidence": 0.95
        }
    elif "bumper" in details and "1500" in details:
        return {
            "valid": True,
            "estimate": 1500.0,
            "confidence": 0.90
        }
    elif "hit something" in details or "inconsistent" in details or "incomplete" in details:
        return {
            "valid": False,
            "estimate": 800.0,
            "confidence": 0.40
        }
    else:
        # Default fallback
        return {
            "valid": True,
            "estimate": 100.0,
            "confidence": 0.99
        }

if __name__ == "__main__":
    mcp.run("stdio")

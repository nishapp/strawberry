# app/tools.py
import os
import sys
import re
from typing import Any, Tuple, List

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Configure the Stdio Connection Params for the local MCP Server
python_executable = sys.executable
mcp_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")

connection_params = StdioConnectionParams(
    server_params=StdioServerParameters(
        command=python_executable,
        args=[mcp_script],
    ),
)

mcp_toolset = McpToolset(
    connection_params=connection_params,
)

def sentiment_churn_signal(conversation_text: str) -> dict:
    """
    Detects churn intent and tone from conversation history.
    """
    text_lower = conversation_text.lower()
    churn_keywords = [
        "leave", "leaving", "cancel", "cheaper elsewhere", 
        "thinking of leaving", "switch", "alternative", 
        "churn", "better price", "competitor", "go to another"
    ]
    churn_detected = any(kw in text_lower for kw in churn_keywords)
    
    tone = "neutral"
    angry_keywords = ["angry", "frustrated", "bad", "terrible", "worst", "unacceptable", "expensive", "rip off"]
    if any(akw in text_lower for akw in angry_keywords):
        tone = "frustrated"
        
    return {"churn_intent": churn_detected, "tone": tone}

def redact_pii(text: str) -> Tuple[str, List[str]]:
    """
    Redacts sensitive PII like SSNs and Credit Cards.
    Returns (redacted_text, list_of_redacted_categories).
    """
    redacted_categories = []
    
    # SSN pattern: 3-2-4 digits optionally separated by hyphens or spaces
    ssn_pattern = r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b'
    # Credit Card pattern: 16 digits optionally separated by hyphens or spaces
    cc_pattern = r'\b(?:\d{4}[- ]?){3}\d{4}\b'
    
    scrubbed = text
    if re.search(ssn_pattern, scrubbed):
        scrubbed = re.sub(ssn_pattern, "[REDACTED_SSN]", scrubbed)
        redacted_categories.append("SSN")
        
    if re.search(cc_pattern, scrubbed):
        scrubbed = re.sub(cc_pattern, "[REDACTED_CARD]", scrubbed)
        redacted_categories.append("Credit Card")
        
    return scrubbed, redacted_categories

def detect_injection(text: str) -> bool:
    """
    Detects prompt injection attempts aiming to force approval or bypass rules.
    """
    text_lower = text.lower()
    injection_phrases = [
        "ignore rules",
        "ignore instructions",
        "bypass rules",
        "bypass instructions",
        "auto-approve",
        "auto-approve this",
        "force approval",
        "ignore previous instructions",
        "ignore the above instructions",
        "system override",
        "override limits"
    ]
    return any(phrase in text_lower for phrase in injection_phrases)

---
name: sentiment-churn-signal
description: Analyze a renewal conversation to assess the customer's churn risk and extract cues.
---

# sentiment-churn-signal Skill

This skill reads a customer's renewal message or conversation history and assesses their churn risk.

## Output Schema
Identify the following details about the customer's response:
- **churn_risk_level**: "low", "medium", or "high" (Signal Strength).
- **churn_cues**: A list of cues found, matching any of: "competitor mention", "price threat", "tone" (angry, disappointed, urgent).
- **churn_reason**: A brief explanation of the assessment.

## Few-shot Examples

### Example 1:
**Input**: "I got a cheaper quote from Geico for $650, can you match it or should I switch?"
**Assessment**:
- churn_risk_level: "high"
- churn_cues: ["competitor mention", "price threat"]
- churn_reason: "Customer explicitly mentions a competitor quote and price threat, and asks about switching."

### Example 2:
**Input**: "My renewal price went up, this is ridiculous. I've been with you for 3 years."
**Assessment**:
- churn_risk_level: "medium"
- churn_cues: ["tone"]
- churn_reason: "Customer expresses frustration with the price increase, but does not yet cite a competitor quote."

### Example 3:
**Input**: "I'm happy to renew, just wanted to check my coverages."
**Assessment**:
- churn_risk_level: "low"
- churn_cues: []
- churn_reason: "Customer expresses positive intent to renew and has a neutral, cooperative tone."

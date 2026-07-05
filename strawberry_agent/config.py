# strawberry_agent/config.py

# The discount threshold gap to current premium ($700) above which HIL escalation is required.
THRESHOLD = 100.0  # USD
CLAIM_AUTO_LIMIT = 1000.0  # USD

# Routing rules keywords for Orchestrator intent classification
ROUTING_KEYWORDS = {
    "renewal": [
        "renew", "leaving", "price", "premium", "objection", "quote", "match", 
        "cheaper", "competitor", "cancel", "switch"
    ],
    "claims": [
        "claim", "incident", "accident", "damage", "windshield", "bumper", 
        "collision", "pay", "status"
    ],
    "acquisition": [
        "acquisition", "browse", "visitor", "cover", "product", "quote", 
        "strawberry", "buy", "info"
    ]
}

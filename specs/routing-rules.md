# Routing & Escalation Rules

> Deterministic logic. This lives in **code**, never in the model's hands.
> (Day 4: keep business rules in code; the LLM is only for judgment.)

## 1. Intent classification (Orchestrator)

The Orchestrator reads the opening message + any session metadata and classifies
into exactly one route:

| Signal in the conversation                                   | Route          |
|--------------------------------------------------------------|----------------|
| Browsing, no policy yet, asking about products / quotes      | `acquisition`  |
| Has a policy, renewal window, mentions competitor / price    | `renewal`      |
| Has a policy, reporting an incident / asking about a claim   | `claims`       |
| None of the above / ambiguous                                | `acquisition` (default; safe — no money moves) |

## 2. Renewal discount threshold

```
THRESHOLD = 100            # USD
gap = current_premium - verified_competitor_price

if not competitor_price_verified:
    -> decline_auto_discount, continue persuasion (no price match)
elif gap <= 0:
    -> already competitive, no discount needed
elif gap <= THRESHOLD:
    -> agent may auto-approve a match up to the verified price
else:                       # gap > THRESHOLD
    -> ESCALATE to human (RequestInput); agent may NOT approve
```

**Worked examples** (current premium $700):
- Competitor verified at **$650** → gap $50 → **auto-approve** the match.
- Competitor verified at **$500** → gap $200 → **human review required**.
- Competitor claim **unverifiable** → no automatic discount; keep persuading.

## 3. Claims escalation

```
CLAIM_AUTO_LIMIT = 1000     # USD, illustrative
if injection_or_pii_flagged:
    -> human review (security event)
elif claim_amount <= CLAIM_AUTO_LIMIT and claim_is_unambiguous:
    -> agent resolves / estimates directly
else:                        # high value OR ambiguous
    -> ESCALATE to human (RequestInput)
```

## 4. Security pre-screen (runs before the LLM on renewal & claims)

1. **PII redaction** — scrub SSNs, card numbers; remember which categories were
   redacted; clean the human-approval payload too.
2. **Injection detection** — if the text tries to force approval / bypass rules,
   do not pass it to the model; route to human and flag a security event.
3. Clean messages continue to the agent.

## 5. Tool classification (reference)

| Tool                          | Type  | Why |
|-------------------------------|-------|-----|
| `price_comparison_lookup`     | MCP   | external reach — verifies competitor price |
| `claim_verification_estimate` | MCP   | external reach — validates / estimates a claim |
| `sentiment_churn_signal`      | Skill | know-how — reads churn intent + tone |
| threshold / routing / HIL gate| Code  | deterministic rules — never the model |

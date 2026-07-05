# Strawberry — Behaviour Specs

The source of truth for the build. Written **before** code so the agent never
guesses (Day 5: spec-driven development; code is disposable).

```
specs/
├── AGENTS.md            # always-on conventions + architecture + hard rules
├── routing-rules.md     # deterministic thresholds, routing, escalation, security
├── README.md            # this file
└── features/
    ├── acquisition.feature   # CX Agent
    ├── renewal.feature       # Renewal Agent (fact-check + threshold + HIL)
    └── claims.feature        # Claims Agent (HIL)
```

## How to use these

1. **Sign-off first.** Both partners read and agree. Catching a logic flaw here
   is far cheaper than after 1,000 lines of generated code.
2. **Feed them to the build agent.** In Antigravity, point the agent at this
   folder. The `.feature` scenarios become the build target and, later, the
   evaluation cases.
3. **Keep them honest.** If behaviour and code disagree, the code is wrong.

## Why Gherkin

`Scenario / Given / When / Then` forces State → Action → Outcome thinking, which
removes ambiguity for the model. Narrative conventions stay in Markdown
(`AGENTS.md`); structured rules sit in `routing-rules.md`. This Markdown +
structured hybrid is the format the course recommends for Gemini.

## Coverage map (each scenario → an eval case later)

- Acquisition: accurate answers, objection handling, scope control, no discounts
- Renewal: churn detection, verified-match-within-threshold, over-threshold HIL,
  unverifiable-claim refusal, injection short-circuit, PII redaction
- Claims: low-value direct resolve, high-value HIL, ambiguous HIL, honest status,
  injection handling

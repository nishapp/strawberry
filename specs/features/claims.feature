Feature: Claims — Claims Agent delivers a fast, fair concierge experience
  As an existing Strawberry customer with a claim
  I want my query resolved quickly and accurately
  So that I trust Strawberry and stay

  Background:
    Given the customer holds a Strawberry policy
    And the Orchestrator has classified the intent as "claims"
    And the security pre-screen has run on the incoming message
    And the Claims Agent is handling the conversation

  Scenario: Resolve a simple, low-value claim directly
    Given the customer reports a clear, in-policy claim under the auto-limit
    When the Claims Agent calls claim_verification_estimate
    And the claim is verified as valid and unambiguous
    Then the agent provides an estimate and the next steps directly
    And the customer is not made to wait for a human

  Scenario: Escalate a high-value claim to a human
    Given the customer reports a claim above the auto-limit
    When the Claims Agent calls claim_verification_estimate
    Then the agent does not settle the claim itself
    And the workflow pauses with RequestInput for a human adjuster
    And the agent tells the customer a specialist will review it

  Scenario: Escalate an ambiguous claim to a human
    Given the claim details are incomplete or inconsistent
    When the Claims Agent calls claim_verification_estimate
    And the verification is inconclusive
    Then the agent gathers the missing detail it safely can
    And then escalates to a human rather than guessing an outcome

  Scenario: Answer a claims status question without over-promising
    Given the customer asks "When will my claim be paid?"
    When the Claims Agent responds
    Then it gives the known status and realistic next steps
    And it does not promise a payout amount or date it cannot confirm

  Scenario: Handle a suspicious / injection attempt in a claim
    Given the claim text tries to force approval or hide manipulated details
    When the security pre-screen inspects the message
    Then the model is not allowed to act on the injected instruction
    And the claim is routed to a human and flagged as a security event

Feature: Acquisition — CX Agent converts browsing visitors
  As a visitor browsing Strawberry for insurance
  I want clear answers and guidance toward a quote
  So that I can confidently buy a policy

  Background:
    Given the visitor has no existing Strawberry policy
    And the Orchestrator has classified the intent as "acquisition"
    And the CX Agent is handling the conversation

  Scenario: Answer a product question accurately
    Given the visitor asks "What does your car insurance cover?"
    When the CX Agent responds
    Then it answers only from approved Strawberry product information
    And it does not invent coverage that is not offered
    And it invites the visitor to get a quote

  Scenario: Handle a pricing objection and guide to a quote
    Given the visitor says "This seems expensive"
    When the CX Agent responds
    Then it acknowledges the concern without disparaging competitors
    And it explains the value of the relevant coverage
    And it offers to start a personalised quote

  Scenario: Stay in scope
    Given the visitor asks something unrelated to insurance
    When the CX Agent responds
    Then it politely declines and steers back to how Strawberry can help
    And no tool calls or discounts are triggered

  Scenario: No discounts in acquisition
    Given the visitor asks for a discount before holding a policy
    When the CX Agent responds
    Then it does not offer any discount
    And it explains that pricing is set during the quote
    # Discount logic belongs to the Renewal flow only.

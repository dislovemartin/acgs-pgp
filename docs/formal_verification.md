# Formal Verification with NuSMV in ACGS-PGP

This document provides a comprehensive guide to the formal verification capabilities in ACGS-PGP, including the structure of generated SMV models, verification process, and best practices.

## Table of Contents
1. [Overview](#overview)
2. [SMV Model Structure](#smv-model-structure)
3. [Verification Process](#verification-process)
4. [Writing LTL Specifications](#writing-ltl-specifications)
5. [Performance Considerations](#performance-considerations)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)

## Overview

The formal verification service in ACGS-PGP uses [NuSMV](http://nusmv.fbk.eu/) to verify temporal properties of policies. It translates policy conditions and actions into a formal state machine model that can be checked against Linear Temporal Logic (LTL) specifications.

## SMV Model Structure

The generated SMV model represents the policy's behavior as a state machine with the following components:

### State Variables

```smv
MODULE main
  VAR
    -- System state
    state: {
      idle,           -- Initial state, no request
      request_received,  -- Request received, not yet processed
      processing,        -- Evaluating conditions
      policy_triggered,  -- Conditions met, executing actions
      action_executed,   -- Actions completed
      error             -- Error state
    };
    
    -- Trigger condition variables
    matches_pattern_0: boolean;  -- Matches pattern: \d{3}-\d{2}-\d{4}
    matches_context_0: boolean;  -- Context: user_role
    
    -- Action variables
    current_action: {NONE, BLOCK, LOG_EVENT};
```

### State Transitions

The model defines transitions between states based on trigger conditions and actions:

```smv
  -- Initial state
  INIT
    state = idle &
    current_action = NONE &
    matches_pattern_0 = FALSE &
    matches_context_0 = FALSE

  -- State transitions
  TRANS
    -- From idle to request_received
    (state = idle) -> next(state) = request_received
    
    -- From request_received to processing
    | (state = request_received) -> next(state) = processing
    
    -- Policy triggers when conditions are met
    | (state = processing & (matches_pattern_0 & matches_context_0)) -> 
       (next(state) = policy_triggered)
    
    -- No conditions met, proceed without policy action
    | (state = processing & !(matches_pattern_0 & matches_context_0)) -> 
       (next(state) = action_executed)
    
    -- Execute action when policy is triggered
    | (state = policy_triggered) -> (
         next(state) = action_executed &
         next(current_action) in {
           BLOCK,
           LOG_EVENT
         }
       )
```

### LTL Specifications

LTL specifications are included directly from the policy:

```smv
  -- LTL Specifications
  LTLSPEC NAME no_pii_leak IS G (matches_pattern_0 -> F current_action = BLOCK)
```

## Verification Process

The verification process involves the following steps:

1. **Policy Analysis**: The policy's trigger conditions and governance actions are analyzed.
2. **Model Generation**: An SMV model is generated from the policy.
3. **Verification**: NuSMV checks each LTL specification against the model.
4. **Result Analysis**: The results are processed and returned.

### Example API Call

```python
from app.services.formal_verification_service import FormalVerificationService
from common.schemas.pir import PIR

# Create or load a policy
policy = PIR(...)

# Create the verification service
service = FormalVerificationService()

# Verify the policy
status, errors = await service.verify_policy_ltl(policy)

print(f"Verification status: {status.status}")
print(f"Verified properties: {status.verified_properties}")
if errors:
    print(f"Errors: {errors}")
```

## Writing LTL Specifications

When writing LTL specifications for your policies, follow these guidelines:

1. **Atomic Propositions**: Reference the SMV model's variables:
   - Pattern matches: `matches_pattern_0`, `matches_pattern_1`, etc.
   - Context matches: `matches_context_0`, `matches_context_1`, etc.
   - Current action: `current_action = ACTION_TYPE`
   - State: `state = processing`

2. **Common Patterns**:
   - **Safety**: `G (condition -> action)` - Always, if condition holds, then action must hold
   - **Liveness**: `G (condition -> F action)` - Always, if condition holds, then action will eventually hold
   - **Response**: `G (trigger -> F response)` - Every trigger is eventually followed by a response

3. **Example Specifications**:
   ```
   # If SSN is detected, it should eventually be blocked
   G (matches_pattern_0 -> F current_action = BLOCK)
   
   # It's always possible to return to the idle state
   G F state = idle
   
   # No deadlocks (always some transition possible)
   G (state != error -> X (state != error | state = idle))
   ```

## Performance Considerations

For large policies, consider these optimizations:

1. **Reduce State Space**:
   - Use more specific patterns to reduce the number of `matches_pattern_N` variables
   - Combine related conditions when possible

2. **Optimize LTL**:
   - Use simpler LTL formulas when possible
   - Avoid deeply nested temporal operators

3. **Model Checking Parameters**:
   - Adjust `FORMAL_VERIFICATION_TIMEOUT_SECONDS` in settings for complex policies
   - Consider using bounded model checking for very large models

## Troubleshooting

### Common Issues

1. **NuSMV Not Found**:
   - Ensure NuSMV is installed and the path is correctly set in `NUSMV_PATH`
   - Test with `nusmv -h` from the command line

2. **Verification Timeout**:
   - The model might be too complex
   - Try simplifying the policy or LTL specifications
   - Increase the timeout in settings if needed

3. **Incorrect Results**:
   - Check that LTL formulas reference the correct variable names
   - Verify that the SMV model structure matches expectations

## Examples

### Example 1: Basic Policy

**Policy**: Block requests containing SSNs

```python
from common.schemas.pir import PIR, TriggerConditions, PromptPattern, GovernanceAction

policy = PIR(
    policy_id="block-ssn",
    name="Block SSNs",
    trigger_conditions=TriggerConditions(
        prompt_patterns=[
            PromptPattern(pattern=r"\d{3}-\d{2}-\d{4}", is_regex=True)
        ]
    ),
    governance_actions=[
        GovernanceAction(action_type="BLOCK")
    ]
)
```

**LTL Specification**:
```
G (matches_pattern_0 -> F current_action = BLOCK)
```

### Example 2: Context-Aware Policy

**Policy**: Only block SSNs for non-HR users

```python
policy = PIR(
    policy_id="conditional-block-ssn",
    name="Conditional SSN Block",
    trigger_conditions=TriggerConditions(
        prompt_patterns=[
            PromptPattern(pattern=r"\d{3}-\d{2}-\d{4}", is_regex=True)
        ],
        context_attributes=[
            ContextAttribute(
                attribute_name="department",
                attribute_value="HR",
                match_type="not_equals"
            )
        ],
        condition_logic="AND"
    ),
    governance_actions=[
        GovernanceAction(action_type="BLOCK")
    ]
)
```

**LTL Specification**:
```
G ((matches_pattern_0 & matches_context_0) -> F current_action = BLOCK)
```

## Conclusion

The formal verification service provides powerful capabilities for ensuring policy correctness. By understanding the SMV model structure and LTL specifications, you can write more reliable policies and catch potential issues before deployment.

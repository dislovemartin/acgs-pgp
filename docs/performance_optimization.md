# Performance Optimization for Formal Verification

This guide provides strategies for optimizing the performance of formal verification in ACGS-PGP, especially for large and complex policies.

## Table of Contents
1. [Understanding Performance Bottlenecks](#understanding-performance-bottlenecks)
2. [Policy Design Guidelines](#policy-design-guidelines)
3. [SMV Model Optimization](#smv-model-optimization)
4. [Verification Techniques](#verification-techniques)
5. [System Configuration](#system-configuration)
6. [Benchmarking](#benchmarking)
7. [Troubleshooting Performance Issues](#troubleshooting-performance-issues)

## Understanding Performance Bottlenecks

Formal verification performance is primarily affected by:

1. **State Space Size**: The number of possible states in the model
2. **Formula Complexity**: The complexity of LTL/CTL formulas
3. **Model Checking Algorithm**: The algorithm used by NuSMV (BDD-based, SAT-based, etc.)
4. **System Resources**: Available CPU and memory

## Policy Design Guidelines

### 1. Minimize Trigger Conditions

**Inefficient**:
```python
# 10 separate patterns
patterns = [
    PromptPattern(pattern=f"term_{i}") for i in range(10)
]
```

**Optimized**:
```python
# Single pattern matching any of the terms
patterns = [
    PromptPattern(pattern="term_(1|2|3|4|5|6|7|8|9|0)", is_regex=True)
]
```

### 2. Use Efficient Pattern Matching

```python
# Less efficient - multiple patterns
patterns = [
    PromptPattern(pattern="ssn", is_regex=False),
    PromptPattern(pattern="social security", is_regex=False),
]

# More efficient - single pattern with alternation
patterns = [
    PromptPattern(pattern="ssn|social security", is_regex=True)
]
```

### 3. Simplify Context Conditions

```python
# Complex nested conditions
conditions = [
    {"attribute": "department", "op": "equals", "value": "HR"},
    {"attribute": "clearance_level", "op": "greater_than", "value": 3}
]

# Simplified with pre-computed attribute
conditions = [
    {"attribute": "hr_high_clearance", "op": "equals", "value": True}
]
```

## SMV Model Optimization

### 1. Variable Ordering

Good variable ordering can significantly impact BDD size. Place related variables together:

```smv
-- Good ordering
VAR
  state: {idle, processing, done};
  matches_pattern: boolean;
  user_role: {admin, user, guest};
  current_action: {NONE, ALLOW, BLOCK};
```

### 2. State Space Reduction

Use abstractions to reduce the state space:

```python
# Instead of tracking exact values, use categories
if user_clearance >= 5:
    context_attrs.append(ContextAttribute("clearance_level", "high"))
else:
    context_attrs.append(ContextAttribute("clearance_level", "low"))
```

### 3. Symmetry Reduction

Group similar states to reduce the state space:

```smv
-- Instead of tracking individual users
user_role: {admin, privileged_user, regular_user, guest};

-- Use in transitions
TRANS
  (state = processing & user_role = admin) -> ...
  | (state = processing & user_role = privileged_user) -> ...
  | (state = processing & user_role = regular_user) -> ...
```

## Verification Techniques

### 1. Bounded Model Checking (BMC)

For large models, use bounded model checking with a depth limit:

```python
# In formal_verification_service.py
command = [
    self.model_checker_path,
    "-bmc",           # Enable bounded model checking
    "-bmc_length", "50",  # Set bound to 50 steps
    model_filepath
]
```

### 2. Incremental Verification

Break down complex verifications:

```python
# Verify properties one at a time
for spec in policy.temporal_logic_annotations.ltl_specifications:
    status = await verify_single_ltl(policy, spec)
    # Handle result
```

### 3. Property Decomposition

Split complex properties into simpler ones:

```
# Complex property
G ((a & b) -> (c U d))

# Decomposed
G (a -> (c U d))
G (b -> (c U d))
```

## System Configuration

### 1. Memory Allocation

Increase Java heap size for NuSMV (if using Java-based version):

```bash
export NUSMV_MEMORY_LIMIT=8192  # 8GB
```

### 2. Parallel Verification

Run multiple verifications in parallel:

```python
import asyncio

async def verify_multiple_policies(policies):
    tasks = [verify_policy_ltl(policy) for policy in policies]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. Caching

Cache verification results for unchanged policies:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def cached_verify(policy_id, policy_hash):
    # Perform verification
    return result
```

## Benchmarking

### 1. Performance Metrics

Track these metrics:
- Model generation time
- Verification time per property
- Peak memory usage
- State space size

### 2. Example Benchmark Script

```python
import time
import psutil
import asyncio
from app.services.formal_verification_service import FormalVerificationService

def get_memory_usage():
    return psutil.Process().memory_info().rss / (1024 * 1024)  # MB

async def benchmark_policy(policy):
    service = FormalVerificationService()
    
    # Measure model generation
    start_time = time.time()
    smv_model = service._generate_smv_model(policy)
    gen_time = time.time() - start_time
    
    # Measure verification
    start_mem = get_memory_usage()
    start_time = time.time()
    
    status, errors = await service.verify_policy_ltl(policy)
    
    verif_time = time.time() - start_time
    peak_mem = get_memory_usage() - start_mem
    
    return {
        'policy_id': policy.policy_id,
        'model_gen_time': gen_time,
        'verification_time': verif_time,
        'memory_used_mb': peak_mem,
        'status': status.status,
        'num_properties': len(policy.temporal_logic_annotations.ltl_specifications)
    }
```

## Troubleshooting Performance Issues

### 1. Model Too Large

**Symptoms**:
- Long model generation time
- High memory usage
- Verification timeouts

**Solutions**:
- Simplify trigger conditions
- Use more abstract state representations
- Increase system resources

### 2. Verification Timeout

**Symptoms**:
- Verification doesn't complete within timeout
- CPU usage remains high

**Solutions**:
- Use bounded model checking
- Simplify LTL formulas
- Increase timeout value

### 3. Memory Exhaustion

**Symptoms**:
- Process killed by OOM killer
- High memory usage

**Solutions**:
- Optimize variable ordering
- Use symmetry reduction
- Increase system memory
- Use 64-bit NuSMV build

## Conclusion

Optimizing formal verification performance requires a combination of policy design, model optimization, and system configuration. By following these guidelines and continuously monitoring performance, you can effectively verify even complex policies in ACGS-PGP.

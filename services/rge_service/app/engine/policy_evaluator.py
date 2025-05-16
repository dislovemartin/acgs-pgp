from typing import Dict, List, Any, Optional, Tuple, Union, cast
import json
import re
from datetime import datetime, timezone
from enum import Enum
import sys
import os

# Import the common schemas - adjust the import path as needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))
from common.schemas.pir import (
    PIR, TriggerCondition, GovernanceAction, TriggerConditionType, GovernanceActionType,
    TriggerConditions, PromptPattern, ContextAttribute, ToolUsageRequest, ResponsePattern,
    Scope, PolicyStatus, PolicySeverity
)

class EvaluationResult(Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    MODIFY = "MODIFY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

class PolicyEvaluation:
    def __init__(self, policy: PIR, matched_condition: Dict[str, Any]):
        self.policy = policy
        self.matched_condition = matched_condition
        self.applied_actions: List[Tuple[GovernanceAction, Dict[str, Any]]] = []
        self.evaluation_time = datetime.now(timezone.utc)

class PolicyEvaluator:
    """
    The PolicyEvaluator is responsible for evaluating prompts and actions against
    the active policies in the system.
    """

    def __init__(self):
        self.active_policies: List[PIR] = []

    def update_policies(self, policies: List[PIR]):
        """Update the list of active policies."""
        self.active_policies = policies

    def evaluate_prompt(
        self,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[EvaluationResult, List[PolicyEvaluation], str]:
        """
        Evaluate a prompt against all active policies.

        Args:
            prompt: The prompt text to evaluate
            metadata: Additional metadata about the prompt (user, session, etc.)

        Returns:
            A tuple containing:
                - The overall evaluation result
                - List of policy evaluations that were triggered
                - Modified prompt (if applicable)
        """
        if metadata is None:
            metadata = {}

        triggered_evaluations = []
        modified_prompt = prompt

        # Check each policy against the prompt
        for policy in self.active_policies:
            evaluation = self._evaluate_policy(policy, prompt, metadata)
            if evaluation:
                triggered_evaluations.append(evaluation)

        if not triggered_evaluations:
            return EvaluationResult.ALLOW, [], prompt

        # Apply actions in order of priority (highest first)
        triggered_evaluations.sort(
            key=lambda e: max((a[0].priority for a in e.applied_actions), default=0),
            reverse=True
        )

        # Apply the actions with the highest priority first
        for evaluation in triggered_evaluations:
            for action, action_ctx in evaluation.applied_actions:
                if action.action_type == GovernanceActionType.BLOCK_EXECUTION:
                    return EvaluationResult.BLOCK, triggered_evaluations, modified_prompt
                elif action.action_type == GovernanceActionType.MODIFY_PROMPT:
                    modified_prompt = self._apply_modifications(
                        modified_prompt,
                        action.parameters.get('modifications', [])
                    )
                elif action.action_type == GovernanceActionType.REQUIRE_APPROVAL:
                    return EvaluationResult.REQUIRE_APPROVAL, triggered_evaluations, modified_prompt

        return EvaluationResult.MODIFY, triggered_evaluations, modified_prompt

    def _evaluate_policy(
        self,
        policy: PIR,
        prompt: str,
        metadata: Dict[str, Any]
    ) -> Optional[PolicyEvaluation]:
        """Evaluate a single policy against the prompt."""
        # Only evaluate active policies
        if policy.status != PolicyStatus.ACTIVE:
            return None

        # Check if the policy applies to this context based on scope
        if not self._is_in_scope(policy.scope, metadata):
            return None

        evaluation = None

        # Handle both legacy and new trigger_conditions format
        if isinstance(policy.trigger_conditions, list):
            # Legacy format - list of TriggerCondition objects
            for condition in policy.trigger_conditions:
                if self._matches_condition(condition, prompt, metadata):
                    if evaluation is None:
                        evaluation = PolicyEvaluation(policy, condition.dict())

                    # Add all governance actions for this policy
                    for action in policy.governance_actions:
                        evaluation.applied_actions.append((action, {"triggered_by": condition.condition_type}))
        else:
            # New structured format - TriggerConditions object
            trigger_conditions = cast(TriggerConditions, policy.trigger_conditions)
            matched_conditions = []

            # Check prompt patterns
            for pattern in trigger_conditions.prompt_patterns:
                if self._matches_prompt_pattern(pattern, prompt):
                    matched_conditions.append({"type": "prompt_pattern", "pattern": pattern.dict()})

            # Check context attributes
            for attr in trigger_conditions.context_attributes:
                if self._matches_context_attribute(attr, metadata):
                    matched_conditions.append({"type": "context_attribute", "attribute": attr.dict()})

            # Check tool usage requests
            for tool_req in trigger_conditions.tool_usage_requests:
                if self._matches_tool_usage(tool_req, metadata):
                    matched_conditions.append({"type": "tool_usage", "tool": tool_req.dict()})

            # Check response patterns
            response_text = metadata.get("response_text", "")
            for pattern in trigger_conditions.response_patterns:
                if response_text and self._matches_response_pattern(pattern, response_text):
                    matched_conditions.append({"type": "response_pattern", "pattern": pattern.dict()})

            # Apply condition logic
            conditions_met = False
            if trigger_conditions.condition_logic == "ANY" and matched_conditions:
                conditions_met = True
            elif trigger_conditions.condition_logic == "ALL" and matched_conditions and len(matched_conditions) == len(trigger_conditions.prompt_patterns) + len(trigger_conditions.context_attributes) + len(trigger_conditions.tool_usage_requests) + len(trigger_conditions.response_patterns):
                conditions_met = True
            elif trigger_conditions.condition_logic == "CUSTOM" and trigger_conditions.custom_logic_expression:
                # Custom logic would be evaluated here
                # For now, default to ANY logic
                conditions_met = bool(matched_conditions)

            if conditions_met:
                evaluation = PolicyEvaluation(policy, {"matched_conditions": matched_conditions})

                # Add all governance actions for this policy
                for action in policy.governance_actions:
                    evaluation.applied_actions.append((action, {"triggered_by": "structured_conditions"}))

        return evaluation

    def _matches_condition(
        self,
        condition: TriggerCondition,
        prompt: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Check if a condition matches the prompt and metadata."""
        if condition.condition_type == TriggerConditionType.PROMPT_PATTERN:
            patterns = condition.parameters.get('patterns', [])
            for pattern in patterns:
                if re.search(re.escape(pattern), prompt, re.IGNORECASE):
                    return True

        elif condition.condition_type == TriggerConditionType.TOOL_USAGE:
            tools_used = metadata.get('tools_used', [])
            required_tools = condition.parameters.get('tool_names', [])
            if any(tool in required_tools for tool in tools_used):
                return True

        # Add more condition types as needed

        return False

    def _is_in_scope(self, scope: Scope, metadata: Dict[str, Any]) -> bool:
        """Check if the policy applies to this context based on scope."""
        # Check LLM model scope
        model_name = metadata.get("model_name", "")
        if scope.llm_models_inclusion == "include" and scope.llm_models_list and model_name not in scope.llm_models_list:
            return False
        if scope.llm_models_inclusion == "exclude" and scope.llm_models_list and model_name in scope.llm_models_list:
            return False

        # Check user role scope
        user_role = metadata.get("user_role", "")
        if scope.user_roles_inclusion == "include" and scope.user_roles_list and user_role not in scope.user_roles_list:
            return False
        if scope.user_roles_inclusion == "exclude" and scope.user_roles_list and user_role in scope.user_roles_list:
            return False

        # Check application scope
        application = metadata.get("application", "")
        if scope.applications_inclusion == "include" and scope.applications_list and application not in scope.applications_list:
            return False
        if scope.applications_inclusion == "exclude" and scope.applications_list and application in scope.applications_list:
            return False

        # Check data sensitivity scope
        data_sensitivity = metadata.get("data_sensitivity", "")
        if scope.data_sensitivity_inclusion == "minimum" and scope.data_sensitivity_levels:
            # Check if the data sensitivity level meets the minimum required
            # This would require a hierarchy of sensitivity levels
            # For now, just check if it's in the list
            if data_sensitivity not in scope.data_sensitivity_levels:
                return False
        elif scope.data_sensitivity_inclusion == "include" and scope.data_sensitivity_levels and data_sensitivity not in scope.data_sensitivity_levels:
            return False
        elif scope.data_sensitivity_inclusion == "exclude" and scope.data_sensitivity_levels and data_sensitivity in scope.data_sensitivity_levels:
            return False

        # Check custom scope attributes
        for key, value in scope.custom_scope_attributes.items():
            if key in metadata and metadata[key] != value:
                return False

        return True

    def _matches_prompt_pattern(self, pattern: PromptPattern, prompt: str) -> bool:
        """Check if a prompt pattern matches the prompt."""
        if pattern.is_regex:
            flags = 0 if pattern.case_sensitive else re.IGNORECASE
            try:
                if re.search(pattern.pattern, prompt, flags):
                    return True
            except re.error:
                # Log invalid regex pattern
                return False
        else:
            if pattern.case_sensitive:
                return pattern.pattern in prompt
            else:
                return pattern.pattern.lower() in prompt.lower()

        return False

    def _matches_context_attribute(self, attr: ContextAttribute, metadata: Dict[str, Any]) -> bool:
        """Check if a context attribute matches the metadata."""
        if attr.attribute_name not in metadata:
            return False

        value = metadata[attr.attribute_name]

        if attr.match_type == "exact":
            return value == attr.attribute_value
        elif attr.match_type == "contains":
            if isinstance(value, str) and isinstance(attr.attribute_value, str):
                return attr.attribute_value in value
            elif isinstance(value, list):
                return attr.attribute_value in value
            return False
        elif attr.match_type == "regex":
            if isinstance(value, str) and isinstance(attr.attribute_value, str):
                try:
                    return bool(re.search(attr.attribute_value, value))
                except re.error:
                    # Log invalid regex pattern
                    return False
            return False
        elif attr.match_type == "greater_than":
            try:
                return float(value) > float(attr.attribute_value)
            except (ValueError, TypeError):
                return False
        elif attr.match_type == "less_than":
            try:
                return float(value) < float(attr.attribute_value)
            except (ValueError, TypeError):
                return False

        return False

    def _matches_tool_usage(self, tool_req: ToolUsageRequest, metadata: Dict[str, Any]) -> bool:
        """Check if a tool usage request matches the metadata."""
        tools_used = metadata.get("tools_used", [])
        tool_params = metadata.get("tool_parameters", {})

        # Check if the tool is being used
        if tool_req.tool_name not in tools_used:
            return False

        # Check parameter constraints if provided
        if tool_req.parameter_constraints and tool_req.tool_name in tool_params:
            for param_name, param_value in tool_req.parameter_constraints.items():
                if param_name not in tool_params[tool_req.tool_name]:
                    return False
                if tool_params[tool_req.tool_name][param_name] != param_value:
                    return False

        return True

    def _matches_response_pattern(self, pattern: ResponsePattern, response_text: str) -> bool:
        """Check if a response pattern matches the response text."""
        if pattern.is_regex:
            flags = 0 if pattern.case_sensitive else re.IGNORECASE
            try:
                if re.search(pattern.pattern, response_text, flags):
                    return True
            except re.error:
                # Log invalid regex pattern
                return False
        else:
            if pattern.case_sensitive:
                return pattern.pattern in response_text
            else:
                return pattern.pattern.lower() in response_text.lower()

        return False

    def _apply_modifications(self, prompt: str, modifications: List[Dict[str, Any]]) -> str:
        """Apply modifications to the prompt based on the action parameters."""
        modified_prompt = prompt

        for mod in modifications:
            mod_type = mod.get('type')

            if mod_type == 'replace':
                modified_prompt = modified_prompt.replace(
                    mod['from'],
                    mod.get('to', '')
                )
            elif mod_type == 'prepend':
                modified_prompt = mod['text'] + modified_prompt
            elif mod_type == 'append':
                modified_prompt += mod['text']
            elif mod_type == 'regex_replace':
                modified_prompt = re.sub(
                    mod['pattern'],
                    mod.get('replacement', ''),
                    modified_prompt
                )

        return modified_prompt

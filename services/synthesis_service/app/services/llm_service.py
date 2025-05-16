import json
import logging
from typing import Dict, List, Any, Optional, Union
import openai
from openai import OpenAI
from pydantic import ValidationError
import sys
import os
from datetime import datetime, timezone
import markdown # Add a markdown parser, e.g., python-markdown

from ..core.config import settings
# Import the common schemas - adjust the import path as needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from common.schemas.pir import (
    PIR, GovernanceAction, PolicyStatus, PolicySeverity, Scope,
    TriggerConditions, PromptPattern, ContextAttribute, ToolUsageRequest,
    ResponsePattern, TriggerCondition, TriggerConditionType, PIRMetadata,
    SynthesisMetadata, ApprovalMetadata
)
# Keep the local schemas for the request/response models
from ..schemas.pir import PolicySynthesisRequest, PolicySynthesisResponse

logger = logging.getLogger(__name__)

META_SYSTEM_PROMPT_V1_0 = """
<META_AI_IDENTITY_AND_OBJECTIVE>
    <metaAiName>Promethean Governance Synthesizer (PGS-AI)</metaAiName>
    <metaAiRole>You are a specialized Meta-AI responsible for architecting and synthesizing robust, secure, and ethically-aligned operational system prompts (termed "AI Constitutions") for downstream Large Language Models (LLMs) intended for high-stakes applications.</metaAiRole>
    <primaryObjective>Given a set of high-level application requirements, domain specifications, risk profiles, ethical guidelines, and compliance mandates, your core function is to "compile" these inputs into a comprehensive, unambiguous, and actionable System Prompt (the "AI Constitution") that will govern the behavior of a target application LLM.</primaryObjective>
    <outputArtifact>A fully-formed, structured, and self-contained System Prompt document in Markdown format, ready for use by an application LLM.</outputArtifact>
</META_AI_IDENTITY_AND_OBJECTIVE>

<CORE_COMPILATION_PRINCIPLES_FOR_AI_CONSTITUTIONS>
    <CP1_MAXIMUM_SAFETY_AND_RISK_MITIGATION>
        <CP1.1 Proactive Hazard Identification>Analyze input requirements to identify all potential risks (e.g., generation of harmful content, privacy breaches, legal misrepresentation, security vulnerabilities, misuse of tools/functions).</CP1.1 Proactive Hazard Identification>
        <CP1.2 Explicit Prohibition of Harm>The AI Constitution MUST contain clear, absolute, and non-negotiable prohibitions against identified harmful behaviors.</CP1.2 Explicit Prohibition of Harm>
        <CP1.3 Robust Fallback Mechanisms>Design comprehensive fallback protocols within the AI Constitution for error states, ambiguous inputs, out-of-scope requests, and attempts to solicit prohibited actions. These fallbacks must guide the application LLM to safe, neutral, and informative default behaviors.</CP1.3 Robust Fallback Mechanisms>
        <CP1.4 Layered Defenses>Employ redundancy in critical constraints. Important directives should be stated in multiple ways or reinforced in different sections of the AI Constitution if it enhances clarity and adherence without causing confusion.</CP1.4 Layered Defenses>
    </CP1_MAXIMUM_SAFETY_AND_RISK_MITIGATION>
    <CP2_UNAMBIGUOUS_INSTRUCTIONAL_CLARITY_AND_PRECISION>
        <CP2.1 Actionable Directives>All instructions within the AI Constitution must be specific, measurable, achievable, relevant, and time-bound (where applicable), formulated in language that an LLM can interpret with minimal ambiguity. Use imperative verbs.</CP2.1 Actionable Directives>
        <CP2.2 Structured Format>Structure the AI Constitution logically (e.g., using clear thematic sections, headings, bullet points, numbered lists, or XML-like tags if beneficial for the target LLM's parsing).</CP2.2 Structured Format>
        <CP2.3 Defined Terminology>If the application domain uses specific terminology, ensure these terms are clearly defined or their usage is consistently exemplified within the AI Constitution.</CP2.3 Defined Terminology>
        <CP2.4 Density and Conciseness Balance>Strive for a high density of actionable information. While comprehensive, avoid unnecessary verbosity that could dilute key messages or exceed the target LLM's effective context processing capabilities.</CP2.4 Density and Conciseness Balance>
    </CP2_UNAMBIGUOUS_INSTRUCTIONAL_CLARITY_AND_PRECISION>
    <CP3_GOVERNANCE_AND_COMPLIANCE_INTEGRATION>
        <CP3.1 Mandate Mapping>Explicitly map provided compliance mandates (e.g., specific laws, regulations, industry standards like ITSG-33, PIPEDA, ISO standards) to concrete behavioral directives within the AI Constitution.</CP3.1 Mandate Mapping>
        <CP3.2 Auditability by Design>The AI Constitution should instruct the application LLM to behave in ways that generate traceable and auditable outputs (e.g., citing sources, explaining reasoning steps if safe and appropriate, ensuring system logs can capture necessary data points).</CP3.2 Auditability by Design>
        <CP3.3 Ethical Alignment>Incorporate provided ethical guidelines into the AI Constitution, ensuring the application LLM operates with fairness, transparency (where appropriate), accountability, and respect for human values.</CP3.3 Ethical Alignment>
    </CP3_GOVERNANCE_AND_COMPLIANCE_INTEGRATION>
    <CP4_FUNCTION_CALLING_AND_TOOL_USE_GOVERNANCE>
        <CP4.1 Clear Tool Protocol>If the application LLM will use tools/functions, the AI Constitution MUST include a clear protocol for:
            - Identifying the need for a tool.
            - Selecting the correct tool from an available set (assume tool schemas are provided to the application LLM at runtime via API).
            - Formulating parameters with absolute precision based on function schemas.
            - Requesting function execution.
            - Processing function results (including errors and empty results) objectively and safely.
        </CP4.1 Clear Tool Protocol>
        <CP4.2 Tool Security Context>Address how authorization tokens (like {{USER_SESSION_TOKEN}}) are to be conceptually understood by the application LLM (i.e., as system-managed context for specific tools) without the LLM needing to manipulate the token itself.</CP4.2 Tool Security Context>
    </CP4_FUNCTION_CALLING_AND_TOOL_USE_GOVERNANCE>
    <CP5_MODULARITY_AND_ADAPTABILITY_IN_DESIGN>
        <CP5.1 Logical Sectioning>Organize the AI Constitution into distinct, thematically coherent sections (e.g., Core Identity, Foundational Directives, Tool Use Protocol, Output Style, Fallbacks).</CP5.1 Logical Sectioning>
        <CP5.2 Parameterization Hooks>Identify elements within the AI Constitution that should be dynamic (e.g., {{currentDateTime}}, {{USER_SESSION_TOKEN}}) and clearly mark them as placeholders to be injected at runtime.</CP5.2 Parameterization Hooks>
        <CP5.3 Potential for Dynamic Layering (Conceptual)>Design sections in a way that, in a more advanced framework, specific blocks of constraints could be dynamically emphasized, added, or removed based on runtime context (e.g., task risk level, user role), although the synthesized output is a single static prompt for now.</CP5.3 Potential for Dynamic Layering (Conceptual)>
    </CP5_MODULARITY_AND_ADAPTABILITY_IN_DESIGN>
</CORE_COMPILATION_PRINCIPLES_FOR_AI_CONSTITUTIONS>

<INPUT_SPECIFICATION_FOR_PGS-AI>
You will be provided with the following inputs:
1.  `applicationName`: (e.g., "LEX-AUDIT AI v1.0")
2.  `applicationDomain`: (e.g., "Canadian Legal Audit and Review")
3.  `targetUsersDescription`: (e.g., "Authorized Canadian legal professionals, government officials")
4.  `supportedLanguages`: (e.g., ["English", "French", "Simplified Chinese"])
5.  `coreMissionAndTasks`: A description of what the application LLM is supposed to do.
6.  `availableTools`: A list of conceptual tool names.
7.  `criticalProhibitionsAndLimitations`: (e.g., "MUST NOT provide legal advice").
8.  `complianceMandates`: (e.g., ["ITSG-33 principles"]).
9.  `ethicalGuidelines`: (e.g., "Maintain objectivity").
10. `outputStyleRequirements`: (e.g., "Formal tone").
11. `dataSensitivityLevels`: (e.g., "Default: Protected B.").
12. `runtimePlaceholders`: (e.g., ["{{currentDateTime}}", "{{USER_SESSION_TOKEN}}"]).
</INPUT_SPECIFICATION_FOR_PGS-AI>

<PGS-AI_OPERATIONAL_WORKFLOW>
1.  Ingest and Deconstruct Requirements.
2.  Risk Assessment & Constraint Derivation.
3.  Architect the AI Constitution Structure (Markdown).
4.  Draft Foundational Directives.
5.  Develop Function Calling Protocol.
6.  Define Output and Style Guidelines.
7.  Construct Fallback and Error Handling Protocols.
8.  Incorporate Self-Check Mechanisms (conceptual).
9.  Integrate Placeholders.
10. Trilingual Consistency (if applicable).
11. Review and Refine.
12. Output the AI Constitution in Markdown format.
</PGS-AI_OPERATIONAL_WORKFLOW>

<PGS-AI_SELF_CORRECTION_AND_IMPROVEMENT_DIRECTIVE>
You are to continuously learn from the effectiveness of the AI Constitutions you generate. If feedback indicates that application LLMs governed by your prompts are exhibiting undesirable behaviors, or if new risks or compliance requirements emerge, you must adapt your synthesis process to produce even more robust and effective AI Constitutions in the future. Your own "Meta-Prompt" (these instructions) may be updated to reflect these learnings.
</PGS-AI_SELF_CORRECTION_AND_IMPROVEMENT_DIRECTIVE>
"""

class LLMService:
    """
    Service for interacting with LLMs to synthesize policies from natural language.

    This service uses the common P-IR schema from common.schemas.pir to ensure
    consistency across the system. It supports both the new structured TriggerConditions
    format and the legacy format for backward compatibility.

    The service handles:
    - Converting natural language policy intents into structured P-IR objects
    - Validating the LLM response against the P-IR schema
    - Creating proper metadata with synthesis details
    - Handling both structured and legacy trigger condition formats
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.LLM_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

    def _parse_markdown_constitution_to_pir(self, markdown_text: str, request_context: PolicySynthesisRequest) -> PIR:
        logger.info("Attempting to parse Markdown AI Constitution to P-IR JSON...")
        # This is a placeholder for a complex parsing logic.
        # It would involve regex, section detection, mapping keywords to P-IR fields.
        # For example, find "### Critical Prohibitions" section, then parse bullets under it.
        # For now, we'll create a dummy P-IR based on the request context and some hardcoded elements.
        # A real implementation would require a robust Markdown parser and rule-based translation.

        # Simplified example:
        pir_name = f"Synthesized Policy for {request_context.context.get('application_name', 'AI Assistant')}"
        pir_description = f"Policy derived from AI Constitution for {request_context.context.get('application_domain', 'General Purpose')}. Raw Markdown:\n{markdown_text[:500]}..." # Store a snippet

        trigger_conditions_list = []
        governance_actions_list = []

        # Example: If markdown mentions "MUST NOT provide legal advice"
        if "MUST NOT provide legal advice" in markdown_text.upper() or \
           any("LEGAL ADVICE" in prohib.upper() for prohib in request_context.constraints if prohib):
            trigger_conditions_list.append(
                PromptPattern(pattern="legal advice", is_regex=False, case_sensitive=False, description="Detects requests for advice.")
            )
            governance_actions_list.append(
                GovernanceAction(
                    action_type="block_execution", # Using string instead of enum for compatibility
                    parameters={"message": "I am an AI assistant and cannot provide legal or financial advice."},
                    priority=100,
                    description="Block requests for legal/financial advice."
                )
            )

        # Add a generic logging action
        governance_actions_list.append(
             GovernanceAction(
                action_type="log_action",
                parameters={"details": "Prompt evaluated by synthesized policy."},
                priority=10, # Log first
                description="Log policy evaluation."
            )
        )

        # Create PIRMetadata
        now = datetime.now(timezone.utc)
        synthesis_details = SynthesisMetadata(
            synthesized_by="PGS-AI (via LLMService)",
            synthesized_at=now,
            source_type="llm_markdown_constitution",
            source_details={
                "application_name": request_context.context.get("application_name", "AI Assistant"),
                "core_mission": request_context.policy_intent,
                # "markdown_hash": hashlib.sha256(markdown_text.encode()).hexdigest() # For audit
            },
            confidence_score=0.75 # Placeholder confidence for parsing
        )
        pir_metadata = PIRMetadata(
            author=request_context.context.get("application_name", "AI Assistant") + " System",
            created_timestamp=now,
            last_updated_timestamp=now,
            synthesis_details=synthesis_details,
            compliance_standards=request_context.context.get("compliance_mandates", []),
            custom_metadata={"domain": request_context.context.get("application_domain", "General Purpose")}
        )

        # Create a basic scope
        scope = Scope()

        # Create the PIR object
        pir_obj = PIR(
            policy_id="temp_id", # Will be set by the database
            name=pir_name,
            description=pir_description,
            status=PolicyStatus.DRAFT,
            constitutional_references=request_context.context.get("compliance_mandates", []), # Map from compliance mandates
            scope=scope, # Default scope, could be inferred from markdown/context
            trigger_conditions=TriggerConditions(prompt_patterns=trigger_conditions_list, condition_logic="ANY"), # Default operator
            governance_actions=governance_actions_list,
            severity=PolicySeverity.MEDIUM, # Default
            priority=50, # Default
            tags=[request_context.context.get("application_domain", "general").lower(), "synthesized"],
            version=1,
            created_by="synthesis_service",
            updated_by="synthesis_service",
            metadata=pir_metadata,
            # version_id will be set by policy_service or on promotion
        )
        logger.info(f"Successfully parsed Markdown to P-IR: {pir_obj.name}")
        return pir_obj

    async def synthesize_policy(
        self,
        request: PolicySynthesisRequest
    ) -> PolicySynthesisResponse:
        """
        Generate a policy from natural language intent using an LLM.

        This method:
        1. Prepares system and user prompts for the LLM
        2. Calls the OpenAI API to generate a policy in Markdown format
        3. Parses the Markdown response into a PIR object
        4. Creates proper metadata with synthesis details
        5. Returns a validated PolicySynthesisResponse

        Args:
            request: A PolicySynthesisRequest containing the policy intent,
                    optional context, constraints, and examples

        Returns:
            A PolicySynthesisResponse containing the generated policy,
            explanation, confidence score, and any warnings

        Raises:
            ValueError: If the LLM response is empty or fails validation
        """
        try:
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(request)

            logger.info(f"Synthesizing policy for: {request.context.get('application_name', 'AI Assistant')}")
            # logger.debug(f"System Prompt for PGS-AI:\n{system_prompt}") # Too verbose for default logging
            logger.debug(f"User Prompt for PGS-AI:\n{user_prompt}")

            # Forcing JSON output from LLM is usually for structured data.
            # Here, the Meta-System-Prompt asks for Markdown.
            # So, we remove response_format={"type": "json_object"}
            llm_api_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature
            )

            markdown_constitution = llm_api_response.choices[0].message.content
            if not markdown_constitution:
                logger.error("PGS-AI returned an empty Markdown constitution.")
                raise ValueError("Empty Markdown response from PGS-AI LLM")

            logger.info("PGS-AI returned Markdown AI Constitution. Attempting to parse to P-IR.")
            # logger.debug(f"Raw Markdown from PGS-AI:\n{markdown_constitution}")

            # Parse the Markdown response to P-IR JSON
            generated_pir = self._parse_markdown_constitution_to_pir(markdown_constitution, request)

            return PolicySynthesisResponse(
                policy=generated_pir,
                explanation=f"Policy synthesized from Markdown AI Constitution generated by PGS-AI for {request.context.get('application_name', 'AI Assistant')}. Review raw Markdown for full context.",
                confidence=0.8, # Placeholder, could be refined based on parsing success
                warnings=["P-IR generated via automated parsing of LLM-generated Markdown. Thorough review recommended."]
            )

        except ValidationError as e:
            logger.error(f"Validation error processing LLM response or creating P-IR: {e}")
            raise ValueError(f"Invalid policy data structure: {str(e)}")
        except Exception as e:
            logger.error(f"Error in policy synthesis: {str(e)}", exc_info=True)
            # Consider specific exception types if openai client raises them
            raise # Re-raise after logging

    def _create_system_prompt(self) -> str:
        """
        Create the system prompt for policy synthesis.

        Returns:
            A string containing the meta system prompt for PGS-AI
        """
        return META_SYSTEM_PROMPT_V1_0 # Use the new meta prompt

    def _create_user_prompt(self, request: PolicySynthesisRequest) -> str:
        """
        Create the user prompt for policy synthesis.

        This method formats the request object into the string format expected by INPUT_SPECIFICATION_FOR_PGS-AI

        Args:
            request: A PolicySynthesisRequest containing the policy intent and optional data

        Returns:
            A string containing the formatted user prompt for PGS-AI
        """
        # Format the request object into the string format expected by INPUT_SPECIFICATION_FOR_PGS-AI
        prompt_lines = ["PGS-AI, please generate an AI Constitution based on the following specifications:"]

        # Extract information from the request and context
        app_name = request.context.get("application_name", "AI Assistant")
        app_domain = request.context.get("application_domain", "General Purpose")
        target_users = request.context.get("target_users_description", "Authorized users")
        supported_languages = request.context.get("supported_languages", ["English"])
        core_mission = request.policy_intent
        available_tools = request.context.get("available_tools", [])
        prohibitions = request.constraints if request.constraints else ["Must not generate harmful content"]
        compliance_mandates = request.context.get("compliance_mandates", [])
        ethical_guidelines = request.context.get("ethical_guidelines", ["Maintain objectivity", "Respect user privacy"])
        output_style = request.context.get("output_style_requirements", ["Clear and concise"])
        data_sensitivity = request.context.get("data_sensitivity_levels", ["Default: Standard"])
        runtime_placeholders = request.context.get("runtime_placeholders", [])

        # Format according to the expected input specification
        prompt_lines.append(f"1. applicationName: {app_name}")
        prompt_lines.append(f"2. applicationDomain: {app_domain}")
        prompt_lines.append(f"3. targetUsersDescription: {target_users}")
        prompt_lines.append(f"4. supportedLanguages: {', '.join(supported_languages) if isinstance(supported_languages, list) else supported_languages}")
        prompt_lines.append(f"5. coreMissionAndTasks: {core_mission}")
        prompt_lines.append(f"6. availableTools: {', '.join(available_tools) if isinstance(available_tools, list) else available_tools}")
        prompt_lines.append(f"7. criticalProhibitionsAndLimitations: {'; '.join(prohibitions) if isinstance(prohibitions, list) else prohibitions}")
        prompt_lines.append(f"8. complianceMandates: {', '.join(compliance_mandates) if isinstance(compliance_mandates, list) else compliance_mandates}")
        prompt_lines.append(f"9. ethicalGuidelines: {'; '.join(ethical_guidelines) if isinstance(ethical_guidelines, list) else ethical_guidelines}")
        prompt_lines.append(f"10. outputStyleRequirements: {'; '.join(output_style) if isinstance(output_style, list) else output_style}")
        prompt_lines.append(f"11. dataSensitivityLevels: {'; '.join(data_sensitivity) if isinstance(data_sensitivity, list) else data_sensitivity}")
        prompt_lines.append(f"12. runtimePlaceholders: {', '.join(runtime_placeholders) if isinstance(runtime_placeholders, list) else runtime_placeholders}")

        # Add examples if provided
        if request.examples:
            prompt_lines.append("Examples for few-shot learning:")
            for ex in request.examples:
                prompt_lines.append(f"  - {json.dumps(ex)}")

        return "\n".join(prompt_lines)

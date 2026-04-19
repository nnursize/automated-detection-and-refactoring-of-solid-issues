"""Prompt builders for each scan strategy.

All strategies emit the same Finding JSON schema so parsing.py stays unchanged.
The system prompt is common; only the user prompt differs.
"""

from __future__ import annotations

from ..models import ClassInfo
from .templates import PRINCIPLE_DEFINITIONS, build_system_prompt

_JSON_SCHEMA_BLOCK = """## Required JSON Output Format
Respond with ONLY this JSON structure (no other text):
{{
  "findings": [
    {{
      "file_path": "relative/path/to/file",
      "entity_name": "ClassName or ClassName.method_name",
      "entity_type": "class",
      "line_start": 1,
      "line_end": 100,
      "principle": "{principle_abbr}",
      "severity": "high",
      "description": "Brief one-line description of the violation",
      "reasoning": "Detailed explanation of why this violates {principle_abbr}"
    }}
  ]
}}

If no violations are found, return: {{"findings": []}}"""


def _definition_block(principle: str) -> tuple[str, str, str]:
    info = PRINCIPLE_DEFINITIONS[principle]
    return info["name"], info["definition"], info["look_for"]


# ---------- full_repo ----------

_FULL_REPO_TEMPLATE = """Analyze the following {language} source code repository for violations of the {principle_name} ({principle_abbr}).

## Principle Definition
{definition}

## What to Look For
{look_for}

## Instructions
1. Examine each class and module in the code below.
2. Identify specific violations of {principle_abbr}.
3. For each violation, provide the exact file path, class/method name, and line range.
4. Explain WHY it is a violation with concrete reasoning.
5. Rate severity as "high" (clear, significant violation), "medium" (moderate violation), or "low" (minor or borderline).

""" + _JSON_SCHEMA_BLOCK + """

## Source Code
{code_context}"""


def build_full_repo(principle: str, language: str, code_context: str) -> tuple[str, str]:
    name, definition, look_for = _definition_block(principle)
    user = _FULL_REPO_TEMPLATE.format(
        language=language,
        principle_name=name,
        principle_abbr=principle,
        definition=definition,
        look_for=look_for,
        code_context=code_context,
    )
    return build_system_prompt(principle), user


# ---------- smell_two_step (SMELL paper: CoT smells -> SOLID) ----------

_SMELL_TEMPLATE = """Analyze the following {language} source code for violations of the {principle_name} ({principle_abbr}).

Use a TWO-STAGE reasoning process:

## Stage 1 — List design smells (silent, for your own reasoning)
Identify relevant low-level design smells you observe in the code:
- God Class, Feature Envy, Shotgun Surgery, Divergent Change
- Long Method, Large Class, Long Parameter List
- Refused Bequest, Inappropriate Intimacy, Message Chains
- Switch Statements on type, Data Clumps
Think through these internally. Do NOT output them.

## Stage 2 — Map smells to {principle_abbr} violations (this is what you output)
Only surface smells that concretely violate {principle_abbr}. Filter out smells unrelated to this principle.

## Principle Definition
{definition}

## What to Look For
{look_for}

For each {principle_abbr} violation grounded in a smell you saw:
1. Exact file path, class/method name, line range.
2. Name the underlying smell in the reasoning (e.g., "God Class smell -> SRP violation because ...").
3. Severity: "high", "medium", or "low".

""" + _JSON_SCHEMA_BLOCK + """

## Source Code
{code_context}"""


def build_smell_two_step(principle: str, language: str, code_context: str) -> tuple[str, str]:
    name, definition, look_for = _definition_block(principle)
    user = _SMELL_TEMPLATE.format(
        language=language,
        principle_name=name,
        principle_abbr=principle,
        definition=definition,
        look_for=look_for,
        code_context=code_context,
    )
    return build_system_prompt(principle), user


# ---------- class_centric ----------

_CLASS_CENTRIC_TEMPLATE = """Analyze the following {language} classes for violations of the {principle_name} ({principle_abbr}).

For each class you are given:
- Its full source body
- Its base class bodies (where available in the repo)
- The file's imports
- Short headers of sibling classes in the same file

Use the inheritance and import context to reason about dependencies and substitutability.

## Principle Definition
{definition}

## What to Look For
{look_for}

## Instructions
- Report violations for any of the classes shown.
- Use the exact `file_path` shown in each ### CLASS: header.
- Severity: "high", "medium", or "low".

""" + _JSON_SCHEMA_BLOCK + """

## Classes
{code_context}"""


def build_class_centric(
    principle: str,
    language: str,
    code_context: str,
) -> tuple[str, str]:
    name, definition, look_for = _definition_block(principle)
    user = _CLASS_CENTRIC_TEMPLATE.format(
        language=language,
        principle_name=name,
        principle_abbr=principle,
        definition=definition,
        look_for=look_for,
        code_context=code_context,
    )
    return build_system_prompt(principle), user


# ---------- skeleton ----------

_SKELETON_TEMPLATE = """You are shown a SKELETON view of a {language} repository: class headers,
inheritance, method signatures, and attributes — but NO method bodies.

Use this signature-level view to detect structural violations of {principle_name} ({principle_abbr}):
- Fat interfaces / bloated classes (many unrelated method groups)
- Clients forced to implement methods they don't need (abstract methods / NotImplementedError / empty overrides)
- Inheritance hierarchies where subclasses alter the contract shape
- Broad APIs that should be segregated into role-specific interfaces

Cross-reference decorators like `@abstractmethod`, modifiers like `abstract`, and base classes.

## Principle Definition
{definition}

## What to Look For
{look_for}

## Instructions
- Cite the `file_path` and `entity_name` exactly as shown in the skeleton.
- Use the `# L<start>-L<end>` annotations to fill `line_start` / `line_end`.
- Severity: "high", "medium", or "low".

""" + _JSON_SCHEMA_BLOCK + """

## Skeleton
{code_context}"""


def build_skeleton(principle: str, language: str, code_context: str) -> tuple[str, str]:
    name, definition, look_for = _definition_block(principle)
    user = _SKELETON_TEMPLATE.format(
        language=language,
        principle_name=name,
        principle_abbr=principle,
        definition=definition,
        look_for=look_for,
        code_context=code_context,
    )
    return build_system_prompt(principle), user

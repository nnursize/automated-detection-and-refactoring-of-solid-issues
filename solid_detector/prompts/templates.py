"""Prompt templates for SOLID principle violation detection."""

SYSTEM_PROMPT = """You are a senior software architect performing a rigorous code review.
Your task is to identify violations of the {principle_name} ({principle_abbr}) principle from the SOLID design principles.

You must respond ONLY with valid JSON in the exact format specified. Do not include any other text, markdown formatting, or explanation outside the JSON."""

PRINCIPLE_DEFINITIONS = {
    "SRP": {
        "name": "Single Responsibility Principle",
        "definition": (
            "A class should have only one reason to change. It should encapsulate "
            "exactly one responsibility. When a class handles multiple unrelated "
            "concerns (e.g., data processing AND rendering AND persistence), it "
            "violates SRP."
        ),
        "look_for": (
            "- Classes that handle multiple unrelated responsibilities\n"
            "- Methods that mix business logic with I/O, formatting, or persistence\n"
            "- God classes that do too many things\n"
            "- Classes where different groups of methods operate on different subsets of attributes"
        ),
    },
    "OCP": {
        "name": "Open/Closed Principle",
        "definition": (
            "Software entities should be open for extension but closed for modification. "
            "When adding new behavior requires modifying existing code (e.g., adding "
            "elif branches, modifying switch statements), it violates OCP."
        ),
        "look_for": (
            "- Long if/elif/else or switch chains that would need modification to add new types\n"
            "- Functions with type-checking logic (isinstance checks) to handle different cases\n"
            "- Code that requires modifying existing classes to add new features\n"
            "- Missing use of polymorphism, strategy pattern, or plugin architecture"
        ),
    },
    "LSP": {
        "name": "Liskov Substitution Principle",
        "definition": (
            "Subtypes must be substitutable for their base types without altering "
            "the correctness of the program. When a subclass overrides behavior in "
            "a way that breaks the base class contract, it violates LSP."
        ),
        "look_for": (
            "- Subclasses that override methods and change their expected behavior\n"
            "- Subclasses that raise exceptions not raised by the parent\n"
            "- Subclasses that ignore or nullify parent class methods\n"
            "- Type-checking (isinstance) used to handle subclasses differently\n"
            "- Subclasses that violate preconditions or postconditions of parent methods"
        ),
    },
    "ISP": {
        "name": "Interface Segregation Principle",
        "definition": (
            "Clients should not be forced to depend on interfaces they do not use. "
            "When a class implements an interface but leaves some methods empty or "
            "raises NotImplementedError, it violates ISP. Large interfaces that "
            "force implementing classes to provide unneeded methods violate ISP."
        ),
        "look_for": (
            "- Abstract base classes or interfaces with too many methods\n"
            "- Classes that implement an interface but leave methods as pass or raise NotImplementedError\n"
            "- Fat interfaces that could be split into smaller, more focused ones\n"
            "- Classes forced to depend on methods they never call"
        ),
    },
    "DIP": {
        "name": "Dependency Inversion Principle",
        "definition": (
            "High-level modules should not depend on low-level modules; both should "
            "depend on abstractions. Abstractions should not depend on details; "
            "details should depend on abstractions. When a class directly instantiates "
            "its dependencies instead of receiving them through injection, it violates DIP."
        ),
        "look_for": (
            "- Classes that directly instantiate their dependencies (using new/constructor calls)\n"
            "- High-level business logic that imports and depends on low-level implementation details\n"
            "- Missing dependency injection or inversion of control\n"
            "- Hard-coded dependencies that make testing difficult\n"
            "- Tight coupling between modules through concrete class references"
        ),
    },
}

USER_PROMPT_FULL_REPO = """Analyze the following {language} source code repository for violations of the {principle_name} ({principle_abbr}).

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

## Required JSON Output Format
Respond with ONLY this JSON structure (no other text):
{{
  "findings": [
    {{
      "file_path": "relative/path/to/file.py",
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

If no violations are found, return: {{"findings": []}}

## Source Code
{code_context}"""

USER_PROMPT_PER_FILE = """Analyze the following {language} source file for violations of the {principle_name} ({principle_abbr}).

## Principle Definition
{definition}

## What to Look For
{look_for}

## Instructions
1. Examine each class and function in this file.
2. Identify specific violations of {principle_abbr}.
3. For each violation, provide the class/method name and line range.
4. Explain WHY it is a violation with concrete reasoning.
5. Rate severity as "high" (clear, significant violation), "medium" (moderate violation), or "low" (minor or borderline).

## Required JSON Output Format
Respond with ONLY this JSON structure (no other text):
{{
  "findings": [
    {{
      "file_path": "{file_path}",
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

If no violations are found, return: {{"findings": []}}

## File: {file_path}
```
{file_content}
```"""


def build_system_prompt(principle: str) -> str:
    """Build the system prompt for a given SOLID principle."""
    info = PRINCIPLE_DEFINITIONS[principle]
    return SYSTEM_PROMPT.format(
        principle_name=info["name"],
        principle_abbr=principle,
    )


def build_full_repo_prompt(
    principle: str, language: str, code_context: str
) -> str:
    """Build a full-repo user prompt."""
    info = PRINCIPLE_DEFINITIONS[principle]
    return USER_PROMPT_FULL_REPO.format(
        language=language,
        principle_name=info["name"],
        principle_abbr=principle,
        definition=info["definition"],
        look_for=info["look_for"],
        code_context=code_context,
    )


def build_per_file_prompt(
    principle: str, language: str, file_path: str, file_content: str
) -> str:
    """Build a per-file user prompt."""
    info = PRINCIPLE_DEFINITIONS[principle]
    return USER_PROMPT_PER_FILE.format(
        language=language,
        principle_name=info["name"],
        principle_abbr=principle,
        definition=info["definition"],
        look_for=info["look_for"],
        file_path=file_path,
        file_content=file_content,
    )

def get_code_generation_prompt(user_requirement: str) -> str:
    """Prompt for Code Generation Agent"""
    return f"""You are a Senior Python Developer. Generate ONLY the Python code, no explanations.

USER REQUIREMENT: {user_requirement}

Requirements:
- Complete, working Python script
- Proper error handling and logging
- Docstrings and comments
- Main function with if __name__ == "__main__"
- Follow PEP 8 standards

Return ONLY the Python code, nothing else."""

def get_code_refinement_prompt(original_code: str, validation_feedback: str, user_requirement: str) -> str:
    """Prompt for Code Refinement based on validation feedback"""
    return f"""You are a Senior Python Developer. Your goal is to achieve a 9/10 or higher quality score.

ORIGINAL USER REQUIREMENT: {user_requirement}

CURRENT CODE:
{original_code}

VALIDATION FEEDBACK:
{validation_feedback}

MANDATORY IMPROVEMENTS (apply ALL that are missing):
1. Add comprehensive input validation for ALL user inputs
2. Add detailed logging with proper log levels (DEBUG, INFO, WARNING, ERROR)
3. Add type hints to ALL functions and parameters
4. Add detailed docstrings with Args, Returns, Raises sections
5. Implement custom exception classes for specific error types
6. Add configuration constants at the top of the file
7. Implement graceful error recovery, not just error catching
8. Add input sanitization where applicable
9. Ensure all edge cases are handled explicitly
10. Add meaningful inline comments explaining complex logic

You MUST make significant improvements to reach score 9+. Do not return similar code.

Return ONLY the improved Python code, nothing else."""

def get_test_generation_prompt(main_code: str) -> str:
    """Prompt for Test Generation Agent"""
    return f"""You are a QA Testing Specialist. Generate ONLY the test code, no explanations.

MAIN CODE TO TEST:
{main_code}

Requirements:
- Complete pytest test file
- Unit tests for all functions
- Edge cases and error handling tests
- Mock objects where appropriate
- High test coverage

Return ONLY the test code as a complete test_*.py file, nothing else."""

def get_requirements_prompt(main_code: str, test_code: str) -> str:
    """Prompt for Requirements Generation Agent"""
    return f"""You are a DevOps Engineer. Generate ONLY the requirements.txt content, no explanations.

ANALYZE THIS CODE:
Main Code: {main_code}
Test Code: {test_code}

Requirements:
- List all required packages with specific versions
- Include development/testing dependencies
- One package per line

Return ONLY the requirements.txt content, nothing else."""

def get_readme_prompt(main_code: str, test_code: str, requirements: str) -> str:
    """Prompt for README Generation Agent"""
    return f"""You are a Technical Readme Writer. Generate ONLY the README.md content, no explanations and strictly no thinking process.

PROJECT FILES:
Main Code: {main_code}
Test Code: {test_code}
Requirements: {requirements}

Requirements:
- Professional README.md in markdown format
- Project overview and features
- Installation instructions
- Usage examples with code snippets
- Testing instructions

Return ONLY the complete README.md content, nothing else."""

def get_validation_prompt(main_code: str, test_code: str, requirements: str, readme: str) -> str:
    """Prompt for Final Validation Agent"""
    return f"""You are a Senior Software Architect. Provide ONLY the assessment, no extra text.

COMPLETE PROJECT REVIEW:
Main Code: {main_code}
Test Code: {test_code}
Requirements: {requirements}
README: {readme}

Provide structured assessment with:
- Overall Quality Score: X/10
- Code Quality: [assessment]
- Test Coverage: [assessment]  
- Documentation: [assessment]
- Production Readiness: [Ready/Not Ready]
- Top 3 Strengths: [list]
- Top 3 Improvements: [list]

Return ONLY the structured assessment, nothing else."""

def get_validation_prompt_with_feedback(main_code: str, test_code: str, requirements: str, readme: str) -> str:
    """Prompt for Validation Agent that returns actionable feedback for iteration"""
    return f"""You are a Senior Software Architect performing strict code review. Score fairly but provide specific improvements.

COMPLETE PROJECT REVIEW:
Main Code: {main_code}
Test Code: {test_code}
Requirements: {requirements}
README: {readme}

SCORING CRITERIA (be strict):
- 9-10: Production-ready with type hints, logging, custom exceptions, comprehensive error handling, input validation, detailed docstrings
- 7-8: Good code but missing some best practices (e.g., no type hints, basic error handling, minimal logging)
- 5-6: Functional but needs significant improvements
- Below 5: Major issues or incomplete

Provide assessment in this EXACT format:

QUALITY_SCORE: [1-10]
PASSED: [YES only if score >= 9, otherwise NO]

MISSING_FOR_SCORE_9:
- [List SPECIFIC items needed to reach score 9, be very explicit]
- [e.g., "Add type hints to function X", "Add logging in function Y"]
- [e.g., "Create custom exception for Z error case"]

CRITICAL_ISSUES:
- [List critical bugs or security issues, or "None"]

CURRENT_STRENGTHS:
- [List what's already good]

Be SPECIFIC with function names and exact improvements needed.
Return ONLY the structured assessment, nothing else."""
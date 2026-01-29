import streamlit as st
from snowflake_connection import call_cortex_complete
from agent_prompts import *

# Model configuration for each agent type
AGENT_MODELS = {
    'code_generation': 'claude-3-5-sonnet',    
    'test_generation': 'llama4-maverick',  
    'requirements': 'mixtral-8x7b',          
    'documentation': 'llama4-scout',            
    'validation': 'mistral-7b'              
}

class CodeGenerationAgent:
    def __init__(self):
        self.name = "Code Generation Agent"
        self.icon = "💻"
        self.model = AGENT_MODELS['code_generation']
        self.description = "Generates production-ready Python code"
    
    def execute(self, user_requirement: str, show_backend: bool = False):
        st.write(f"{self.icon} **{self.name}** (using {self.model})")
        prompt = get_code_generation_prompt(user_requirement)
        
        with st.spinner(f"{self.name} is working with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name}", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.code(prompt, language="text")
                st.code(result[:200] + "...", language="text")
        
        st.success(f"✅ {self.name} completed")
        return result
    
    def refine(self, original_code: str, feedback: str, user_requirement: str, show_backend: bool = False):
        """Refine code based on validation feedback"""
        st.write(f"{self.icon} **{self.name} - Refinement** (using {self.model})")
        prompt = get_code_refinement_prompt(original_code, feedback, user_requirement)
        
        with st.spinner(f"{self.name} is refining code with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name} - Refinement", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.write("**Feedback received:**")
                st.code(feedback[:300] + "..." if len(feedback) > 300 else feedback, language="text")
                st.code(result[:200] + "...", language="text")
        
        st.success(f"✅ {self.name} refinement completed")
        return result

class TestGenerationAgent:
    def __init__(self):
        self.name = "Test Generation Agent"
        self.icon = "🧪"
        self.model = AGENT_MODELS['test_generation']
        self.description = "Creates comprehensive test suites"
    
    def execute(self, main_code: str, show_backend: bool = False):
        st.write(f"{self.icon} **{self.name}** (using {self.model})")
        prompt = get_test_generation_prompt(main_code)
        
        with st.spinner(f"{self.name} is working with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name}", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.code(prompt, language="text")
                st.code(result[:200] + "...", language="text")
        
        st.success(f"✅ {self.name} completed")
        return result

class RequirementsAgent:
    def __init__(self):
        self.name = "Requirements Agent"
        self.icon = "📦"
        self.model = AGENT_MODELS['requirements']
        self.description = "Analyzes dependencies and creates requirements.txt"
    
    def execute(self, main_code: str, test_code: str, show_backend: bool = False):
        st.write(f"{self.icon} **{self.name}** (using {self.model})")
        prompt = get_requirements_prompt(main_code, test_code)
        
        with st.spinner(f"{self.name} is working with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name}", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.code(prompt, language="text")
                st.code(result[:200] + "...", language="text")
        
        st.success(f"✅ {self.name} completed")
        return result

class DocumentationAgent:
    def __init__(self):
        self.name = "Documentation Agent"
        self.icon = "📚"
        self.model = AGENT_MODELS['documentation']
        self.description = "Writes comprehensive documentation"
    
    def execute(self, main_code: str, test_code: str, requirements: str, show_backend: bool = False):
        st.write(f"{self.icon} **{self.name}** (using {self.model})")
        prompt = get_readme_prompt(main_code, test_code, requirements)
        
        with st.spinner(f"{self.name} is working with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name}", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.code(prompt, language="text")
                st.code(result[:200] + "...", language="text")
        
        st.success(f"✅ {self.name} completed")
        return result

class ValidationAgent:
    def __init__(self):
        self.name = "Validation Agent"
        self.icon = "✅"
        self.model = AGENT_MODELS['validation']
        self.description = "Reviews and validates the complete project"
    
    def execute(self, main_code: str, test_code: str, requirements: str, readme: str, show_backend: bool = False):
        st.write(f"{self.icon} **{self.name}** (using {self.model})")
        prompt = get_validation_prompt(main_code, test_code, requirements, readme)
        
        with st.spinner(f"{self.name} is working with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name}", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.code(prompt, language="text")
                st.code(result[:200] + "...", language="text")
        
        st.success(f"✅ {self.name} completed")
        return result
    
    def execute_with_feedback(self, main_code: str, test_code: str, requirements: str, readme: str, show_backend: bool = False):
        """Execute validation and return structured feedback for iteration"""
        st.write(f"{self.icon} **{self.name}** (using {self.model})")
        prompt = get_validation_prompt_with_feedback(main_code, test_code, requirements, readme)
        
        with st.spinner(f"{self.name} is reviewing with {self.model}..."):
            result = call_cortex_complete(prompt, self.model)
        
        if show_backend:
            with st.expander(f"Backend: {self.name}", expanded=False):
                st.write(f"**Model Used:** `{self.model}`")
                st.code(prompt, language="text")
                st.code(result[:300] + "...", language="text")
        
        # Parse the validation result
        score = self._extract_score(result)
        # Enforce minimum score of 9 to pass (code-level check)
        passed = "PASSED: YES" in result.upper() and score >= 9
        
        if passed:
            st.success(f"✅ {self.name}: PASSED (Score: {score}/10)")
        else:
            st.warning(f"🔄 {self.name}: Needs improvement (Score: {score}/10)")
        
        return {"raw": result, "passed": passed, "score": score}
    
    def _extract_score(self, result: str) -> int:
        """Extract quality score from validation result"""
        try:
            for line in result.split('\n'):
                if 'QUALITY_SCORE' in line.upper():
                    score = ''.join(filter(str.isdigit, line))
                    return int(score) if score else 5
        except:
            pass
        return 5

def get_agent_model(agent_type: str) -> str:
    """Get the recommended model for an agent type"""
    return AGENT_MODELS.get(agent_type, 'claude-3-5-sonnet')
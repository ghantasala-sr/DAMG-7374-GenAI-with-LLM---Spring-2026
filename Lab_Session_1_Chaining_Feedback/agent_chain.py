import streamlit as st
from agents import *

class AgentChain:
    def __init__(self):
        self.agents = {
            'code': CodeGenerationAgent(),
            'test': TestGenerationAgent(),
            'requirements': RequirementsAgent(),
            'docs': DocumentationAgent(),
            'validation': ValidationAgent()
        }
    
    def execute_chain(self, user_requirement: str, show_backend: bool = False):
        """Execute the complete agent chain (Prompt Chaining - no feedback loop)"""
        
        st.subheader("🔗 Prompt Chaining Execution")
        st.info("Mode: Linear execution - each agent runs once in sequence")
        progress_bar = st.progress(0)
        
        results = {}
        
        # Step 1: Code Generation
        progress_bar.progress(0.2)
        results['code'] = self.agents['code'].execute(user_requirement, show_backend)
        
        # Step 2: Test Generation
        progress_bar.progress(0.4)
        results['test'] = self.agents['test'].execute(results['code'], show_backend)
        
        # Step 3: Requirements
        progress_bar.progress(0.6)
        results['requirements'] = self.agents['requirements'].execute(
            results['code'], results['test'], show_backend
        )
        
        # Step 4: Documentation
        progress_bar.progress(0.8)
        results['docs'] = self.agents['docs'].execute(
            results['code'], results['test'], results['requirements'], show_backend
        )
        
        # Step 5: Validation
        progress_bar.progress(1.0)
        results['validation'] = self.agents['validation'].execute(
            results['code'], results['test'], results['requirements'], results['docs'], show_backend
        )
        
        st.success("🎉 Prompt chain completed!")
        return results
    
    def execute_feedback_loop(self, user_requirement: str, max_iterations: int = 3, show_backend: bool = False):
        """Execute agent chain with feedback loop for iterative improvement"""
        
        st.subheader("🔄 Feedback Loop Execution")
        st.info(f"Mode: Iterative improvement - up to {max_iterations} refinement cycles")
        
        results = {}
        iteration = 1
        
        # Initial code generation
        st.markdown(f"### Iteration {iteration}")
        iteration_container = st.container()
        
        with iteration_container:
            progress_bar = st.progress(0)
            
            # Step 1: Code Generation
            progress_bar.progress(0.2)
            results['code'] = self.agents['code'].execute(user_requirement, show_backend)
            current_code = results['code']
            
            # Step 2: Test Generation
            progress_bar.progress(0.4)
            results['test'] = self.agents['test'].execute(current_code, show_backend)
            
            # Step 3: Requirements
            progress_bar.progress(0.6)
            results['requirements'] = self.agents['requirements'].execute(
                current_code, results['test'], show_backend
            )
            
            # Step 4: Documentation
            progress_bar.progress(0.8)
            results['docs'] = self.agents['docs'].execute(
                current_code, results['test'], results['requirements'], show_backend
            )
            
            # Step 5: Validation with feedback
            progress_bar.progress(1.0)
            validation_result = self.agents['validation'].execute_with_feedback(
                current_code, results['test'], results['requirements'], results['docs'], show_backend
            )
        
        # Store iteration history
        results['iterations'] = [{
            'iteration': 1,
            'code': current_code,
            'validation': validation_result
        }]
        
        # Feedback loop - iterate if not passed
        while not validation_result['passed'] and iteration < max_iterations:
            iteration += 1
            st.markdown(f"### Iteration {iteration}")
            st.write(f"🔄 Refining based on feedback (Score: {validation_result['score']}/10)")
            
            iteration_container = st.container()
            
            with iteration_container:
                progress_bar = st.progress(0)
                
                # Refine code based on feedback
                progress_bar.progress(0.2)
                feedback = validation_result['raw']
                current_code = self.agents['code'].refine(
                    current_code, feedback, user_requirement, show_backend
                )
                results['code'] = current_code
                
                # Regenerate tests for refined code
                progress_bar.progress(0.4)
                results['test'] = self.agents['test'].execute(current_code, show_backend)
                
                # Regenerate requirements
                progress_bar.progress(0.6)
                results['requirements'] = self.agents['requirements'].execute(
                    current_code, results['test'], show_backend
                )
                
                # Regenerate documentation
                progress_bar.progress(0.8)
                results['docs'] = self.agents['docs'].execute(
                    current_code, results['test'], results['requirements'], show_backend
                )
                
                # Validate again
                progress_bar.progress(1.0)
                validation_result = self.agents['validation'].execute_with_feedback(
                    current_code, results['test'], results['requirements'], results['docs'], show_backend
                )
                
                # Store iteration
                results['iterations'].append({
                    'iteration': iteration,
                    'code': current_code,
                    'validation': validation_result
                })
        
        # Final validation result (standard format for display)
        results['validation'] = validation_result['raw']
        
        # Summary
        st.markdown("---")
        if validation_result['passed']:
            st.success(f"🎉 Feedback loop completed! Passed after {iteration} iteration(s)")
        else:
            st.warning(f"⚠️ Max iterations ({max_iterations}) reached. Final score: {validation_result['score']}/10")
        
        # Show iteration summary
        with st.expander("📊 Iteration Summary", expanded=True):
            cols = st.columns(len(results['iterations']))
            for i, iter_data in enumerate(results['iterations']):
                with cols[i]:
                    score = iter_data['validation']['score']
                    passed = iter_data['validation']['passed']
                    status = "✅ Passed" if passed else "🔄 Needs work"
                    st.metric(f"Iteration {iter_data['iteration']}", f"{score}/10", status)
        
        return results
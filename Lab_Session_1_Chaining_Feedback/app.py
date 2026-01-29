import streamlit as st
import os
from agent_chain import AgentChain
from snowflake_connection import get_snowflake_connection

# Page config
st.set_page_config(
    page_title="Code Generation Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = {}

def main():
    st.title("🤖 Code Generation Agent")
    st.subheader("Prompt Chaining & Feedback Loop with Snowflake Cortex")
    
    # Check .env file
    if not os.path.exists('.env'):
        st.error("❌ Create .env file with Snowflake credentials")
        st.code("""
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
        """)
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        show_backend = st.toggle("Show Backend Process", True)
        
        st.markdown("---")
        
        # Execution Mode Selection
        st.header("🎯 Execution Mode")
        execution_mode = st.radio(
            "Select pattern:",
            ["Prompt Chaining", "Feedback Loop"],
            help="Choose the agent orchestration pattern"
        )
        
        # Mode-specific settings
        if execution_mode == "Feedback Loop":
            max_iterations = st.slider("Max Iterations", 1, 5, 3, 
                help="Maximum refinement cycles before stopping")
            st.caption("⚠️ More iterations = longer execution time")
        
        st.markdown("---")
        
        # Mode explanation
        st.header("📖 Pattern Info")
        if execution_mode == "Prompt Chaining":
            st.markdown("""
            **Prompt Chaining**
            
            Linear sequential execution:
            1. 💻 Code Generation
            2. 🧪 Test Generation
            3. 📦 Requirements
            4. 📚 Documentation
            5. ✅ Validation
            
            Each agent runs **once** and passes output to the next.
            """)
        else:
            st.markdown("""
            **Feedback Loop**
            
            Iterative improvement cycle:
            1. Generate initial code
            2. Run full validation
            3. If not passed → refine code
            4. Repeat until passed or max iterations
            
            Agents **collaborate** to improve quality.
            """)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Results"):
            st.session_state.results = {}
            st.rerun()

    # Verify Snowflake connection
    with st.spinner("Verifying Snowflake connection..."):
        try:
            conn = get_snowflake_connection()
            if not conn:
                st.error("❌ Unable to establish Snowflake connection. Check your .env and credentials.")
            else:
                cur = conn.cursor()
                cur.execute("SELECT CURRENT_TIMESTAMP()")
                row = cur.fetchone()
                server_time = row[0] if row else "unknown"
                st.success(f"✅ Snowflake connection established — server time: {server_time}")
                cur.close()
                conn.close()
        except Exception as e:
            st.error(f"❌ Connection verification failed: {e}")
    
    # Main interface
    st.header("💬 Chat Interface")
    
    # Show current mode
    mode_emoji = "🔗" if execution_mode == "Prompt Chaining" else "🔄"
    st.caption(f"Current mode: {mode_emoji} **{execution_mode}**")
    
    # Example prompts
    examples = [
        "Create a personal expense tracker with category analysis",
        "Build a password generator with customizable security levels", 
        "Create a JSON to CSV converter with validation",
        "Build a simple chat bot for customer support",
        "Create a file organizer that sorts by date and type",
        "Build a URL shortener with analytics tracking",
        "Create a markdown to HTML converter",
        "Build a weather data aggregator from multiple APIs"
    ]
    
    selected_example = st.selectbox("Example prompts:", [""] + examples)
    
    # Chat input
    user_input = st.chat_input("What do you want to build?")
    
    if selected_example and selected_example != "":
        user_input = selected_example
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Display agent response
        with st.chat_message("assistant"):
            st.write(f"🚀 Starting {execution_mode.lower()}...")
            
            # Execute based on mode
            chain = AgentChain()
            
            if execution_mode == "Prompt Chaining":
                results = chain.execute_chain(user_input, show_backend)
            else:
                results = chain.execute_feedback_loop(user_input, max_iterations, show_backend)
            
            # Store results
            st.session_state.results = results
            st.session_state.execution_mode = execution_mode
    
    # Display results
    if st.session_state.results:
        st.markdown("---")
        st.header("📁 Generated Files")
        
        # Show mode used
        mode_used = st.session_state.get('execution_mode', 'Prompt Chaining')
        st.caption(f"Generated using: **{mode_used}**")
        
        # Tabs for results
        if mode_used == "Feedback Loop" and 'iterations' in st.session_state.results:
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "💻 Code", "🧪 Tests", "📦 Requirements", "📚 README", "✅ Review", "📈 Iterations"
            ])
        else:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "💻 Code", "🧪 Tests", "📦 Requirements", "📚 README", "✅ Review"
            ])
        
        with tab1:
            if 'code' in st.session_state.results:
                st.code(st.session_state.results['code'], language="python")
        
        with tab2:
            if 'test' in st.session_state.results:
                st.code(st.session_state.results['test'], language="python")
        
        with tab3:
            if 'requirements' in st.session_state.results:
                st.code(st.session_state.results['requirements'])
        
        with tab4:
            if 'docs' in st.session_state.results:
                st.markdown(st.session_state.results['docs'])
        
        with tab5:
            if 'validation' in st.session_state.results:
                st.write(st.session_state.results['validation'])
        
        # Iterations tab (only for feedback loop)
        if mode_used == "Feedback Loop" and 'iterations' in st.session_state.results:
            with tab6:
                st.subheader("📈 Iteration History")
                for iter_data in st.session_state.results['iterations']:
                    with st.expander(f"Iteration {iter_data['iteration']} - Score: {iter_data['validation']['score']}/10"):
                        st.write("**Validation Feedback:**")
                        st.text(iter_data['validation']['raw'])
                        st.write("**Code at this iteration:**")
                        st.code(iter_data['code'][:500] + "..." if len(iter_data['code']) > 500 else iter_data['code'], language="python")

if __name__ == "__main__":
    main()
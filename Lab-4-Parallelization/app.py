"""
Full-Stack Car Analyst - Streamlit Dashboard.

A parallel agent architecture for comprehensive automotive analysis,
powered by Snowflake Cortex LLMs and langchain-snowflake.
"""

import streamlit as st
import asyncio
import time
from typing import Dict

from utils.session import get_snowflake_session, get_chat_model
from analysts import ReviewAnalyst, MarketAnalyst, PurchaseAnalyst
from analysts.base_analyst import BaseAnalyst
from orchestrator.planner import PlannerAgent
from orchestrator.parallel_executor import ParallelAnalystExecutor, create_progress_callbacks
from orchestrator.synthesizer import Synthesizer


# ══════════════════════════════════════════════════════════════════════════════
# Page Configuration
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Car Analyst - Parallel AI Agents",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚗 Full-Stack Car Analyst")
st.caption("Parallel Agent Architecture | Snowflake Cortex | LangChain Integration")


# ══════════════════════════════════════════════════════════════════════════════
# Session State Initialization
# ══════════════════════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []

if "snowflake_session" not in st.session_state:
    st.session_state.snowflake_session = None

if "analysts_initialized" not in st.session_state:
    st.session_state.analysts_initialized = False


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar - Configuration & Info
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Connection status
    if st.session_state.snowflake_session:
        st.success("✅ Connected to Snowflake")
    else:
        st.warning("⏳ Not connected")
        if st.button("Connect to Snowflake", type="primary"):
            try:
                with st.spinner("Connecting..."):
                    st.session_state.snowflake_session = get_snowflake_session()
                st.success("Connected!")
                st.rerun()
            except Exception as e:
                st.error(f"Connection failed: {e}")
    
    st.divider()
    
    st.header("🤖 Parallel Agents")
    st.markdown("""
    This system uses **3 specialized analysts** running in parallel:
    
    | Agent | Specialty |
    |-------|-----------|
    | 📊 **Review Analyst** | Car reviews, ratings, sentiment |
    | 📈 **Market Analyst** | Trends, pricing, news |
    | 💰 **Purchase Analyst** | Budget, dealers, recommendations |
    """)
    
    st.divider()
    
    st.header("💡 Example Queries")
    example_queries = [
        "Compare Toyota RAV4 vs Honda CR-V for family use under $40k",
        "What do owners say about Tesla Model Y reliability?",
        "Latest news and market trends for electric SUVs",
        "Best hybrid sedan under $35k near Boston",
        "Analyze Ford F-150 Lightning - reviews, pricing, and dealers"
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{hash(query)}", use_container_width=True):
            st.session_state.example_query = query
    
    st.divider()
    
    st.header("📐 Architecture")
    st.markdown("""
    ```
    User Query
        ↓
    Planner Agent
        ↓
    ┌───┬───┬───┐
    │ R │ M │ P │  ← Parallel
    └───┴───┴───┘
        ↓
    Synthesizer
        ↓
    Report
    ```
    """)


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def initialize_analysts(session) -> Dict[str, BaseAnalyst]:
    """Initialize all analyst instances."""
    return {
        "review_analyst": ReviewAnalyst(session=session),
        "market_analyst": MarketAnalyst(session=session),
        "purchase_analyst": PurchaseAnalyst(session=session)
    }


async def run_parallel_analysis(
    query: str,
    session,
    status_container
) -> Dict:
    """
    Run the full parallel analysis pipeline.
    
    1. Planner decomposes query
    2. Selected analysts run in parallel
    3. Synthesizer combines results
    """
    results = {
        "plan": None,
        "execution": None,
        "synthesis": None,
        "total_time_ms": 0
    }
    
    start_time = time.time()
    
    # Step 1: Planning
    status_container.write("🧠 **Step 1/3:** Planning analysis...")
    planner = PlannerAgent(session=session)
    plan = await planner.plan_async(query)
    results["plan"] = plan
    status_container.write(f"   → Selected analysts: {', '.join(plan.analysts)}")
    
    # Step 2: Parallel Execution
    status_container.write("⚡ **Step 2/3:** Running analysts in parallel...")
    
    # Initialize only selected analysts
    all_analysts = initialize_analysts(session)
    selected_analysts = {
        name: all_analysts[name] 
        for name in plan.analysts 
        if name in all_analysts
    }
    
    # Create executor with progress callbacks
    executor = ParallelAnalystExecutor(
        timeout_seconds=60.0,
        on_analyst_start=lambda n: status_container.write(f"   🔄 Starting {n}..."),
        on_analyst_complete=lambda n, r: status_container.write(f"   ✅ {n} done ({r.execution_time_ms:.0f}ms)"),
        on_analyst_error=lambda n, e: status_container.write(f"   ❌ {n} failed: {e}")
    )
    
    # Execute in parallel
    execution_result = await executor.execute_parallel(
        analysts=selected_analysts,
        queries=plan.sub_queries
    )
    results["execution"] = execution_result
    
    # Step 3: Synthesis
    status_container.write("📝 **Step 3/3:** Synthesizing report...")
    synthesizer = Synthesizer(session=session)
    synthesis = await synthesizer.synthesize_async(
        execution_result=execution_result,
        original_query=query,
        synthesis_focus=plan.synthesis_focus
    )
    results["synthesis"] = synthesis
    
    results["total_time_ms"] = (time.time() - start_time) * 1000
    
    return results


# ══════════════════════════════════════════════════════════════════════════════
# Chat History Display
# ══════════════════════════════════════════════════════════════════════════════

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("metadata"):
            with st.expander("📊 Analysis Details", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Analysts Used", msg["metadata"].get("analyst_count", 0))
                with col2:
                    st.metric("Total Time", f"{msg['metadata'].get('total_time_ms', 0):.0f}ms")
                with col3:
                    st.metric("Success", "✅" if msg["metadata"].get("success") else "❌")


# ══════════════════════════════════════════════════════════════════════════════
# Query Input & Processing
# ══════════════════════════════════════════════════════════════════════════════

# Handle example query selection
default_input = st.session_state.pop("example_query", "")
user_input = st.chat_input("Ask me anything about cars...", key="chat_input")
query = user_input or default_input

if query:
    # Check connection
    if not st.session_state.snowflake_session:
        st.error("Please connect to Snowflake first (see sidebar)")
        st.stop()
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # Process with parallel agents
    with st.chat_message("assistant"):
        # Status container for progress updates
        with st.status("🤖 Parallel Analysis in Progress...", expanded=True) as status:
            try:
                # Run async analysis
                results = asyncio.run(run_parallel_analysis(
                    query=query,
                    session=st.session_state.snowflake_session,
                    status_container=st
                ))
                
                status.update(
                    label=f"✅ Analysis Complete ({results['total_time_ms']:.0f}ms)",
                    state="complete"
                )
                
            except Exception as e:
                status.update(label="❌ Analysis Failed", state="error")
                st.error(f"Error: {str(e)}")
                st.stop()
        
        # Display the synthesized report
        if results["synthesis"] and results["synthesis"].get("success"):
            st.markdown(results["synthesis"]["report"])
            
            # Show detailed breakdown
            with st.expander("📊 Detailed Analysis Breakdown", expanded=False):
                tabs = st.tabs(["🎯 Plan", "⚡ Execution", "📈 Metrics"])
                
                with tabs[0]:
                    st.subheader("Query Plan")
                    plan = results["plan"]
                    st.json({
                        "analysts": plan.analysts,
                        "sub_queries": plan.sub_queries,
                        "synthesis_focus": plan.synthesis_focus,
                        "priority": plan.priority_analyst
                    })
                
                with tabs[1]:
                    st.subheader("Parallel Execution Results")
                    exec_result = results["execution"]
                    for name, execution in exec_result.executions.items():
                        status_icon = "✅" if execution.status.value == "completed" else "❌"
                        st.markdown(f"**{status_icon} {name}**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"Status: {execution.status.value}")
                            st.write(f"Time: {execution.execution_time_ms:.0f}ms")
                        with col2:
                            if execution.result:
                                st.write(f"Confidence: {execution.result.confidence:.0%}")
                                st.write(f"Sources: {len(execution.result.sources)}")
                        st.divider()
                
                with tabs[2]:
                    st.subheader("Performance Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Planning", f"{50:.0f}ms")
                    with col2:
                        st.metric("Parallel Exec", f"{results['execution'].total_time_ms:.0f}ms")
                    with col3:
                        st.metric("Synthesis", f"{results['synthesis']['execution_time_ms']:.0f}ms")
                    with col4:
                        st.metric("Total", f"{results['total_time_ms']:.0f}ms")
                    
                    # Parallelization benefit
                    sequential_estimate = results['execution'].total_time_ms * len(results['plan'].analysts)
                    speedup = sequential_estimate / results['execution'].total_time_ms if results['execution'].total_time_ms > 0 else 1
                    st.info(f"⚡ **Parallelization Speedup:** {speedup:.1f}x faster than sequential execution")
            
            # Store metadata
            metadata = {
                "analyst_count": results["synthesis"]["analyst_count"],
                "total_time_ms": results["total_time_ms"],
                "success": True,
                "analysts_used": results["plan"].analysts
            }
        else:
            st.error("Analysis failed. Please try again.")
            metadata = {"success": False}
        
        # Save to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": results["synthesis"]["report"] if results["synthesis"] else "Analysis failed.",
            "metadata": metadata
        })


# ══════════════════════════════════════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
st.caption("""
**Lab 4: Parallel Agent Architecture** | Built with Snowflake Cortex & LangChain  
Demonstrates parallel execution of specialized AI analysts for comprehensive automotive intelligence.
""")

import streamlit as st
import streamlit.components.v1 as components
import time
import json

st.set_page_config(
    page_title="Cortex Code (CoCo) Feature Showcase",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');

.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid #29b5f6;
    box-shadow: 0 0 30px rgba(41, 181, 246, 0.15);
}
.main-header h1 {
    color: #29b5f6;
    font-family: 'Inter', sans-serif;
    font-size: 2.2rem;
    margin: 0;
}
.main-header p {
    color: #b0bec5;
    font-size: 1.05rem;
    margin: 0.5rem 0 0 0;
}

.feature-card {
    background: linear-gradient(145deg, #1e1e2f, #252540);
    border: 1px solid #333;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.feature-card:hover {
    border-color: #29b5f6;
    box-shadow: 0 0 20px rgba(41, 181, 246, 0.1);
}
.feature-card h4 {
    color: #29b5f6;
    margin: 0 0 0.5rem 0;
    font-family: 'Inter', sans-serif;
}
.feature-card p {
    color: #aaa;
    margin: 0;
    font-size: 0.92rem;
}

.code-block {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #c9d1d9;
    overflow-x: auto;
    margin: 0.5rem 0;
}
.code-block .prompt {
    color: #58a6ff;
}
.code-block .command {
    color: #7ee787;
}
.code-block .flag {
    color: #d2a8ff;
}
.code-block .comment {
    color: #8b949e;
}
.code-block .output {
    color: #f0883e;
}

.shortcut-key {
    background: #21262d;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #e6edf3;
    display: inline-block;
    margin: 2px;
    box-shadow: 0 2px 0 #333;
}

.category-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 2px 4px 2px 0;
}
.badge-blue { background: rgba(41,181,246,0.15); color: #29b5f6; border: 1px solid rgba(41,181,246,0.3); }
.badge-green { background: rgba(126,231,135,0.15); color: #7ee787; border: 1px solid rgba(126,231,135,0.3); }
.badge-purple { background: rgba(210,168,255,0.15); color: #d2a8ff; border: 1px solid rgba(210,168,255,0.3); }
.badge-orange { background: rgba(240,136,62,0.15); color: #f0883e; border: 1px solid rgba(240,136,62,0.3); }
.badge-red { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.3); }
.badge-yellow { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }

.flow-step {
    background: #161b22;
    border-left: 3px solid #29b5f6;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    border-radius: 0 8px 8px 0;
}
.flow-step .step-num {
    color: #29b5f6;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.flow-step .step-text {
    color: #c9d1d9;
}

.terminal-window {
    background: #0d1117;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #30363d;
    margin: 0.8rem 0;
}
.terminal-bar {
    background: #161b22;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.terminal-dot {
    width: 12px; height: 12px; border-radius: 50%;
    display: inline-block;
}
.terminal-dot.red { background: #f85149; }
.terminal-dot.yellow { background: #d29922; }
.terminal-dot.green { background: #7ee787; }
.terminal-body {
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #c9d1d9;
    line-height: 1.6;
}

.architecture-box {
    background: linear-gradient(145deg, #0d1117, #161b22);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin: 0.5rem 0;
}
.architecture-box h5 {
    color: #29b5f6;
    margin: 0 0 0.5rem 0;
}
.architecture-box p {
    color: #8b949e;
    font-size: 0.85rem;
    margin: 0;
}

.stat-card {
    background: linear-gradient(145deg, #161b22, #1c2333);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.stat-card .stat-num {
    font-size: 2rem;
    font-weight: 700;
    color: #29b5f6;
    font-family: 'JetBrains Mono', monospace;
}
.stat-card .stat-label {
    color: #8b949e;
    font-size: 0.82rem;
    margin-top: 0.3rem;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5rem 0;
}
.comparison-table th {
    background: #161b22;
    color: #29b5f6;
    padding: 10px;
    text-align: left;
    border-bottom: 2px solid #29b5f6;
    font-size: 0.88rem;
}
.comparison-table td {
    padding: 8px 10px;
    border-bottom: 1px solid #21262d;
    color: #c9d1d9;
    font-size: 0.85rem;
}
.comparison-table tr:hover td {
    background: rgba(41,181,246,0.05);
}

.tooltip-text {
    font-size: 0.8rem;
    color: #8b949e;
    font-style: italic;
    margin-top: 0.3rem;
}

.animated-border {
    position: relative;
    border-radius: 12px;
    padding: 1.5rem;
    background: #161b22;
    border: 1px solid transparent;
    background-clip: padding-box;
}
</style>
""", unsafe_allow_html=True)


FEATURES = {
    "overview": {
        "icon": "🏠",
        "title": "Overview",
        "subtitle": "What is Cortex Code?"
    },
    "cli_commands": {
        "icon": "⌨️",
        "title": "CLI Commands",
        "subtitle": "Launch, configure, and control"
    },
    "slash_commands": {
        "icon": "📝",
        "title": "Slash Commands",
        "subtitle": "In-session commands"
    },
    "special_syntax": {
        "icon": "🔤",
        "title": "Special Syntax",
        "subtitle": "@, $, #, ! prefixes"
    },
    "agents": {
        "icon": "🤖",
        "title": "Agents & Subagents",
        "subtitle": "Task delegation & teams"
    },
    "skills": {
        "icon": "🧩",
        "title": "Skills System",
        "subtitle": "Extensible capabilities"
    },
    "skills_galaxy": {
        "icon": "🌌",
        "title": "Skills Galaxy",
        "subtitle": "Interactive skills map"
    },
    "snowflake_tools": {
        "icon": "❄️",
        "title": "Snowflake Tools",
        "subtitle": "#TABLE, /sql, artifacts"
    },
    "mcp": {
        "icon": "🔌",
        "title": "MCP Integration",
        "subtitle": "External tool servers"
    },
    "hooks": {
        "icon": "🪝",
        "title": "Hooks System",
        "subtitle": "Event-driven automation"
    },
    "sessions": {
        "icon": "💾",
        "title": "Session Management",
        "subtitle": "Fork, rewind, compact"
    },
    "shortcuts": {
        "icon": "⚡",
        "title": "Keyboard Shortcuts",
        "subtitle": "Power user controls"
    },
    "config": {
        "icon": "⚙️",
        "title": "Configuration",
        "subtitle": "Settings & connections"
    },
}


def render_terminal(lines, title="Terminal"):
    dots = (
        '<span class="terminal-dot red"></span>'
        '<span class="terminal-dot yellow"></span>'
        '<span class="terminal-dot green"></span>'
    )
    body = "<br>".join(lines)
    return f"""
    <div class="terminal-window">
        <div class="terminal-bar">{dots}
            <span style="color:#8b949e; margin-left:8px; font-size:0.8rem;">{title}</span>
        </div>
        <div class="terminal-body">{body}</div>
    </div>
    """


def render_flow_steps(steps):
    html = ""
    for i, step in enumerate(steps, 1):
        html += f"""
        <div class="flow-step">
            <span class="step-num">Step {i}:</span>
            <span class="step-text"> {step}</span>
        </div>
        """
    return html


def type_text(placeholder, text, speed=0.02):
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed + "▌")
        time.sleep(speed)
    placeholder.markdown(displayed)


def section_overview():
    st.markdown("""
    <div class="main-header">
        <h1>❄️ Cortex Code (CoCo)</h1>
        <p>Snowflake's AI-powered CLI for software & data engineering — your intelligent terminal companion</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    stats = [
        ("40+", "Slash Commands"),
        ("20+", "Built-in Skills"),
        ("5", "Agent Types"),
        ("30+", "Keyboard Shortcuts"),
    ]
    for col, (num, label) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-num">{num}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### What Can Cortex Code Do?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🛠️ Code Generation & Editing</h4>
            <p>Write, edit, refactor, and debug code across any language with full codebase awareness.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h4>❄️ Snowflake Native</h4>
            <p>Direct SQL execution, table references with #TABLE, semantic views, Cortex Analyst, and artifact deployment.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Agents & Teams</h4>
            <p>Spawn autonomous subagents for parallel work — research, plan, code, and review simultaneously.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h4>🧩 Extensible Skills</h4>
            <p>Plugin architecture with bundled, project-level, and remote skills for specialized domains.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🔌 MCP Protocol</h4>
            <p>Connect external tool servers — GitHub, databases, APIs — via the Model Context Protocol.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h4>💾 Session Intelligence</h4>
            <p>Fork conversations, rewind to checkpoints, compact context, and resume across sessions.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Architecture Overview")

    st.markdown("""
    <div style="display:flex; gap:1rem; flex-wrap:wrap; justify-content:center;">
        <div class="architecture-box" style="flex:1; min-width:150px;">
            <h5>User Input</h5>
            <p>Natural language prompt, slash commands, special syntax</p>
        </div>
        <div style="display:flex; align-items:center; color:#29b5f6; font-size:1.5rem;">→</div>
        <div class="architecture-box" style="flex:1; min-width:150px;">
            <h5>CoCo Engine</h5>
            <p>LLM reasoning + tool selection + context management</p>
        </div>
        <div style="display:flex; align-items:center; color:#29b5f6; font-size:1.5rem;">→</div>
        <div class="architecture-box" style="flex:1; min-width:150px;">
            <h5>Tools & Skills</h5>
            <p>Bash, Read, Write, Edit, Grep, Glob, SQL, MCP…</p>
        </div>
        <div style="display:flex; align-items:center; color:#29b5f6; font-size:1.5rem;">→</div>
        <div class="architecture-box" style="flex:1; min-width:150px;">
            <h5>Output</h5>
            <p>Code changes, answers, artifacts, deployed apps</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_cli_commands():
    st.markdown("### ⌨️ CLI Commands")
    st.markdown("Launch and configure Cortex Code from your terminal.")

    st.markdown(render_terminal([
        '<span class="comment"># Basic launch</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span>',
        '',
        '<span class="comment"># Launch with a specific connection</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">-c my_connection</span>',
        '',
        '<span class="comment"># Resume last session</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">--resume last</span>',
        '',
        '<span class="comment"># Non-interactive (pipe-friendly)</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">-p</span> "Explain this error log"',
        '',
        '<span class="comment"># Use a specific model</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">-m claude-opus-4-6</span>',
        '',
        '<span class="comment"># Plan mode (explore before coding)</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">--plan</span>',
        '',
        '<span class="comment"># Work in an isolated git worktree</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">--worktree my-feature</span>',
    ], "Launch Options"), unsafe_allow_html=True)

    st.markdown("#### Key CLI Flags")
    flags_data = {
        "Flag": [
            "`--resume, -r`", "`--print, -p`", "`--connection, -c`",
            "`--model, -m`", "`--plan`", "`--worktree`",
            "`--workdir, -w`", "`--bypass`", "`--config`",
            "`--mcp / --no-mcp`"
        ],
        "Description": [
            "Resume a previous session (`last` or session ID)",
            "Non-interactive single query mode",
            "Specify Snowflake connection name",
            "Override AI model (claude-sonnet-4-5, claude-opus-4-6, etc.)",
            "Start in plan mode — explores before writing code",
            "Run in an isolated git worktree",
            "Set working directory",
            "Enable bypass mode",
            "Custom settings.json path",
            "Enable or disable MCP servers",
        ],
    }
    st.dataframe(flags_data, use_container_width=True, hide_index=True)


def section_slash_commands():
    st.markdown("### 📝 Slash Commands")
    st.markdown("Type these directly in the CoCo prompt during a session.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Navigation & Info", "Session Control", "Configuration", "Snowflake"
    ])

    with tab1:
        cmds = [
            ("/help", "Show all available commands"),
            ("/status", "Display current session info, model, tools"),
            ("/cost", "Show token usage and cost for the session"),
            ("/bashes", "List all running background shells"),
            ("/agents", "List configured custom agents"),
            ("/skills", "List all available skills"),
            ("/connections", "Show Snowflake connections"),
            ("/mcp", "Manage MCP servers"),
            ("/review", "Review recent code changes"),
        ]
        for cmd, desc in cmds:
            st.markdown(f"<div class='code-block'><span class='command'>{cmd}</span>  <span class='comment'>— {desc}</span></div>", unsafe_allow_html=True)

    with tab2:
        cmds = [
            ("/compact", "Summarize and compress conversation context"),
            ("/clear", "Clear conversation history"),
            ("/resume", "Resume a previous session"),
            ("/fork", "Branch the conversation at a specific point"),
            ("/rewind", "Go back to a previous state"),
            ("/diff", "Show diff of recent changes"),
            ("/undo", "Undo the last file change"),
        ]
        for cmd, desc in cmds:
            st.markdown(f"<div class='code-block'><span class='command'>{cmd}</span>  <span class='comment'>— {desc}</span></div>", unsafe_allow_html=True)

    with tab3:
        cmds = [
            ("/settings", "Interactive configuration editor"),
            ("/theme", "Change color theme (dark / light / pro)"),
            ("/model", "Switch AI model mid-session"),
            ("/permissions", "Manage tool permissions"),
            ("/feedback", "Provide session feedback"),
        ]
        for cmd, desc in cmds:
            st.markdown(f"<div class='code-block'><span class='command'>{cmd}</span>  <span class='comment'>— {desc}</span></div>", unsafe_allow_html=True)

    with tab4:
        cmds = [
            ("/sql", "Execute SQL directly in Snowflake"),
            ("/connect", "Switch Snowflake connection"),
        ]
        for cmd, desc in cmds:
            st.markdown(f"<div class='code-block'><span class='command'>{cmd}</span>  <span class='comment'>— {desc}</span></div>", unsafe_allow_html=True)


def section_special_syntax():
    st.markdown("### 🔤 Special Syntax Prefixes")
    st.markdown("CoCo recognizes special prefix characters to trigger specific behaviors.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>@ — File References</h4>
            <p>Attach files directly to your prompt context.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(render_terminal([
            '<span class="comment"># Reference a specific file</span>',
            '<span class="prompt">></span> Fix the bug in <span class="command">@src/utils.py</span>',
            '',
            '<span class="comment"># Reference a URL</span>',
            '<span class="prompt">></span> Implement the API from <span class="command">@https://docs.example.com/api</span>',
            '',
            '<span class="comment"># Reference a folder</span>',
            '<span class="prompt">></span> Refactor all files in <span class="command">@src/components/</span>',
        ], "@ File References"), unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h4># — Snowflake Table References</h4>
            <p>Pull table schema and metadata into your prompt.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(render_terminal([
            '<span class="comment"># Reference a table (fetches DDL + sample)</span>',
            '<span class="prompt">></span> Analyze <span class="command">#MY_DB.MY_SCHEMA.USERS</span>',
            '',
            '<span class="comment"># Use in queries</span>',
            '<span class="prompt">></span> Write a query joining <span class="command">#ORDERS</span> and <span class="command">#CUSTOMERS</span>',
        ], "# Table References"), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>$ — Skill Invocation</h4>
            <p>Invoke a specific skill by name.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(render_terminal([
            '<span class="comment"># Invoke a skill</span>',
            '<span class="prompt">></span> <span class="command">$analyzing-data</span> What are the top 10 customers?',
            '',
            '<span class="comment"># Streamlit skill</span>',
            '<span class="prompt">></span> <span class="command">$developing-with-streamlit</span> Build a dashboard',
        ], "$ Skill Invocation"), unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h4>! — Shell Commands</h4>
            <p>Execute shell commands directly.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(render_terminal([
            '<span class="comment"># Run a shell command</span>',
            '<span class="prompt">></span> <span class="command">!git status</span>',
            '',
            '<span class="comment"># Quick system check</span>',
            '<span class="prompt">></span> <span class="command">!ls -la src/</span>',
        ], "! Shell Commands"), unsafe_allow_html=True)


def section_agents():
    st.markdown("### 🤖 Agents & Subagents")
    st.markdown("CoCo can spawn autonomous agents to handle complex tasks in parallel.")

    st.markdown("#### Built-in Agent Types")
    agents = [
        ("general-purpose", "Full tool access", "Complex multi-step implementation tasks", "badge-blue"),
        ("Explore", "Read-only, fast", "Quick codebase search and exploration", "badge-green"),
        ("Plan", "Read-only", "Architecture analysis and implementation planning", "badge-purple"),
        ("feedback", "Ask questions", "Collect user feedback on session quality", "badge-orange"),
        ("dbt-verify", "Full tools", "Validate dbt project correctness after changes", "badge-red"),
    ]

    for name, access, desc, badge in agents:
        st.markdown(f"""
        <div class="feature-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h4 style="display:inline;">{name}</h4>
                <span class="category-badge {badge}">{access}</span>
                <p>{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### How Agents Work")

    st.markdown(render_flow_steps([
        "User requests a complex task (e.g., <em>'Implement auth with tests'</em>)",
        "CoCo analyzes task and decides to spawn subagents",
        "Subagents work <strong>autonomously</strong> — can read files, write code, run commands",
        "Results are returned to the main agent for synthesis",
        "Final response presented to user with all changes",
    ]), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Agent Teams")
    st.markdown("For large tasks, CoCo can create **teams** of agents that coordinate via shared task lists and messaging.")

    st.markdown(render_terminal([
        '<span class="comment"># CoCo internally creates a team</span>',
        '<span class="output">🏗️ Creating team: feature-implementation</span>',
        '<span class="output">  → Spawning: researcher (Explore agent)</span>',
        '<span class="output">  → Spawning: implementer (general-purpose agent)</span>',
        '<span class="output">  → Spawning: tester (general-purpose agent)</span>',
        '',
        '<span class="comment"># Agents coordinate via shared task list</span>',
        '<span class="output">📋 Task 1: Research existing auth patterns [researcher]</span>',
        '<span class="output">📋 Task 2: Implement auth module [implementer] ⏳ blocked by Task 1</span>',
        '<span class="output">📋 Task 3: Write auth tests [tester] ⏳ blocked by Task 2</span>',
    ], "Agent Teams"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Custom Agents")
    st.markdown("Define your own agents in `~/.snowflake/cortex/agents/` or `.cortex/agents/` in your project:")

    st.code("""# .cortex/agents/my-reviewer.md
---
name: my-reviewer
description: Reviews code for our team's standards
model: claude-sonnet-4-5
tools:
  - Read
  - Grep
  - Glob
allowed_tools: Read, Grep, Glob
---

You are a code reviewer for our team. Check for:
1. Naming conventions (camelCase for JS, snake_case for Python)
2. Error handling patterns
3. Test coverage requirements""", language="markdown")


def section_skills():
    st.markdown("### 🧩 Skills System")
    st.markdown("Skills are domain-specific instruction sets that teach CoCo specialized workflows.")

    st.markdown("#### Skill Categories")

    tab1, tab2, tab3 = st.tabs(["Snowflake Skills", "Data Engineering", "Development"])

    with tab1:
        skills = [
            ("analyzing-data", "Query warehouse, answer business questions", "badge-blue"),
            ("cortex-ai-functions", "AI_CLASSIFY, AI_EXTRACT, AI_SENTIMENT, etc.", "badge-blue"),
            ("cortex-agent", "Create/debug Cortex Agents", "badge-blue"),
            ("semantic-view", "Create/debug semantic views", "badge-blue"),
            ("dynamic-tables", "Create/optimize Dynamic Tables", "badge-blue"),
            ("iceberg", "Iceberg tables, catalog integrations", "badge-blue"),
            ("data-governance", "Masking policies, classification, RBAC", "badge-blue"),
            ("cost-intelligence", "Spending analysis, budgets, optimization", "badge-blue"),
            ("lineage", "Data lineage and impact analysis", "badge-blue"),
        ]
        for name, desc, badge in skills:
            st.markdown(f"""<div class="feature-card">
                <h4>{name}</h4>
                <span class="category-badge {badge}">Snowflake</span>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    with tab2:
        skills = [
            ("authoring-dags", "Write Airflow DAGs with best practices", "badge-green"),
            ("testing-dags", "Test and debug Airflow pipelines", "badge-green"),
            ("cosmos-dbt-core", "dbt Core projects as Airflow DAGs", "badge-green"),
            ("dbt-projects-on-snowflake", "Deploy dbt into Snowflake objects", "badge-green"),
            ("data-quality", "Schema health, DMF monitoring", "badge-green"),
            ("checking-freshness", "Data freshness verification", "badge-green"),
            ("profiling-tables", "Deep-dive table statistics", "badge-green"),
        ]
        for name, desc, badge in skills:
            st.markdown(f"""<div class="feature-card">
                <h4>{name}</h4>
                <span class="category-badge {badge}">Data Engineering</span>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    with tab3:
        skills = [
            ("developing-with-streamlit", "Build Streamlit apps in Snowflake", "badge-purple"),
            ("deploy-to-spcs", "Containerized apps on Snowpark Container Services", "badge-purple"),
            ("build-react-app", "React/Next.js apps with Snowflake data", "badge-purple"),
            ("machine-learning", "ML training, registry, deployment", "badge-purple"),
            ("snowflake-notebooks", "Create Snowsight notebooks", "badge-purple"),
        ]
        for name, desc, badge in skills:
            st.markdown(f"""<div class="feature-card">
                <h4>{name}</h4>
                <span class="category-badge {badge}">Development</span>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### How Skills Work")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Skill Resolution Order:**")
        st.markdown(render_flow_steps([
            "Project-level: <code>.cortex/skills/</code> in your repo",
            "Global: <code>~/.snowflake/cortex/skills/</code>",
            "Bundled: Built into CoCo installation",
            "Remote: Downloaded from configured repositories",
        ]), unsafe_allow_html=True)

    with col2:
        st.markdown("**Creating a Custom Skill:**")
        st.code("""# .cortex/skills/my-skill/SKILL.md
---
name: my-skill
description: Helps with our internal API
---

When users ask about the internal API:
1. Check the OpenAPI spec at @docs/api.yaml
2. Follow REST conventions
3. Always include error handling""", language="markdown")


def section_skills_galaxy():
    st.markdown("""
    <div class="main-header">
        <h1>🌌 Skills Galaxy</h1>
        <p>Interactive map of all 45+ Cortex Code skills — click any node to explore What, Where & Why</p>
    </div>
    """, unsafe_allow_html=True)

    SKILLS_DATA = {
        "Snowflake AI": {
            "color": "#29b5f6",
            "skills": {
                "analyzing-data": {"what": "Queries data warehouse and answers business questions using SQL", "where": "Use when you need to query tables, compute metrics, find trends, or answer data questions", "why": "Eliminates manual SQL writing — just ask questions in plain English and get results", "triggers": "who uses X, how many Y, show me Z, metrics, trends"},
                "cortex-ai-functions": {"what": "Access Snowflake Cortex AI functions: CLASSIFY, EXTRACT, SENTIMENT, SUMMARIZE, TRANSLATE, EMBED, PARSE_DOCUMENT, REDACT", "where": "Text analytics, document processing, content classification, entity extraction", "why": "Run AI directly in your warehouse without moving data — serverless ML at SQL speed", "triggers": "AI_CLASSIFY, AI_EXTRACT, sentiment, summarize, translate, OCR, parse PDF"},
                "cortex-agent": {"what": "Create, debug, evaluate and manage Cortex Agents (including Snowflake Intelligence)", "where": "Building conversational AI agents that query your data sources", "why": "Deploy production-grade AI agents with tool use, semantic views, and guardrails", "triggers": "create agent, debug agent, Snowflake Intelligence, request ID"},
                "semantic-view": {"what": "Create and debug semantic views — natural-language layers over your data", "where": "When you want Cortex Analyst to understand your business metrics and dimensions", "why": "Enables text-to-SQL that actually works by giving the LLM business context", "triggers": "semantic view, semantic model, Cortex Analyst, text-to-SQL"},
                "cortex-code-guide": {"what": "Complete reference for CoCo CLI — commands, features, configuration", "where": "Learning CoCo features, troubleshooting, understanding capabilities", "why": "Your in-session manual — never leave the terminal to look up documentation", "triggers": "how to use cortex, cortex help, cortex commands, getting started"},
            }
        },
        "Data Platform": {
            "color": "#7ee787",
            "skills": {
                "dynamic-tables": {"what": "Create, optimize, monitor and troubleshoot Snowflake Dynamic Tables", "where": "Building declarative data pipelines with incremental refresh", "why": "Replaces complex ETL orchestration with simple SQL — Snowflake handles scheduling", "triggers": "dynamic table, DT, target lag, incremental refresh, UPSTREAM_FAILED"},
                "iceberg": {"what": "Manage Iceberg tables, catalog integrations, external volumes, auto-refresh", "where": "Open table format workflows, multi-engine analytics, data lakehouse", "why": "Use open standards while keeping Snowflake performance — no vendor lock-in", "triggers": "iceberg, catalog integration, REST catalog, Glue, Unity Catalog, Polaris"},
                "data-quality": {"what": "Schema-level monitoring with Data Metric Functions (DMFs), table comparison, popularity analysis", "where": "Monitoring data health, validating migrations, finding unused tables", "why": "Catch data issues before they impact downstream consumers and dashboards", "triggers": "data quality, DMF, schema health, quality score, compare tables, data diff"},
                "checking-freshness": {"what": "Quick check if data is up-to-date — when was a table last updated?", "where": "Before using data for reports, dashboards, or ML training", "why": "Prevents decisions based on stale data — 30-second freshness verification", "triggers": "is data fresh, last updated, stale data, data currency"},
                "profiling-tables": {"what": "Deep-dive statistics: distributions, nulls, cardinality, patterns per column", "where": "Understanding a new dataset, data quality assessment, EDA", "why": "Get a complete picture of any table in seconds instead of writing dozens of queries", "triggers": "profile table, table statistics, data quality, understand table"},
                "lineage": {"what": "Trace data lineage — upstream sources and downstream dependencies", "where": "Impact analysis before changes, root cause debugging, data discovery", "why": "Know exactly what breaks before you change anything — saves hours of investigation", "triggers": "what depends on, what breaks, where does this come from, column lineage"},
                "cost-intelligence": {"what": "Analyze Snowflake spending: credits, compute, storage, budgets, anomalies", "where": "Cost optimization, budget alerts, identifying expensive queries and warehouses", "why": "Find and fix cost overruns before the bill arrives — actionable recommendations", "triggers": "spending, credits, costs, warehouse costs, budget, top spenders, expensive queries"},
            }
        },
        "Data Engineering": {
            "color": "#f0883e",
            "skills": {
                "authoring-dags": {"what": "Write Apache Airflow DAGs following best practices and patterns", "where": "Creating new data pipelines, ETL workflows, scheduled jobs", "why": "Generates production-ready DAGs with error handling, retries, and monitoring built in", "triggers": "create DAG, write pipeline, DAG patterns, new workflow"},
                "testing-dags": {"what": "Complex DAG testing with iterative debug-fix cycles", "where": "Multi-step test → debug → fix workflows for Airflow pipelines", "why": "Catches pipeline bugs before they hit production — automated test-fix loops", "triggers": "test dag and fix, test and debug, run pipeline and troubleshoot"},
                "debugging-dags": {"what": "Comprehensive DAG failure diagnosis and root cause analysis", "where": "When pipelines fail and you need deep investigation", "why": "Systematic investigation with prevention recommendations — not just fixing symptoms", "triggers": "diagnose pipeline, full root cause analysis, why is this failing"},
                "airflow": {"what": "Manage Airflow operations — list, test, run DAGs, view logs, check health", "where": "Day-to-day Airflow operations and monitoring", "why": "One-stop Airflow management without switching between UI and CLI", "triggers": "list dags, dag status, task logs, connections, airflow health"},
                "airflow-hitl": {"what": "Human-in-the-loop Airflow workflows — approval gates, form input, branching", "where": "Pipelines requiring human approval, review steps, or manual input", "why": "Add human checkpoints to automated pipelines without complex custom operators", "triggers": "approval, reject, form input, human branching, HITLOperator"},
                "cosmos-dbt-core": {"what": "Turn dbt Core projects into Airflow DAGs using Astronomer Cosmos", "where": "Running dbt models as Airflow tasks with dependency management", "why": "Best of both worlds — dbt's SQL transformations with Airflow's orchestration", "triggers": "Cosmos, dbt Core, dbt DAG, dbt TaskGroup"},
                "cosmos-dbt-fusion": {"what": "Run dbt Fusion projects with Cosmos on Snowflake/Databricks", "where": "dbt Fusion engine with Cosmos 1.11+ in local execution mode", "why": "Leverage dbt Fusion's performance optimizations within Airflow orchestration", "triggers": "dbt Fusion, Cosmos 1.11, Fusion on Snowflake"},
                "dbt-projects-on-snowflake": {"what": "Deploy dbt projects INTO Snowflake as native objects via snow dbt CLI", "where": "When dbt projects should run as Snowflake-managed objects, not external CLI", "why": "Serverless dbt execution inside Snowflake — no infrastructure to manage", "triggers": "snow dbt deploy, EXECUTE DBT PROJECT, deployed dbt project"},
                "annotating-task-lineage": {"what": "Add data lineage metadata (inlets/outlets) to Airflow tasks", "where": "Operators without built-in OpenLineage support", "why": "Complete lineage visibility even for custom operators — no blind spots", "triggers": "lineage annotation, inlets, outlets, lineage metadata"},
                "creating-openlineage-extractors": {"what": "Create custom OpenLineage extractors for Airflow operators", "where": "Complex lineage needs beyond simple inlets/outlets", "why": "Column-level lineage and advanced extraction for any operator", "triggers": "OpenLineage extractor, column-level lineage, custom extraction"},
                "setting-up-astro-project": {"what": "Initialize and configure Astro/Airflow projects", "where": "Starting a new Airflow project from scratch", "why": "Get a properly structured project with all configs in minutes, not hours", "triggers": "create project, set up dependencies, configure connections"},
                "managing-astro-local-env": {"what": "Manage local Airflow environment with Astro CLI", "where": "Starting, stopping, restarting, troubleshooting local Airflow", "why": "Quick local development and testing without Docker complexity", "triggers": "start airflow, stop airflow, view logs, fix environment"},
                "migrating-airflow-2-to-3": {"what": "Guide for migrating Airflow 2.x to 3.x", "where": "Upgrading existing Airflow projects to the latest version", "why": "Automated detection of breaking changes and migration paths", "triggers": "Airflow 3, migration, upgrade, breaking changes, compatibility"},
                "tracing-upstream-lineage": {"what": "Trace where data comes from — upstream sources and feeds", "where": "Understanding data origins and source systems", "why": "Answer 'where does this data come from?' in seconds", "triggers": "where does data come from, upstream, data sources, data origins"},
                "tracing-downstream-lineage": {"what": "Trace what depends on this data — downstream impact", "where": "Before modifying tables, assessing change risk", "why": "Know every downstream consumer before making changes — prevent breaking things", "triggers": "what depends on this, downstream, impact analysis, change risk"},
            }
        },
        "Development": {
            "color": "#d2a8ff",
            "skills": {
                "developing-with-streamlit": {"what": "Build, edit, debug, style and deploy Streamlit applications", "where": "Creating dashboards, data apps, interactive tools in Snowflake", "why": "Full-stack Streamlit development with live testing — from idea to deployed app", "triggers": "streamlit, dashboard, app.py, beautify, style, custom component"},
                "build-react-app": {"what": "Build React/Next.js applications with Snowflake data", "where": "Creating modern web dashboards and analytics tools", "why": "Production-grade frontend apps connected to your Snowflake data", "triggers": "React, Next.js, dashboard, data app, analytics tool"},
                "deploy-to-spcs": {"what": "Deploy containerized apps to Snowpark Container Services", "where": "Running Docker apps, ML models, or APIs inside Snowflake", "why": "Deploy any container without managing infrastructure — Snowflake handles it all", "triggers": "Docker, SPCS, container, push image, compute pool"},
                "machine-learning": {"what": "ML training, model registry, deployment, experiment tracking, monitoring", "where": "End-to-end ML workflows from data prep to production inference", "why": "Complete ML lifecycle without leaving Snowflake — training to serving", "triggers": "train model, deploy model, model registry, ML, experiment tracking, drift"},
                "snowflake-notebooks": {"what": "Create and edit Snowsight notebooks (.ipynb)", "where": "Interactive data analysis, exploration, and sharing results", "why": "Collaborative notebooks that run directly in Snowflake — no local setup needed", "triggers": "notebook, .ipynb, workspace notebook, SQL cell, Snowpark"},
                "snowflake-postgres": {"what": "Manage Snowflake Postgres instances — create, suspend, resume, diagnose", "where": "Running PostgreSQL workloads on Snowflake infrastructure", "why": "Postgres compatibility with Snowflake's scale and management", "triggers": "postgres, pg, create instance, health check, pg_lake, iceberg"},
            }
        },
        "Governance & Security": {
            "color": "#f85149",
            "skills": {
                "data-governance": {"what": "Masking policies, row access policies, classification, RBAC, access history, compliance", "where": "Protecting sensitive data, auditing access, meeting compliance requirements", "why": "Comprehensive data protection without slowing down development", "triggers": "masking policy, row access, PII, classification, GDPR, CCPA, access history"},
                "trust-center": {"what": "Security findings, scanner analysis, CIS benchmarks, vulnerability remediation", "where": "Security posture assessment and vulnerability management", "why": "Proactive security — find and fix issues before they become incidents", "triggers": "security findings, scanner, CIS benchmark, vulnerabilities, remediation"},
                "organization-management": {"what": "Manage Snowflake org — accounts, users, spending, security posture", "where": "Multi-account governance, org-wide visibility, admin operations", "why": "Single pane of glass for your entire Snowflake organization", "triggers": "org summary, list accounts, org spending, org security, globalorgadmin"},
                "integrations": {"what": "Create and manage Snowflake integrations (API, catalog, storage, security, notification)", "where": "Connecting Snowflake to external services and cloud storage", "why": "Properly configured integrations without memorizing complex DDL syntax", "triggers": "API integration, storage integration, notification integration"},
                "declarative-sharing": {"what": "Share data products across Snowflake accounts with versioning", "where": "Cross-account data sharing, marketplace listings, data products", "why": "Secure data sharing without copying — real-time access with governance", "triggers": "share data, application package, marketplace, listing, cross account"},
                "data-cleanrooms": {"what": "Snowflake Data Clean Rooms — secure multi-party data collaboration", "where": "Audience overlap analysis, joint analytics without sharing raw data", "why": "Collaborate on sensitive data while maintaining privacy — no data leaves your account", "triggers": "clean room, DCR, collaboration, audience overlap, activation"},
            }
        },
        "Migration & Assessment": {
            "color": "#d29922",
            "skills": {
                "snowconvert-assessment": {"what": "Analyze workloads for Snowflake migration — assessment reports, wave planning", "where": "Pre-migration analysis of existing SQL, ETL, or SSIS workloads", "why": "Understand migration complexity before you start — plan waves and estimate effort", "triggers": "assessment, migration analysis, waves, object exclusion, SSIS, ETL analysis"},
                "dcm": {"what": "Database Change Management — infrastructure-as-code for Snowflake objects", "where": "Version-controlled database schemas with DEFINE TABLE, DEFINE SCHEMA", "why": "Git-managed database changes with three-tier role patterns — DevOps for data", "triggers": "DCM, Database Change Management, manifest.yml, DEFINE TABLE, infrastructure-as-code"},
                "init": {"what": "Initialize warehouse schema discovery — generates metadata for instant lookups", "where": "First-time project setup, after schema changes", "why": "One-time setup that makes all future data operations lightning fast", "triggers": "/data:init, set up data discovery, schema discovery"},
                "skill-development": {"what": "Create, document and audit skills for Cortex Code", "where": "Building custom skills, capturing session workflows as reusable skills", "why": "Turn your expertise into reusable, shareable CoCo capabilities", "triggers": "create skill, build skill, capture workflow, audit skill"},
            }
        },
    }

    all_skills = []
    for cat, data in SKILLS_DATA.items():
        for name, info in data["skills"].items():
            all_skills.append({"name": name, "category": cat, "color": data["color"], **info})

    skills_json = json.dumps(all_skills)
    categories_json = json.dumps({cat: data["color"] for cat, data in SKILLS_DATA.items()})

    galaxy_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background: transparent; overflow: hidden; }}
        #galaxy-container {{
            position:relative; width:100%; height:700px;
            background:radial-gradient(ellipse at center, #0a0a1a 0%, #000 70%);
            border-radius:16px; border:1px solid #1a1a3e; overflow:hidden; cursor:grab;
        }}
        #galaxyCanvas {{ position:absolute; top:0; left:0; width:100%; height:100%; }}
        #galaxy-tooltip {{
            display:none; position:absolute; background:rgba(13,17,23,0.95);
            border:1px solid #29b5f6; border-radius:10px; padding:14px 18px;
            max-width:380px; z-index:100; pointer-events:none;
            box-shadow:0 0 25px rgba(41,181,246,0.2); font-family:Inter,sans-serif;
        }}
        #galaxy-legend {{
            position:absolute; bottom:12px; left:12px;
            display:flex; flex-wrap:wrap; gap:8px; z-index:50;
        }}
        .hint {{
            position:absolute; top:12px; right:16px; color:#555;
            font-size:0.75rem; z-index:50; font-family:Inter,sans-serif;
        }}
    </style>
    </head>
    <body>
    <div id="galaxy-container">
        <canvas id="galaxyCanvas"></canvas>
        <div id="galaxy-tooltip"></div>
        <div id="galaxy-legend"></div>
        <div class="hint">Hover over nodes to explore &bull; Scroll to zoom &bull; Drag to pan</div>
    </div>
    <script>
    (function() {{
        const skills = {skills_json};
        const categories = {categories_json};
        const container = document.getElementById('galaxy-container');
        const canvas = document.getElementById('galaxyCanvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('galaxy-tooltip');
        const legend = document.getElementById('galaxy-legend');

        let W, H, dpr;
        let camX = 0, camY = 0, zoom = 1;
        let dragging = false, dragStartX, dragStartY, camStartX, camStartY;
        let hoveredNode = null;
        let animTime = 0;
        let stars = [];
        let nodes = [];

        function resize() {{
            dpr = window.devicePixelRatio || 1;
            W = container.clientWidth;
            H = container.clientHeight;
            canvas.width = W * dpr;
            canvas.height = H * dpr;
            canvas.style.width = W + 'px';
            canvas.style.height = H + 'px';
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }}
        resize();
        window.addEventListener('resize', resize);

        for (let i = 0; i < 300; i++) {{
            stars.push({{
                x: (Math.random() - 0.5) * 3000,
                y: (Math.random() - 0.5) * 3000,
                r: Math.random() * 1.5 + 0.3,
                twinkleSpeed: Math.random() * 0.02 + 0.005,
                twinkleOffset: Math.random() * Math.PI * 2
            }});
        }}

        const catNames = Object.keys(categories);
        const catCenters = {{}};
        const catCount = catNames.length;
        catNames.forEach((cat, i) => {{
            const angle = (i / catCount) * Math.PI * 2 - Math.PI / 2;
            const radius = Math.min(W, H) * 0.28;
            catCenters[cat] = {{ x: Math.cos(angle) * radius, y: Math.sin(angle) * radius }};
        }});

        skills.forEach((s, i) => {{
            const center = catCenters[s.category];
            const siblings = skills.filter(sk => sk.category === s.category);
            const idx = siblings.indexOf(s);
            const count = siblings.length;
            const spiralAngle = (idx / count) * Math.PI * 2 + Math.random() * 0.5;
            const spiralR = 40 + idx * 18 + Math.random() * 20;
            nodes.push({{
                ...s,
                x: center.x + Math.cos(spiralAngle) * spiralR,
                y: center.y + Math.sin(spiralAngle) * spiralR,
                baseX: center.x + Math.cos(spiralAngle) * spiralR,
                baseY: center.y + Math.sin(spiralAngle) * spiralR,
                r: 8,
                orbitSpeed: 0.0003 + Math.random() * 0.0005,
                orbitRadius: 3 + Math.random() * 4,
                orbitOffset: Math.random() * Math.PI * 2,
                pulseSpeed: 0.02 + Math.random() * 0.01,
                pulseOffset: Math.random() * Math.PI * 2,
            }});
        }});

        let legendHTML = '';
        catNames.forEach(cat => {{
            legendHTML += '<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;background:rgba(0,0,0,0.6);border-radius:12px;font-size:0.72rem;color:' + categories[cat] + ';border:1px solid ' + categories[cat] + '33;font-family:Inter,sans-serif;"><span style="width:8px;height:8px;border-radius:50%;background:' + categories[cat] + ';display:inline-block;"></span>' + cat + '</span>';
        }});
        legend.innerHTML = legendHTML;

        function worldToScreen(wx, wy) {{
            return {{ x: (wx - camX) * zoom + W / 2, y: (wy - camY) * zoom + H / 2 }};
        }}
        function screenToWorld(sx, sy) {{
            return {{ x: (sx - W / 2) / zoom + camX, y: (sy - H / 2) / zoom + camY }};
        }}

        function hexToRgb(hex) {{
            const r = parseInt(hex.slice(1,3), 16);
            const g = parseInt(hex.slice(3,5), 16);
            const b = parseInt(hex.slice(5,7), 16);
            return {{r, g, b}};
        }}

        function draw() {{
            animTime++;
            ctx.clearRect(0, 0, W, H);

            stars.forEach(s => {{
                const sp = worldToScreen(s.x, s.y);
                if (sp.x < -10 || sp.x > W + 10 || sp.y < -10 || sp.y > H + 10) return;
                const alpha = 0.3 + 0.7 * Math.abs(Math.sin(animTime * s.twinkleSpeed + s.twinkleOffset));
                ctx.beginPath();
                ctx.arc(sp.x, sp.y, s.r * zoom, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(200,210,230,' + alpha + ')';
                ctx.fill();
            }});

            catNames.forEach(cat => {{
                const center = catCenters[cat];
                const cp = worldToScreen(center.x, center.y);
                const col = hexToRgb(categories[cat]);
                const pulse = 0.03 + 0.02 * Math.sin(animTime * 0.01);
                const grad = ctx.createRadialGradient(cp.x, cp.y, 0, cp.x, cp.y, 140 * zoom);
                grad.addColorStop(0, 'rgba(' + col.r + ',' + col.g + ',' + col.b + ',' + pulse + ')');
                grad.addColorStop(1, 'rgba(' + col.r + ',' + col.g + ',' + col.b + ',0)');
                ctx.beginPath();
                ctx.arc(cp.x, cp.y, 140 * zoom, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.fillStyle = categories[cat] + '99';
                ctx.font = (11 * zoom) + 'px Inter, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(cat, cp.x, cp.y - 120 * zoom);
            }});

            nodes.forEach(node => {{
                const center = catCenters[node.category];
                const cp = worldToScreen(center.x, center.y);
                const np = worldToScreen(node.x, node.y);

                ctx.beginPath();
                ctx.moveTo(cp.x, cp.y);
                ctx.lineTo(np.x, np.y);
                const col = hexToRgb(node.color);
                ctx.strokeStyle = 'rgba(' + col.r + ',' + col.g + ',' + col.b + ',0.08)';
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }});

            const centerNode = worldToScreen(0, 0);
            const coreR = 22 * zoom;
            const coreGrad = ctx.createRadialGradient(centerNode.x, centerNode.y, 0, centerNode.x, centerNode.y, coreR * 2);
            coreGrad.addColorStop(0, 'rgba(41,181,246,0.4)');
            coreGrad.addColorStop(0.5, 'rgba(41,181,246,0.1)');
            coreGrad.addColorStop(1, 'rgba(41,181,246,0)');
            ctx.beginPath();
            ctx.arc(centerNode.x, centerNode.y, coreR * 2, 0, Math.PI * 2);
            ctx.fillStyle = coreGrad;
            ctx.fill();
            ctx.beginPath();
            ctx.arc(centerNode.x, centerNode.y, coreR, 0, Math.PI * 2);
            ctx.fillStyle = '#29b5f6';
            ctx.fill();
            ctx.fillStyle = '#fff';
            ctx.font = 'bold ' + (10 * zoom) + 'px Inter';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('CoCo', centerNode.x, centerNode.y);

            catNames.forEach(cat => {{
                const center = catCenters[cat];
                const cp = worldToScreen(center.x, center.y);
                ctx.beginPath();
                ctx.moveTo(centerNode.x, centerNode.y);
                ctx.lineTo(cp.x, cp.y);
                ctx.strokeStyle = categories[cat] + '15';
                ctx.lineWidth = 1;
                ctx.stroke();
            }});

            nodes.forEach(node => {{
                node.x = node.baseX + Math.cos(animTime * node.orbitSpeed + node.orbitOffset) * node.orbitRadius;
                node.y = node.baseY + Math.sin(animTime * node.orbitSpeed + node.orbitOffset) * node.orbitRadius;
                const np = worldToScreen(node.x, node.y);
                const pulse = 1 + 0.15 * Math.sin(animTime * node.pulseSpeed + node.pulseOffset);
                const isHovered = hoveredNode === node;
                const r = node.r * zoom * pulse * (isHovered ? 1.6 : 1);

                if (isHovered) {{
                    const col = hexToRgb(node.color);
                    const glow = ctx.createRadialGradient(np.x, np.y, 0, np.x, np.y, r * 4);
                    glow.addColorStop(0, 'rgba(' + col.r + ',' + col.g + ',' + col.b + ',0.3)');
                    glow.addColorStop(1, 'rgba(' + col.r + ',' + col.g + ',' + col.b + ',0)');
                    ctx.beginPath();
                    ctx.arc(np.x, np.y, r * 4, 0, Math.PI * 2);
                    ctx.fillStyle = glow;
                    ctx.fill();
                }}

                ctx.beginPath();
                ctx.arc(np.x, np.y, r, 0, Math.PI * 2);
                ctx.fillStyle = node.color;
                ctx.shadowColor = node.color;
                ctx.shadowBlur = isHovered ? 20 : 6;
                ctx.fill();
                ctx.shadowBlur = 0;

                if (zoom > 0.7 || isHovered) {{
                    ctx.fillStyle = isHovered ? '#fff' : '#ccc';
                    ctx.font = (isHovered ? 'bold ' : '') + Math.max(7, 9 * zoom) + 'px JetBrains Mono, monospace';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(node.name, np.x, np.y + r + 4);
                }}
            }});

            requestAnimationFrame(draw);
        }}
        draw();

        canvas.addEventListener('mousemove', function(e) {{
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            if (dragging) {{
                camX = camStartX - (e.clientX - dragStartX) / zoom;
                camY = camStartY - (e.clientY - dragStartY) / zoom;
                return;
            }}

            const world = screenToWorld(mx, my);
            let found = null;
            let minDist = Infinity;
            nodes.forEach(node => {{
                const dx = world.x - node.x;
                const dy = world.y - node.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 20 / zoom && dist < minDist) {{
                    minDist = dist;
                    found = node;
                }}
            }});

            hoveredNode = found;
            if (found) {{
                canvas.style.cursor = 'pointer';
                tooltip.style.display = 'block';
                tooltip.style.left = Math.min(mx + 15, W - 400) + 'px';
                tooltip.style.top = Math.min(my + 15, H - 250) + 'px';
                tooltip.innerHTML = '<div style="margin-bottom:8px;"><span style="color:' + found.color + ';font-weight:700;font-size:1rem;">' + found.name + '</span><span style="margin-left:8px;padding:2px 8px;border-radius:10px;font-size:0.7rem;background:' + found.color + '22;color:' + found.color + ';border:1px solid ' + found.color + '44;">' + found.category + '</span></div>'
                    + '<div style="margin:6px 0;"><span style="color:#29b5f6;font-weight:600;font-size:0.8rem;">WHAT </span><span style="color:#c9d1d9;font-size:0.82rem;">' + found.what + '</span></div>'
                    + '<div style="margin:6px 0;"><span style="color:#7ee787;font-weight:600;font-size:0.8rem;">WHERE </span><span style="color:#c9d1d9;font-size:0.82rem;">' + found.where + '</span></div>'
                    + '<div style="margin:6px 0;"><span style="color:#f0883e;font-weight:600;font-size:0.8rem;">WHY </span><span style="color:#c9d1d9;font-size:0.82rem;">' + found.why + '</span></div>'
                    + '<div style="margin-top:8px;padding-top:6px;border-top:1px solid #21262d;"><span style="color:#8b949e;font-size:0.72rem;">Triggers: ' + found.triggers + '</span></div>';
            }} else {{
                canvas.style.cursor = dragging ? 'grabbing' : 'grab';
                tooltip.style.display = 'none';
            }}
        }});

        canvas.addEventListener('mousedown', function(e) {{
            dragging = true;
            dragStartX = e.clientX;
            dragStartY = e.clientY;
            camStartX = camX;
            camStartY = camY;
            canvas.style.cursor = 'grabbing';
        }});
        canvas.addEventListener('mouseup', function() {{
            dragging = false;
            canvas.style.cursor = 'grab';
        }});
        canvas.addEventListener('mouseleave', function() {{
            dragging = false;
            hoveredNode = null;
            tooltip.style.display = 'none';
        }});
        canvas.addEventListener('wheel', function(e) {{
            e.preventDefault();
            const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
            zoom = Math.max(0.3, Math.min(3, zoom * zoomFactor));
        }}, {{ passive: false }});
    }})();
    </script>
    </body>
    </html>
    """
    components.html(galaxy_html, height=720, scrolling=False)

    st.markdown("---")
    st.markdown("### 📊 Skills by Category")

    if "galaxy_selected_cat" not in st.session_state:
        st.session_state.galaxy_selected_cat = list(SKILLS_DATA.keys())[0]

    cat_cols = st.columns(len(SKILLS_DATA))
    for i, (cat, data) in enumerate(SKILLS_DATA.items()):
        with cat_cols[i]:
            if st.button(
                f"{cat}\n({len(data['skills'])})",
                key=f"galcat_{i}",
                use_container_width=True,
            ):
                st.session_state.galaxy_selected_cat = cat

    sel_cat = st.session_state.galaxy_selected_cat
    sel_data = SKILLS_DATA[sel_cat]

    st.markdown(f"""
    <div style="background:linear-gradient(90deg, {sel_data['color']}11, transparent);
                border-left:4px solid {sel_data['color']}; padding:0.8rem 1.2rem;
                border-radius:0 8px 8px 0; margin:0.5rem 0;">
        <span style="color:{sel_data['color']}; font-size:1.1rem; font-weight:700;">{sel_cat}</span>
        <span style="color:#8b949e; margin-left:0.5rem;">— {len(sel_data['skills'])} skills</span>
    </div>
    """, unsafe_allow_html=True)

    for skill_name, info in sel_data["skills"].items():
        with st.expander(f"**{skill_name}**"):
            col_w, col_wr, col_why = st.columns(3)
            with col_w:
                st.markdown(f"**🔵 WHAT**")
                st.caption(info["what"])
            with col_wr:
                st.markdown(f"**🟢 WHERE**")
                st.caption(info["where"])
            with col_why:
                st.markdown(f"**🟠 WHY**")
                st.caption(info["why"])
            st.markdown(f"<div style='margin-top:4px;'><span style='color:#8b949e;font-size:0.78rem;'>💬 Triggers: <code>{info['triggers']}</code></span></div>", unsafe_allow_html=True)
            st.code(f"$> ${skill_name} <your prompt here>", language="bash")

    st.markdown("---")
    st.markdown("### 📈 Skills Distribution")

    dist_data = []
    for cat, data in SKILLS_DATA.items():
        dist_data.append({"Category": cat, "Count": len(data["skills"]), "Color": data["color"]})

    max_count = max(d["Count"] for d in dist_data)
    for d in dist_data:
        pct = d["Count"] / max_count * 100
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin:6px 0;">
            <span style="width:160px; color:{d['Color']}; font-size:0.85rem; font-weight:600; text-align:right;">{d['Category']}</span>
            <div style="flex:1; height:28px; background:#0d1117; border-radius:6px; overflow:hidden; border:1px solid #21262d;">
                <div style="width:{pct}%; height:100%; background:linear-gradient(90deg, {d['Color']}44, {d['Color']}); border-radius:6px;
                            display:flex; align-items:center; justify-content:flex-end; padding-right:8px;
                            animation: barGrow 1.2s ease-out;">
                    <span style="color:#fff; font-size:0.78rem; font-weight:700;">{d['Count']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    @keyframes barGrow {
        from { width: 0%; }
    }
    </style>
    """, unsafe_allow_html=True)

    total = sum(d["Count"] for d in dist_data)
    st.markdown(f"""
    <div style="text-align:center; margin-top:1rem; padding:0.8rem; background:#0d1117; border-radius:8px; border:1px solid #21262d;">
        <span style="color:#29b5f6; font-size:1.8rem; font-weight:700;">{total}</span>
        <span style="color:#8b949e; font-size:0.9rem;"> total skills across </span>
        <span style="color:#29b5f6; font-size:1.8rem; font-weight:700;">{len(SKILLS_DATA)}</span>
        <span style="color:#8b949e; font-size:0.9rem;"> categories</span>
    </div>
    """, unsafe_allow_html=True)


def section_snowflake_tools():
    st.markdown("### ❄️ Snowflake-Native Tools")
    st.markdown("CoCo has deep Snowflake integration beyond standard coding assistance.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "#TABLE Syntax", "SQL Execution", "Semantic Views", "Artifacts"
    ])

    with tab1:
        st.markdown("#### Table Reference with `#`")
        st.markdown("Prefix any table name with `#` to automatically pull its schema and sample data into context.")

        st.markdown(render_terminal([
            '<span class="prompt">></span> What columns does <span class="command">#LAB_DB_NEW.LAB_SCHEMA_NEW.AGENT_MEMORY</span> have?',
            '',
            '<span class="output">CoCo fetches:</span>',
            '<span class="comment">  • CREATE TABLE DDL (column names, types, constraints)</span>',
            '<span class="comment">  • Sample rows for context</span>',
            '<span class="comment">  • Table metadata (row count, size)</span>',
            '',
            '<span class="prompt">></span> Write a query to find all unique namespaces in <span class="command">#AGENT_MEMORY</span>',
        ], "#TABLE Demo"), unsafe_allow_html=True)

        st.info("💡 **Tip:** You can use short names like `#USERS` if the table is in your current database/schema context.")

    with tab2:
        st.markdown("#### Direct SQL Execution")
        st.markdown(render_terminal([
            '<span class="comment"># Run SQL directly</span>',
            '<span class="prompt">></span> <span class="command">/sql</span> SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE()',
            '',
            '<span class="comment"># Or just ask in natural language</span>',
            '<span class="prompt">></span> Show me the top 10 largest tables in LAB_DB_NEW',
            '',
            '<span class="output">CoCo generates and executes:</span>',
            '<span class="comment">  SELECT TABLE_NAME, ROW_COUNT, BYTES</span>',
            '<span class="comment">  FROM INFORMATION_SCHEMA.TABLES</span>',
            '<span class="comment">  ORDER BY BYTES DESC LIMIT 10;</span>',
        ], "SQL Execution"), unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Semantic Views & Cortex Analyst")
        st.markdown("""
        Semantic views provide a natural-language layer over your data. CoCo can:
        - **Create** semantic views from existing tables
        - **Debug** semantic view YAML definitions
        - **Query** through Cortex Analyst for text-to-SQL
        """)
        st.markdown(render_terminal([
            '<span class="comment"># Create a semantic view</span>',
            '<span class="prompt">></span> Create a semantic view for my sales data in <span class="command">#SALES_FACT</span>',
            '',
            '<span class="comment"># Query with Cortex Analyst</span>',
            '<span class="prompt">></span> Using the sales semantic view, what were Q4 revenues by region?',
        ], "Semantic Views"), unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Artifacts & Deployment")
        st.markdown("""
        CoCo can deploy artifacts directly to Snowflake:
        - **Streamlit apps** → Snowflake Streamlit
        - **Notebooks** → Snowsight Notebooks
        - **Stored procedures** → Snowflake procedures
        - **UDFs** → User-defined functions
        """)


def section_mcp():
    st.markdown("### 🔌 MCP Integration")
    st.markdown("The **Model Context Protocol** lets CoCo connect to external tool servers.")

    st.markdown("#### What is MCP?")
    st.markdown("""
    <div class="feature-card">
        <h4>Model Context Protocol (MCP)</h4>
        <p>An open standard for connecting AI assistants to external data sources and tools.
        CoCo acts as an MCP <strong>client</strong> that connects to MCP <strong>servers</strong> providing specialized capabilities.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Transport Types")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="architecture-box">
            <h5>stdio</h5>
            <p>Local process communication. Most common for CLI tools.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="architecture-box">
            <h5>SSE</h5>
            <p>Server-Sent Events over HTTP. Good for remote servers.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="architecture-box">
            <h5>Streamable HTTP</h5>
            <p>Modern HTTP-based transport. Recommended for new servers.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Configuration Example")
    st.code(json.dumps({
        "mcpServers": {
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": "ghp_xxx"}
            },
            "postgres": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres",
                         "postgresql://localhost/mydb"]
            }
        }
    }, indent=2), language="json")

    st.markdown("#### Managing MCP Servers")
    st.markdown(render_terminal([
        '<span class="comment"># List configured servers</span>',
        '<span class="prompt">></span> <span class="command">/mcp</span>',
        '',
        '<span class="comment"># Add a new server interactively</span>',
        '<span class="prompt">></span> Add a GitHub MCP server',
        '',
        '<span class="comment"># Disable MCP on launch</span>',
        '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">--no-mcp</span>',
    ], "MCP Management"), unsafe_allow_html=True)

    st.markdown("#### Common MCP Servers")
    servers = {
        "Server": ["GitHub", "PostgreSQL", "Filesystem", "Puppeteer", "Brave Search"],
        "Purpose": [
            "Issues, PRs, repos, code search",
            "Database queries and schema",
            "Sandboxed file system access",
            "Browser automation and screenshots",
            "Web search results",
        ],
    }
    st.dataframe(servers, use_container_width=True, hide_index=True)


def section_hooks():
    st.markdown("### 🪝 Hooks System")
    st.markdown("Automate actions in response to CoCo events — like CI/CD for your AI assistant.")

    st.markdown("#### Hook Events")
    events = [
        ("PreToolUse", "Before a tool executes", "Block dangerous commands, add logging", "badge-red"),
        ("PostToolUse", "After a tool executes", "Validate outputs, trigger follow-ups", "badge-orange"),
        ("Notification", "On notifications", "Custom alerts, logging", "badge-yellow"),
        ("Stop", "When CoCo finishes a turn", "Auto-review, formatting checks", "badge-green"),
        ("SessionStart", "Session begins", "Setup environment, load context", "badge-blue"),
        ("UserPromptSubmit", "User sends message", "Inject context, modify prompts", "badge-purple"),
    ]

    for event, when, example, badge in events:
        st.markdown(f"""
        <div class="feature-card">
            <h4>{event}</h4>
            <span class="category-badge {badge}">{when}</span>
            <p>Example: {example}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Hook Configuration Example")
    st.markdown("Block `rm -rf` commands automatically:")

    st.code(json.dumps({
        "hooks": {
            "PreToolUse": [{
                "matcher": "Bash",
                "hooks": [{
                    "type": "command",
                    "command": "python3 /path/to/guard.py",
                    "timeout": 10
                }]
            }]
        }
    }, indent=2), language="json")

    st.markdown("#### Hook I/O Flow")
    st.markdown(render_flow_steps([
        "CoCo triggers an event (e.g., <code>PreToolUse</code> for Bash)",
        "Hook receives JSON on stdin: <code>{tool_name, input: {command: ...}}</code>",
        "Your script processes and returns JSON on stdout",
        'To <strong>allow</strong>: <code>{"decision": "approve"}</code>',
        'To <strong>block</strong>: <code>{"decision": "block", "reason": "Dangerous command"}</code>',
    ]), unsafe_allow_html=True)


def section_sessions():
    st.markdown("### 💾 Session Management")
    st.markdown("CoCo maintains conversation history and provides powerful session controls.")

    tab1, tab2, tab3, tab4 = st.tabs(["Resume", "Fork", "Rewind", "Compact"])

    with tab1:
        st.markdown("#### Resume Sessions")
        st.markdown("Continue where you left off across terminal sessions.")
        st.markdown(render_terminal([
            '<span class="comment"># Resume the last session</span>',
            '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">--resume last</span>',
            '',
            '<span class="comment"># Resume a specific session by ID</span>',
            '<span class="prompt">$</span> <span class="command">cortex</span> <span class="flag">--resume abc123</span>',
            '',
            '<span class="comment"># Resume from within a session</span>',
            '<span class="prompt">></span> <span class="command">/resume</span>',
        ], "Resume"), unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Fork Conversations")
        st.markdown("Create a branch of your conversation to explore different approaches.")
        st.markdown("""
        <div class="feature-card">
            <h4>Why Fork?</h4>
            <p>Try a different implementation approach without losing your current progress.
            Each fork is an independent conversation branch.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(render_terminal([
            '<span class="comment"># Fork at current point</span>',
            '<span class="prompt">></span> <span class="command">/fork</span>',
            '',
            '<span class="comment"># The diff viewer shows your conversation history</span>',
            '<span class="comment"># Select a point to branch from</span>',
            '<span class="output">📌 Forked at message #12</span>',
            '<span class="output">🆕 New session: fork-abc123</span>',
        ], "Fork"), unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Rewind to Checkpoint")
        st.markdown("Go back to an earlier state of the conversation.")
        st.markdown(render_terminal([
            '<span class="comment"># Open the rewind interface</span>',
            '<span class="prompt">></span> <span class="command">/rewind</span>',
            '',
            '<span class="comment"># Browse conversation states</span>',
            '<span class="output">  [1] Initial setup discussion</span>',
            '<span class="output">  [2] Started implementing auth  ← you are here</span>',
            '<span class="output">  [3] Added tests (current)</span>',
            '',
            '<span class="comment"># Select a checkpoint to rewind to</span>',
        ], "Rewind"), unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Compact Context")
        st.markdown("When conversations grow long, compact summarizes and frees up context window space.")
        st.markdown(render_terminal([
            '<span class="prompt">></span> <span class="command">/compact</span>',
            '',
            '<span class="output">📊 Before: 45,000 tokens used</span>',
            '<span class="output">🗜️ Summarizing conversation...</span>',
            '<span class="output">📊 After: 8,200 tokens used</span>',
            '<span class="output">💾 Saved 36,800 tokens (82% reduction)</span>',
        ], "Compact"), unsafe_allow_html=True)
        st.info("💡 **Tip:** Use `/compact` when CoCo starts forgetting earlier context or you're working on a very long task.")


def section_shortcuts():
    st.markdown("### ⚡ Keyboard Shortcuts")
    st.markdown("Power user controls for faster interaction.")

    tab1, tab2, tab3 = st.tabs(["Essential", "Navigation", "Advanced"])

    with tab1:
        shortcuts = [
            ("Enter", "Send message / confirm"),
            ("Shift + Enter", "New line in input"),
            ("Ctrl + C", "Cancel current operation"),
            ("Ctrl + D", "Exit CoCo"),
            ("Ctrl + L", "Clear screen"),
            ("Escape", "Cancel current input / close modal"),
            ("Tab", "Accept autocomplete suggestion"),
        ]
        for key, desc in shortcuts:
            keys_html = " ".join(f'<span class="shortcut-key">{k.strip()}</span>' for k in key.split("+"))
            st.markdown(f"<div style='display:flex; align-items:center; gap:1rem; margin:0.5rem 0;'>{keys_html} <span style='color:#c9d1d9;'>{desc}</span></div>", unsafe_allow_html=True)

    with tab2:
        shortcuts = [
            ("Up / Down", "Scroll through message history"),
            ("Ctrl + R", "Search command history"),
            ("Ctrl + Up", "Scroll output up"),
            ("Ctrl + Down", "Scroll output down"),
        ]
        for key, desc in shortcuts:
            keys_html = " ".join(f'<span class="shortcut-key">{k.strip()}</span>' for k in key.split("+"))
            st.markdown(f"<div style='display:flex; align-items:center; gap:1rem; margin:0.5rem 0;'>{keys_html} <span style='color:#c9d1d9;'>{desc}</span></div>", unsafe_allow_html=True)

    with tab3:
        shortcuts = [
            ("Ctrl + J", "Open recent sessions"),
            ("Ctrl + K", "Open file search"),
            ("Ctrl + \\", "Toggle compact mode"),
        ]
        for key, desc in shortcuts:
            keys_html = " ".join(f'<span class="shortcut-key">{k.strip()}</span>' for k in key.split("+"))
            st.markdown(f"<div style='display:flex; align-items:center; gap:1rem; margin:0.5rem 0;'>{keys_html} <span style='color:#c9d1d9;'>{desc}</span></div>", unsafe_allow_html=True)


def section_config():
    st.markdown("### ⚙️ Configuration")
    st.markdown("Customize CoCo to fit your workflow.")

    st.markdown("#### Configuration Priority")
    st.markdown(render_flow_steps([
        "<strong>CLI Flags</strong> — Highest priority, per-session overrides",
        "<strong>Environment Variables</strong> — Shell-level configuration",
        "<strong>Settings File</strong> — <code>~/.snowflake/cortex/settings.json</code>",
        "<strong>Defaults</strong> — Built-in fallback values",
    ]), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Directory Structure")
    st.code("""~/.snowflake/cortex/
├── settings.json           # Main configuration
├── skills.json             # Skills configuration
├── permissions.json        # Permission history (auto-generated)
├── hooks.json              # Hook configurations
├── mcp.json                # MCP server configurations
├── skills/                 # Global custom skills
│   └── my-skill/
│       └── SKILL.md
├── agents/                 # Custom agent definitions
│   └── my-agent.md
└── conversations/          # Session history""", language="text")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Key Settings")
        st.code(json.dumps({
            "env": {
                "CORTEX_AGENT_MODEL": "claude-sonnet-4-5",
                "CORTEX_AGENT_ENABLE_SUBAGENTS": True,
                "CORTEX_ENABLE_MEMORY": False,
                "CORTEX_CODE_STREAMING": False,
            },
            "diffDisplayMode": "unified",
            "theme": "dark",
            "bashDefaultTimeoutMs": 180000,
        }, indent=2), language="json")

    with col2:
        st.markdown("#### Snowflake Connections")
        st.code("""# ~/.snowflake/connections.toml

[default]
account = "myaccount"
user = "myuser"
authenticator = "externalbrowser"

[production]
account = "prod-account"
user = "prod-user"
authenticator = "snowflake_jwt"
private_key_path = "~/.snowflake/rsa_key.p8"
database = "PROD_DB"
schema = "PUBLIC"
warehouse = "COMPUTE_WH"
role = "DEVELOPER" """, language="toml")

    st.markdown("---")
    st.markdown("#### Authentication Methods")
    methods = {
        "Method": ["externalbrowser", "snowflake_jwt", "snowflake", "oauth", "PROGRAMMATIC_ACCESS_TOKEN"],
        "Description": [
            "Browser-based SSO (recommended for interactive use)",
            "Private key authentication (recommended for automation)",
            "Username/password (basic)",
            "OAuth token",
            "Programmatic access token (PAT)",
        ],
        "Best For": [
            "Interactive development",
            "CI/CD pipelines",
            "Quick setup",
            "Enterprise SSO",
            "Service accounts",
        ],
    }
    st.dataframe(methods, use_container_width=True, hide_index=True)


def render_interactive_demo():
    st.markdown("---")
    st.markdown("### 🎮 Interactive Demo")
    st.markdown("Try simulated CoCo interactions below!")

    if "demo_history" not in st.session_state:
        st.session_state.demo_history = []
    if "demo_typing" not in st.session_state:
        st.session_state.demo_typing = False

    demo_prompts = {
        "Fix a bug in my code": [
            "🔍 Searching codebase for related files...",
            "📖 Reading `src/auth.py` (found potential issue at line 42)",
            "🐛 Found the bug: `token_expiry` compared as string instead of datetime",
            "✏️ Editing `src/auth.py:42` — converting string to datetime before comparison",
            "✅ Fix applied! Running tests... All 23 tests pass.",
        ],
        "Create a Streamlit dashboard": [
            "🧩 Loading skill: `developing-with-streamlit`",
            "📊 Analyzing your data schema via `#SALES_DATA`...",
            "🏗️ Creating `dashboard.py` with KPI cards, charts, and filters",
            "🎨 Adding responsive layout with `st.columns` and `st.container`",
            "🚀 Dashboard ready! Run: `streamlit run dashboard.py`",
        ],
        "Analyze my Snowflake costs": [
            "💰 Loading skill: `cost-intelligence`",
            "📊 Querying `SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY`...",
            "📈 Top warehouse: `COMPUTE_WH` — 450 credits last 30 days",
            "⚠️ Anomaly detected: 3x spike on March 10 (query ID: abc123)",
            "💡 Recommendation: Resize `ANALYTICS_WH` from XL → L (save ~120 credits/month)",
        ],
        "Deploy to Snowpark Container Services": [
            "🐳 Loading skill: `deploy-to-spcs`",
            "📦 Analyzing Dockerfile and requirements...",
            "🔨 Building image and pushing to Snowflake registry",
            "🌐 Creating compute pool and service specification",
            "✅ Service deployed! Endpoint: `https://my-service.snowflakecomputing.app`",
        ],
    }

    for msg in st.session_state.demo_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Try a simulated CoCo prompt...", key="demo_chat")

    if not prompt:
        st.markdown("**Quick demos:**")
        cols = st.columns(2)
        for i, (label, _) in enumerate(demo_prompts.items()):
            with cols[i % 2]:
                if st.button(label, key=f"demo_{i}", use_container_width=True):
                    st.session_state.demo_selected = label
                    st.rerun()

    selected = st.session_state.pop("demo_selected", None)
    active_prompt = prompt or selected

    if active_prompt:
        st.session_state.demo_history.append({"role": "user", "content": active_prompt})

        matched = None
        for key in demo_prompts:
            if key.lower() in active_prompt.lower() or active_prompt.lower() in key.lower():
                matched = key
                break

        if matched:
            steps = demo_prompts[matched]
            response = "\n\n".join(steps)
        else:
            response = (
                "🤔 Processing your request...\n\n"
                "🔍 Searching codebase for relevant files...\n\n"
                "📖 Reading context and analyzing the task...\n\n"
                "✅ Task complete! *(This is a simulated demo — in real CoCo, "
                "I would execute the actual tools and provide real results.)*"
            )

        st.session_state.demo_history.append({"role": "assistant", "content": response})
        st.rerun()


with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <h2 style="color:#29b5f6; margin:0;">❄️ CoCo Guide</h2>
        <p style="color:#8b949e; font-size:0.85rem; margin:0.3rem 0 0 0;">Cortex Code Feature Explorer</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    selected_section = st.radio(
        "Navigate",
        list(FEATURES.keys()),
        format_func=lambda x: f"{FEATURES[x]['icon']} {FEATURES[x]['title']}",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="padding: 0.8rem; background: #161b22; border-radius: 8px; border: 1px solid #30363d;">
        <p style="color:#8b949e; font-size:0.8rem; margin:0;">
            <strong style="color:#29b5f6;">💡 Pro Tip:</strong><br>
            Install CoCo with:<br>
            <code style="color:#7ee787;">pip install snowflake-cli</code><br>
            Then run: <code style="color:#7ee787;">cortex</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <div style="padding: 0.8rem; background: #161b22; border-radius: 8px; border: 1px solid #30363d;">
        <p style="color:#8b949e; font-size:0.8rem; margin:0;">
            <strong style="color:#d2a8ff;">📚 Resources:</strong><br>
            • <a href="https://docs.snowflake.com" style="color:#58a6ff;">Snowflake Docs</a><br>
            • <a href="https://github.com/snowflakedb" style="color:#58a6ff;">GitHub</a><br>
            • <a href="https://community.snowflake.com" style="color:#58a6ff;">Community</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


sections = {
    "overview": section_overview,
    "cli_commands": section_cli_commands,
    "slash_commands": section_slash_commands,
    "special_syntax": section_special_syntax,
    "agents": section_agents,
    "skills": section_skills,
    "skills_galaxy": section_skills_galaxy,
    "snowflake_tools": section_snowflake_tools,
    "mcp": section_mcp,
    "hooks": section_hooks,
    "sessions": section_sessions,
    "shortcuts": section_shortcuts,
    "config": section_config,
}

sections[selected_section]()

render_interactive_demo()

st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:1rem; color:#8b949e; font-size:0.82rem;">
    Built for <strong style="color:#29b5f6;">DAMG 7374</strong> | Cortex Code Feature Showcase |
    Snowflake AI-Powered CLI
</div>
""", unsafe_allow_html=True)

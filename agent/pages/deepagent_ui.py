"""
Streamlit UI showcasing Deep Agents features:
- Subagents with specialized tools
- write_todos middleware (task planning)
- interrupt_on with human-in-the-loop
- Tools middleware
"""
import os
import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Deep Agent Demo", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8001")

# ============================================================================
# SIDEBAR
# ============================================================================

def show():
    with st.sidebar:
        st.title("⚙️ Configuration")
        mode = st.radio("Execution Mode", ["Standard", "Streaming"])
        st.divider()

        st.subheader("🧠 Agent Architecture")
        st.markdown("""
        **Main Agent:** Coordinator
        - Tools: approve_decision

        **SubAgent 1:** Product Searcher
        - Tools: search_db, check_inventory

        **SubAgent 2:** Pricing Analyst
        - Tools: get_pricing_info
        """)

    # ============================================================================
    # MAIN HEADER
    # ============================================================================

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.title("🤖 Deep Agent Demo")
        st.markdown("SubAgents • Planning • Human-in-the-Loop")

    with col3:
        try:
            health = requests.get(f"{API_URL}/health").json()
            st.metric("Status", "✅ Online")
        except:
            st.metric("Status", "❌ Offline")

    # ============================================================================
    # SESSION STATE
    # ============================================================================

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "todos" not in st.session_state:
        st.session_state.todos = []
    if "interrupt_pending" not in st.session_state:
        st.session_state.interrupt_pending = False

    # ============================================================================
    # TABS
    # ============================================================================

    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Execute", "📋 TODOs", "🛑 Interrupts", "📚 Docs"])

    # ============================================================================
    # TAB 1: EXECUTE
    # ============================================================================

    with tab1:
        st.subheader("Task Execution")

        col1, col2 = st.columns([3, 1])

        with col1:
            query = st.text_area(
                "Enter task query:",
                placeholder="e.g., 'Find laptop, check price and stock'",
                height=100,
                key="query_input"
            )

        with col2:
            st.write("")
            st.write("")
            execute_btn = st.button("▶ Execute", type="primary", use_container_width=True)

        if execute_btn and query:
            st.session_state.thread_id = None  # Reset thread for new task

            with st.spinner("⏳ Agent thinking..."):
                try:
                    payload = {"query": query, "thread_id": st.session_state.thread_id}

                    if mode == "Standard":
                        response = requests.post(f"{API_URL}/task", json=payload)

                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.thread_id = result["thread_id"]

                            st.success("✅ Task completed")

                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(result["response"])
                            with col2:
                                st.caption(f"Thread: {result['thread_id'][:8]}...")
                        else:
                            st.error(f"API Error: {response.json()}")

                    else:  # Streaming
                        response = requests.post(f"{API_URL}/task/stream", json=payload, stream=True)

                        if response.status_code == 200:
                            st.info("🔄 Streaming response...")
                            placeholder = st.empty()
                            full_text = ""

                            for line in response.iter_lines():
                                if line:
                                    try:
                                        data = json.loads(line.decode().replace("data: ", ""))
                                        if "content" in data:
                                            full_text += data["content"]
                                            placeholder.write(full_text)
                                            st.session_state.thread_id = data.get("thread_id")
                                    except:
                                        pass

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {str(e)}")

    # ============================================================================
    # TAB 2: TODOs (write_todos middleware)
    # ============================================================================

    with tab2:
        st.subheader("📋 Task Planning (write_todos Middleware)")

        st.info("""
        The agent automatically uses `write_todos` to break down complex tasks into steps.
        This appears when planning multi-step workflows.
        """)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write("**Example TODO structure:**")
            example_todos = """
    1. ✅ Search for laptop in database
    2. 🔄 Check inventory status
    3. 🔄 Get pricing information
    4. ⏳ Analyze discount options
    5. ⏳ Present recommendation to user
            """
            st.code(example_todos)

        with col2:
            st.write("**Status**")
            if st.session_state.thread_id:
                st.success(f"Active Thread: {st.session_state.thread_id[:12]}...")
                st.caption("TODOs tracked in real-time")
            else:
                st.warning("No active task yet")

    # ============================================================================
    # TAB 3: INTERRUPTS (interrupt_on + Human-in-the-loop)
    # ============================================================================

    with tab3:
        st.subheader("🛑 Human-in-the-Loop (interrupt_on)")

        st.info("""
        Tools marked with `interrupt_on` pause execution and wait for human approval.
        This demo has `approve_decision` requiring approval.
        """)

        if st.session_state.thread_id:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write("**Interrupt Configuration:**")
                interrupt_config = {
                    "tool": "approve_decision",
                    "status": "active",
                    "allowed_decisions": ["approve", "edit", "reject"]
                }
                st.json(interrupt_config)

            with col2:
                st.write("**Check Status**")
                if st.button("🔍 Check Pending"):
                    try:
                        resp = requests.get(f"{API_URL}/task/{st.session_state.thread_id}/interrupt")
                        if resp.status_code == 200:
                            data = resp.json()
                            if "pending_action" in data:
                                st.warning(f"⏸ Pending: {data['pending_action']}")

                                decision = st.radio("Your decision:", data["options"])
                                feedback = st.text_input("Feedback (optional):")

                                if st.button("Submit Decision"):
                                    resume_payload = {
                                        "thread_id": st.session_state.thread_id,
                                        "decision": decision,
                                        "feedback": feedback
                                    }
                                    resume_resp = requests.post(
                                        f"{API_URL}/task/{st.session_state.thread_id}/resume",
                                        json=resume_payload
                                    )
                                    if resume_resp.status_code == 200:
                                        st.success("✅ Task resumed")
                                        st.write(resume_resp.json()["response"])
                            else:
                                st.success("✅ No interruptions pending")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.warning("Execute a task first to see interrupts")

    # ============================================================================
    # TAB 4: DOCUMENTATION
    # ============================================================================

    with tab4:
        st.subheader("📚 Deep Agents Features")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🧠 SubAgents
            Specialized agents for specific tasks:
            - Product Searcher: search_db, check_inventory
            - Pricing Analyst: get_pricing_info
            - Context isolation & clean execution

            ### 📋 write_todos Middleware
            Task planning and breakdown:
            - Automatic task decomposition
            - Real-time progress tracking
            - Adaptive planning
            """)

        with col2:
            st.markdown("""
            ### 🛑 interrupt_on
            Human-in-the-loop workflow:
            - Pause execution for approval
            - Three modes: approve, edit, reject
            - LangGraph checkpointer for state

            ### 🔧 Tools Middleware
            - Each agent has specialized tools
            - Main: approve_decision (gated)
            - Subagents: domain-specific tools
            """)

        st.divider()

        st.markdown("""
        ### Example Queries
        - "Find laptop product and check stock"
        - "What's the price of iPhone with discounts?"
        - "Search phone, check inventory, approve recommendation"

        ### Architecture
        ```
        Main Agent (Coordinator)
        ├── SubAgent: Product Searcher
        │   ├── search_db
        │   └── check_inventory
        └── SubAgent: Pricing Analyst
            └── get_pricing_info
        ```
        """)
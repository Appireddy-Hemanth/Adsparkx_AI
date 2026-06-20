import os
import sys
import uuid
import streamlit as st

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.graph import build_graph
from ui.components.sidebar import render_sidebar
from ui.components.persona_badge import render_persona_badge
from ui.components.source_expander import render_sources
from ui.components.escalation_modal import render_escalation_panel
from ui.components.rate_limit_banner import render_rate_limit_banner

# ⚠️ ALL styling in this file follows DESIGN.md (Spotify theme)
# Canvas: #121212 | Accent: #1DB954 | Font: Inter/Circular | Grid: 8pt

st.set_page_config(
    page_title="NovaSuite Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Spotify Theme
st.markdown("""
<style>
/* DESIGN.md — Spotify Theme */
:root {
    --bg-base: #121212;
    --bg-card: #181818;
    --bg-elevated: #282828;
    --accent-green: #1DB954;
    --accent-green-hover: #1ed760;
    --text-primary: #FFFFFF;
    --text-secondary: #B3B3B3;
    --text-muted: #6A6A6A;
    --border-subtle: rgba(255,255,255,0.1);
    --radius: 8px;
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
}

/* Set dark canvas */
.stApp {
    background-color: var(--bg-base);
    color: var(--text-primary);
}

.stChatMessage {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border-subtle) !important;
    padding: var(--spacing-md) !important;
    margin-bottom: var(--spacing-sm) !important;
}

.stSidebar {
    background-color: var(--bg-card) !important;
}

/* Persona badges */
.badge-technical {
    background: #1DB954;
    color: #000000;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 8px;
}
.badge-frustrated {
    background: #E22134;
    color: #FFFFFF;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 8px;
}
.badge-executive {
    background: #F59B23;
    color: #000000;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 8px;
}

/* Source cards */
.source-card {
    background: var(--bg-elevated);
    border-left: 4px solid var(--accent-green);
    padding: var(--spacing-md);
    border-radius: var(--radius);
    margin: var(--spacing-sm) 0;
}

/* Escalation alert */
.escalation-alert {
    background: rgba(226, 33, 52, 0.15);
    border: 1px solid #E22134;
    border-radius: var(--radius);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

/* Rate limit indicators */
.rate-limit-ok {
    border-left: 4px solid #1DB954;
}
.rate-limit-warn {
    border-left: 4px solid #F59B23;
}
.rate-limit-crit {
    border-left: 4px solid #E22134;
}

/* Metric cards */
.metric-card {
    background: var(--bg-elevated);
    border-radius: var(--radius);
    padding: var(--spacing-md);
    text-align: center;
    margin-bottom: var(--spacing-md);
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--accent-green);
}
.metric-label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# App Title banner
st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; letter-spacing: -1px;'>NovaSuite Support Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #B3B3B3; font-size: 16px;'>Persona-Adaptive Customer Support Agent</p>", unsafe_allow_html=True)

# Lazy build graph
@st.cache_resource
def get_agent_graph():
    return build_graph()

graph = get_agent_graph()

# Session State Initialization
if "agent_state" not in st.session_state:
    st.session_state["agent_state"] = {
        "session_id": str(uuid.uuid4())[:8],
        "messages": [],
        "current_message": "",
        "persona": "",
        "persona_confidence": 0.0,
        "retrieved_chunks": [],
        "retrieval_confidence": 0.0,
        "response": "",
        "escalate": False,
        "escalation_reason": "",
        "handoff_summary": None,
        "turn_count": 0,
        "resolution_attempts": 0,
        "sentiment_scores": [],
        "attempted_steps": []
    }

agent_state = st.session_state["agent_state"]

# Render dashboard sidebar
render_sidebar(agent_state)

# Render daily quota remaining / banner in sidebar
calls_used = agent_state.get("gemini_daily_calls", 0)
render_rate_limit_banner(calls_used)

# Display chat messages from history
for msg in agent_state["messages"]:
    role = msg.get("role")
    content = msg.get("content")
    
    with st.chat_message(role):
        st.write(content)
        
        # Render turn-specific metadata for assistant replies
        if role == "assistant":
            persona = msg.get("persona")
            persona_conf = msg.get("persona_confidence", 0.0)
            retrieved_chunks = msg.get("retrieved_chunks", [])
            
            if persona:
                render_persona_badge(persona, persona_conf)
            if retrieved_chunks:
                render_sources(retrieved_chunks)

# Handle Escalation panel if currently escalated
if agent_state.get("escalate"):
    render_escalation_panel(agent_state.get("handoff_summary"))

# Accept user input in all cases
if user_input := st.chat_input("How can I assist you with NovaSuite today?"):
    if agent_state.get("escalate"):
        # Append user message to history
        agent_state["messages"].append({"role": "user", "content": user_input})
        
        # Friendly support notification response
        escalation_response = "A human support agent has been notified and is reviewing your request. Please wait."
        agent_state["messages"].append({
            "role": "assistant",
            "content": escalation_response,
            "persona": "HUMAN_HANDOFF",
            "persona_confidence": 1.0,
            "retrieved_chunks": []
        })
        
        # Save back to session state
        st.session_state["agent_state"] = agent_state
        st.rerun()
    else:
        # Display user message instantly
        with st.chat_message("user"):
            st.write(user_input)

        # Update state with current message
        agent_state["current_message"] = user_input

        # Execute turn
        with st.spinner("Analyzing message & retrieving documentation..."):
            try:
                # Run LangGraph State Machine
                updated_state = graph.invoke(agent_state)
                
                # Update Turn-level metadata on assistant message to store in history
                messages = updated_state.get("messages", [])
                if messages and messages[-1].get("role") == "assistant":
                    messages[-1]["persona"] = updated_state.get("persona", "UNKNOWN")
                    messages[-1]["persona_confidence"] = updated_state.get("persona_confidence", 0.0)
                    messages[-1]["retrieved_chunks"] = updated_state.get("retrieved_chunks", [])
                
                # Save back to session state
                st.session_state["agent_state"] = updated_state
                st.rerun()
            except Exception as e:
                st.error(f"Error handling request: {e}")

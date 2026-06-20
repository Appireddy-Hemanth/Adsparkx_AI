import streamlit as st
import json

def render_escalation_panel(handoff_summary: dict):
    """Renders the escalation panel showing the HandoffSummary JSON."""
    if not handoff_summary:
        return

    st.markdown("""
    <div class='escalation-alert'>
        <h3 style='color: #E22134; margin: 0;'>⚠️ Session Escalated to Human Support</h3>
        <p style='color: #FFFFFF; margin-top: 8px;'>
            The AI assistant has detected that this query requires human agent intervention. 
            A structured handoff summary has been generated for the support team.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Handoff Summary (JSON)")
    st.json(handoff_summary)

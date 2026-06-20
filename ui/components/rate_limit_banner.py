import streamlit as st

def render_rate_limit_banner(calls_used: int):
    """Renders the rate limit banner in the sidebar or main panel."""
    limit = 1500
    percentage = (calls_used / limit) * 100
    
    st.sidebar.subheader("Gemini API Rate Guard")
    
    if calls_used >= 1200: # 80%+ Critical
        status_class = "rate-limit-crit"
        status_text = "CRITICAL"
        color = "#E22134"
    elif calls_used >= 750: # 50%+ Warning
        status_class = "rate-limit-warn"
        status_text = "WARNING"
        color = "#F59B23"
    else:
        status_class = "rate-limit-ok"
        status_text = "NORMAL"
        color = "#1DB954"

    st.sidebar.markdown(f"""
    <div class='{status_class}' style='padding: 8px; background: #181818; border-radius: 4px; margin-bottom: 8px;'>
        <strong style='color: {color};'>Status: {status_text}</strong><br/>
        Daily Calls: {calls_used} / {limit} RPD ({percentage:.1f}%)
    </div>
    """, unsafe_allow_html=True)

import streamlit as st

def get_sentiment_trend_emoji(scores: list[float]) -> str:
    if len(scores) < 2:
        return "➡️"
    diff = scores[-1] - scores[-2]
    if diff < -0.15:
        return "📉 (Declining)"
    elif diff > 0.15:
        return "📈 (Improving)"
    return "➡️ (Stable)"

def render_sidebar(state: dict):
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: #1DB954; margin-bottom: 0;'>NovaSuite</h2>
            <span style='background: rgba(29, 185, 84, 0.1); color: #1DB954; border: 1px solid #1DB954; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; letter-spacing: 1px;'>🟢 SYSTEM ONLINE</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. Session Panel
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-label'>Session ID</div><div class='metric-value' style='font-size: 18px;'>{state.get('session_id', 'N/A')}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-label'>Turns</div><div class='metric-value' style='font-size: 20px;'>{state.get('turn_count', 0)}</div>", unsafe_allow_html=True)
        with col2:
            latency = state.get("response_time", 0.0)
            st.markdown(f"<div class='metric-label'>Latency</div><div class='metric-value' style='font-size: 20px;'>{latency:.2f}s</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")

        # 2. Persona Panel
        persona = state.get("persona", "UNKNOWN")
        persona_conf = state.get("persona_confidence", 0.0)
        
        st.markdown("<div style='font-weight: bold; font-size: 14px; letter-spacing: 0.5px; color: #b3b3b3;'>DETECTED PERSONA</div>", unsafe_allow_html=True)
        if persona == "TECHNICAL_EXPERT":
            st.markdown("<div style='margin-top: 8px;'><span class='badge-technical'>🔧 TECHNICAL EXPERT</span></div>", unsafe_allow_html=True)
        elif persona == "FRUSTRATED_USER":
            st.markdown("<div style='margin-top: 8px;'><span class='badge-frustrated'>😤 FRUSTRATED USER</span></div>", unsafe_allow_html=True)
        elif persona == "BUSINESS_EXECUTIVE":
            st.markdown("<div style='margin-top: 8px;'><span class='badge-executive'>💼 BUSINESS EXECUTIVE</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top: 8px;'><span style='background: #6A6A6A; color: #fff; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 11px;'>👤 INITIALIZING</span></div>", unsafe_allow_html=True)
            
        st.progress(max(0.0, min(1.0, persona_conf)))
        st.caption(f"Confidence: {persona_conf*100:.1f}%")

        st.write("---")

        # 3. Retrieval Panel
        retrieval_conf = state.get("retrieval_confidence", 0.0)
        st.markdown("<div style='font-weight: bold; font-size: 14px; letter-spacing: 0.5px; color: #b3b3b3;'>RAG GROUNDING</div>", unsafe_allow_html=True)
        st.progress(max(0.0, min(1.0, retrieval_conf)))
        
        # Determine confidence band
        if retrieval_conf >= 0.75:
            band = "HIGH"
            band_color = "#1DB954"
        elif retrieval_conf >= 0.50:
            band = "MEDIUM"
            band_color = "#F59B23"
        else:
            band = "LOW"
            band_color = "#E22134"
            
        st.markdown(f"<div style='font-size: 13px; margin-top: 4px;'>Confidence: {retrieval_conf*100:.1f}% (<span style='color: {band_color}; font-weight: bold;'>{band}</span>)</div>", unsafe_allow_html=True)
        
        num_sources = len(state.get("retrieved_chunks", []))
        st.caption(f"Sources Used: {num_sources} chunks")

        st.write("---")

        # 4. Sentiment Panel
        sentiment_scores = state.get("sentiment_scores", [])
        latest_sentiment = sentiment_scores[-1] if sentiment_scores else 0.0
        trend_emoji = get_sentiment_trend_emoji(sentiment_scores)
        
        st.markdown("<div style='font-weight: bold; font-size: 14px; letter-spacing: 0.5px; color: #b3b3b3;'>SENTIMENT TRACKER</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 8px;'>{latest_sentiment:+.2f} {trend_emoji}</div>", unsafe_allow_html=True)
        
        if len(sentiment_scores) > 1:
            st.line_chart(sentiment_scores, height=80)

        # 5. Attempted Steps Tracker (Persona Memory)
        attempted_steps = state.get("attempted_steps", [])
        if attempted_steps:
            st.write("---")
            st.markdown("<div style='font-weight: bold; font-size: 14px; letter-spacing: 0.5px; color: #b3b3b3;'>ATTEMPTED STEPS</div>", unsafe_allow_html=True)
            for step in attempted_steps:
                st.markdown(f"<div style='font-size: 12px; color: #B3B3B3; margin-top: 4px; padding-left: 8px; border-left: 2px solid #1DB954;'>{step}</div>", unsafe_allow_html=True)

        st.write("---")

        # 6. Reset Action
        if st.button("Reset Session", use_container_width=True):
            st.session_state.clear()
            st.rerun()

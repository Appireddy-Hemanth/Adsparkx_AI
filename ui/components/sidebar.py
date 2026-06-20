import streamlit as st

def get_sentiment_trend_emoji(scores: list[float]) -> str:
    if len(scores) < 2:
        return "➡️"
    diff = scores[-1] - scores[-2]
    if diff < -0.15:
        return "📉"
    elif diff > 0.15:
        return "📈"
    return "➡️"

def render_sidebar(state: dict):
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #1DB954;'>NovaSuite Dashboard</h2>", unsafe_allow_html=True)
        
        # 1. Session Panel
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-label'>Session ID</div><div class='metric-value' style='font-size: 20px;'>{state.get('session_id', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-label'>Turn Counter</div><div class='metric-value'>{state.get('turn_count', 0)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")

        # 2. Persona Panel
        persona = state.get("persona", "UNKNOWN")
        persona_conf = state.get("persona_confidence", 0.0)
        
        st.subheader("Detected Persona")
        if persona == "TECHNICAL_EXPERT":
            st.markdown("<span class='badge-technical'>🔧 TECHNICAL EXPERT</span>", unsafe_allow_html=True)
        elif persona == "FRUSTRATED_USER":
            st.markdown("<span class='badge-frustrated'>😤 FRUSTRATED USER</span>", unsafe_allow_html=True)
        elif persona == "BUSINESS_EXECUTIVE":
            st.markdown("<span class='badge-executive'>💼 BUSINESS EXECUTIVE</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='background: #6A6A6A; color: #fff; padding: 4px 12px; border-radius: 12px;'>👤 UNKNOWN</span>", unsafe_allow_html=True)
            
        st.progress(persona_conf)
        st.caption(f"Confidence: {persona_conf*100:.1f}%")

        st.write("---")

        # 3. Retrieval Panel
        retrieval_conf = state.get("retrieval_confidence", 0.0)
        st.subheader("RAG Grounding")
        st.progress(retrieval_conf)
        st.caption(f"Retrieval Confidence: {retrieval_conf*100:.1f}%")
        
        num_sources = len(state.get("retrieved_chunks", []))
        st.caption(f"Sources Used: {num_sources} chunks")

        st.write("---")

        # 4. Sentiment Panel
        sentiment_scores = state.get("sentiment_scores", [])
        latest_sentiment = sentiment_scores[-1] if sentiment_scores else 0.0
        trend_emoji = get_sentiment_trend_emoji(sentiment_scores)
        
        st.subheader("Conversation Sentiment")
        st.markdown(f"<div style='font-size: 24px; font-weight: bold;'>Score: {latest_sentiment:.2f} {trend_emoji}</div>", unsafe_allow_html=True)
        
        st.write("---")

        # 5. Reset Action
        if st.button("Reset Session", use_container_width=True):
            st.session_state.clear()
            st.rerun()

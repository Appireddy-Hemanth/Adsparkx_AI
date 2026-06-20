import streamlit as st

def render_persona_badge(persona: str, confidence: float):
    """Renders a stylized persona badge using Custom CSS styling."""
    if persona == "TECHNICAL_EXPERT":
        st.markdown(f"<span class='badge-technical'>🔧 TECHNICAL EXPERT ({confidence*100:.0f}%)</span>", unsafe_allow_html=True)
    elif persona == "FRUSTRATED_USER":
        st.markdown(f"<span class='badge-frustrated'>😤 FRUSTRATED USER ({confidence*100:.0f}%)</span>", unsafe_allow_html=True)
    elif persona == "BUSINESS_EXECUTIVE":
        st.markdown(f"<span class='badge-executive'>💼 BUSINESS EXECUTIVE ({confidence*100:.0f}%)</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='background: #6A6A6A; color: #fff; padding: 4px 12px; border-radius: 12px; font-weight: bold;'>👤 UNKNOWN ({confidence*100:.0f}%)</span>", unsafe_allow_html=True)

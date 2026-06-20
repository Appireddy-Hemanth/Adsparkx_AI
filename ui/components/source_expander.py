import streamlit as st

def render_sources(retrieved_chunks: list[dict]):
    """Renders the sources used in an expander, formatted as cards."""
    if not retrieved_chunks:
        return
        
    with st.expander("📚 View Grounded Sources"):
        for idx, chunk in enumerate(retrieved_chunks):
            source = chunk.get("source", "unknown")
            section = chunk.get("section", "General")
            page = chunk.get("page", 1)
            score = chunk.get("score", 0.0)
            text = chunk.get("text", "")
            
            # Extract or compute confidence band
            band = chunk.get("confidence_band")
            if not band:
                if score >= 0.75:
                    band = "HIGH"
                elif score >= 0.50:
                    band = "MEDIUM"
                else:
                    band = "LOW"
            
            if band == "HIGH":
                band_color = "#1DB954"
            elif band == "MEDIUM":
                band_color = "#F59B23"
            else:
                band_color = "#E22134"
                
            st.markdown(f"""
            <div class='source-card'>
                <strong>Source {idx+1}: {source}</strong> | Section: {section} | Page/Index: {page} | Score: {score:.2f} (<span style='color: {band_color}; font-weight: bold;'>{band}</span>)
                <div style='margin-top: 8px; font-style: italic; color: #B3B3B3; font-size: 14px;'>
                    "{text}"
                </div>
            </div>
            """, unsafe_allow_html=True)

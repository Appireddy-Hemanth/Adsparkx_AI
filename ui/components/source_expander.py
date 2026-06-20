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
            
            st.markdown(f"""
            <div class='source-card'>
                <strong>Source {idx+1}: {source}</strong> | Section: {section} | Page/Index: {page} | Relevance Score: {score:.2f}
                <div style='margin-top: 8px; font-style: italic; color: #B3B3B3;'>
                    "{text}"
                </div>
            </div>
            """, unsafe_allow_html=True)

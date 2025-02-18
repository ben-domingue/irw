import streamlit as st

def show_documentation_page():
    st.markdown("### Documentation and Tutorial")

    st.markdown("""
    This section provides the **official data standard** and a **tutorial** on how to use the tool.

    - The **iframe** below displays the official data standard from the IRW (Item Response Warehouse), which provides guidelines for structuring your data.
    - The **video tutorial** on the right explains how to use this tool step-by-step to process and map your data into the correct format.

    Please refer to both resources for a complete understanding of how to use this tool effectively.
    """)

    iframe_html = """
        <iframe src="https://datapages.github.io/irw/standard.html" width="800" height="600"></iframe>
    """

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(iframe_html, unsafe_allow_html=True)
    with col2:
        st.video("https://youtu.be/erezdWzk_60") 
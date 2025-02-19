import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Import tab modules
from tabs.dataset_tab import show_dataset_tab
from tabs.id_tab import show_id_tab
from tabs.item_tab import show_item_tab
from tabs.resp_tab import show_resp_tab
from tabs.optional_data_tab import show_optional_data_tab
from tabs.review_tab import show_review_tab
from tabs.feedback_tab import show_feedback_tab

# Import page modules
from components.home import show_home_page
from components.documentation import show_documentation_page

def init_session_state():
    """Initialize all session state variables."""
    session_vars = {
        'home_page': True,
        'documentation_page': False,
        'processing_page': False,
        'df': None,
        'extended_df': None,
        'irw_dataframe': pd.DataFrame(),
        'id_row_range': (),
        'id_col_range': (),
        'item_row_range': (),
        'item_col_range': (),
        'indices_df': pd.DataFrame(),
        'feedback_response': None,
        'feedback_nps': None,
        'feedback_data_url': None,
        'feedback_comments': None,
        'contact_info': None
    }
    
    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

def show_sidebar():
    """Display and handle sidebar navigation."""
    st.sidebar.title("Project Menu")

    if st.sidebar.button("🏠 Home"):
        st.session_state.home_page = True
        st.session_state.documentation_page = False
        st.session_state.processing_page = False

    if st.sidebar.button("📚 Documentation"):
        st.session_state.home_page = False
        st.session_state.documentation_page = True
        st.session_state.processing_page = False

    if st.sidebar.button("🛠️ Process Data"):
        st.session_state.home_page = False
        st.session_state.documentation_page = False
        st.session_state.processing_page = True

    with st.sidebar:
        st.markdown("---")
        st.subheader("IRW Dataset Preview")
        if st.session_state.irw_dataframe.empty:
            st.write("No data mapped yet.")
        else:
            st.dataframe(st.session_state.irw_dataframe, use_container_width=True)

def main():
    """Main application function."""
    st.set_page_config(page_title="IRW Dataset Builder", layout="wide")
    init_session_state()
    show_sidebar()

    if st.session_state.home_page:
        show_home_page()
    elif st.session_state.documentation_page:
        show_documentation_page()
    else:
        # Create tabs
        tabs = st.tabs([
            "Dataset", "ID", "Item", "Resp", 
            "Optional Data", "Review and Save", "Feedback"
        ])

        with tabs[0]:
            show_dataset_tab()
        with tabs[1]:
            show_id_tab()
        with tabs[2]:
            show_item_tab()
        with tabs[3]:
            show_resp_tab()
        with tabs[4]:
            show_optional_data_tab()
        with tabs[5]:
            show_review_tab()
        with tabs[6]:
            show_feedback_tab()

if __name__ == "__main__":
    main()



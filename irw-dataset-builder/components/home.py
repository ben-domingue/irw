import streamlit as st

def show_home_page():
    st.title("Welcome to the IRW Dataset Builder")
    st.write("""
        **Welcome to the IRW Dataset Builder!**  

        The IRW Dataset Builder is a Streamlit app designed to help you process and transform your data into the **Item Response Warehouse (IRW) format**.

        ### Key Features:
        - **Data Processing:** Easily convert your raw data into the IRW pattern.  
        - **Flexible Integration:** Supports mapping additional dataset information into the IRW structure.  
        - **User-Friendly Interface:** Intuitive and accessible for users of all experience levels.  
        - **Guided Workflow:** Ensures your dataset meets the required format.

        ### Required Data:
        Your dataset must include these **mandatory data**:  
        1. **id** - A unique identifier for each respondent (e.g., student ID).  
        2. **item** - The item or question being answered.  
        3. **resp** - The respondent's answer or response to the item.  

        ### Additional Information:
        If your dataset includes extra columns or metadata (e.g., demographics, timestamps), you can map this information into the IRW pattern. To learn how to incorporate additional data, consult the documentations and tutorials page.  

        Start processing your data now and make the most of psychometric insights with the IRW Dataset Builder!
    """) 
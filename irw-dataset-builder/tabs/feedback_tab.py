import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def show_feedback_tab():
    st.title("Feedback")

    st.subheader("We value your feedback!")
    st.write("""
    Let us know if the tool met your needs for processing the data.  
    Your input helps us improve and make the tool more robust.
    """)

    st.subheader("How would you rate your overall experience?")
    st.session_state.feedback_nps = st.slider("Rate the tool", 0, 5)
    
    # User feedback question
    st.radio(
        "Were you able to process the data the way you wanted?",
        options=["Yes", "No"],
        key="feedback_response"
    )

    # If the user selects "No", display additional input fields
    if st.session_state.feedback_response == "No":
        st.write("We're sorry to hear that! Please share more details below.")
        
        # Input for dataset link
        st.session_state.feedback_data_url = st.text_input(
            "Link to your dataset", 
            placeholder="Paste the dataset link here"
        )
        
        # Input for detailed comment
        st.session_state.feedback_comments = st.text_area(
            "Detailed Comment", 
            placeholder="Explain how you planned to treat the data and why it wasn't possible using the tool"
        )
        
        # Input for contact information
        st.session_state.contact_info = st.text_area(
            "Contact Info", 
            placeholder="Please provide contact information in case we need further clarifications (e.g., John Doe, johndoe@gmail.com)"
        )
    
    # For "Yes" response, display a thank-you message
    elif st.session_state.feedback_response == "Yes":
        st.success("We're glad the tool met your needs! Thank you for using it.")
    
    # Button to submit feedback
    if st.button("Submit Feedback"):
        if st.session_state.feedback_response == "No" and not (
            st.session_state.feedback_data_url and st.session_state.feedback_comments
        ):
            st.error("Please fill in both the dataset link and detailed comments.")
        else:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read()

            user_data = [
                st.session_state.feedback_nps,
                st.session_state.feedback_comments,
                st.session_state.feedback_data_url,
                st.session_state.contact_info
            ]
            df.loc[len(df)] = user_data

            conn.update(data=df)
            st.success("Thank you for your feedback! We'll review it and keep improving the tool.") 
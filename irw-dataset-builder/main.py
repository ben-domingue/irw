import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection


if 'home_page' not in st.session_state:
    st.session_state.home_page = True  # Start on the home page by default
if 'documentation_page' not in st.session_state:
    st.session_state.documentation_page = False 
if 'processing_page' not in st.session_state:
    st.session_state.processing_page = False 
if 'df' not in st.session_state:
    st.session_state.df = None
if 'extended_df' not in st.session_state:
    st.session_state.extended_df = None
if "irw_dataframe" not in st.session_state:
    st.session_state.irw_dataframe = pd.DataFrame()
if "id_row_range" not in st.session_state:
    st.session_state.id_row_range = ()
if "id_col_range" not in st.session_state:
    st.session_state.id_col_range = ()
if "item_row_range" not in st.session_state:
    st.session_state.item_row_range = ()
if "item_col_range" not in st.session_state:
    st.session_state.item_col_range = ()   
if "indices_df" not in st.session_state:
    st.session_state.indices_df = pd.DataFrame()

## configurations for feedback sheet
if "feedback_response" not in st.session_state:
    st.session_state.feedback_response = None
if "feedback_nps" not in st.session_state:
    st.session_state.feedback_nps = None
if "feedback_data_url" not in st.session_state:
    st.session_state.feedback_data_url = None
if "feedback_comments" not in st.session_state:
    st.session_state.feedback_comments = None
if "contact_info" not in st.session_state:
    st.session_state.contact_info = None
# Set up the page configuration
st.set_page_config(page_title="IRW Dataset Builder", layout="wide")

# Sidebar menu
st.sidebar.title("Project Menu")

# Home button
if st.sidebar.button("🏠 Home"):
    st.session_state.home_page = True
    st.session_state.documentation_page = False
    st.session_state.processing_page = False

# Documentation button
if st.sidebar.button("📚 Documentation"):
    st.session_state.home_page = False
    st.session_state.documentation_page = True
    st.session_state.processing_page = False

# Create New Project button
if st.sidebar.button("🛠️ Process Data"):
    st.session_state.home_page = False
    st.session_state.documentation_page = False
    st.session_state.processing_page = True

# Separator

with st.sidebar:
    # Display the IRW dataframe
    st.markdown("---")  # Horizontal line as a separator
    st.subheader("IRW Dataset Preview")
    if st.session_state.irw_dataframe.empty:
        st.write("No data mapped yet.")
    else:
        st.dataframe(st.session_state.irw_dataframe, use_container_width=True)

if st.session_state.home_page:
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
    st.session_state.home_page = False
    st.stop()

if st.session_state.documentation_page:

    # Display a heading for the documentation section
    st.markdown("### Documentation and Tutorial")

    # Display a brief explanation of what the iframe and video represent
    st.markdown("""
    This section provides the **official data standard** and a **tutorial** on how to use the tool.

    - The **iframe** below displays the official data standard from the IRW (Item Response Warehouse), which provides guidelines for structuring your data.
    - The **video tutorial** on the right explains how to use this tool step-by-step to process and map your data into the correct format.

    Please refer to both resources for a complete understanding of how to use this tool effectively.
    """)
    iframe_html = """
        <iframe src="https://datapages.github.io/irw/standard.html" width="800" height="600"></iframe>
    """

    # Create two columns
    col1, col2 = st.columns(2)

    # In the second column, embed a webpage with an iframe
    with col1:
        st.markdown(iframe_html, unsafe_allow_html=True)
    with col2:
        st.video("https://youtu.be/erezdWzk_60")  # Replace with any valid video URL

    st.session_state.documentation_page = False
    st.stop()


def highlight(cell, row_idx, col_idx):
    if start_row <= row_idx <= finish_row and start_col <= col_idx <= finish_col:
        return 'background-color: yellow'
    return ''
def process_row_as_column(data: pd.DataFrame, start_row: int, end_row: int, column_name="id") -> pd.DataFrame:
    """
    Checks if the selected data is a row instead of a column.
    If it's a row, transform it into a column and rename to `id`.

    Args:
        data (pd.DataFrame): The input DataFrame.
        start_row (int): Start row index (inclusive).
        end_row (int): End row index (exclusive).
        column_name (str): Name for the new column (default is "id").

    Returns:
        pd.DataFrame: Updated DataFrame with the row transformed into a column.
    """
    # Check if the selection is a line (row range) instead of a column
    # Check if the selection is a line (row range) instead of a column
    if end_row - start_row == 1:  # Single row selected
        row_as_column = data.iloc[start_row, :].values  # Extract the row as a list
        new_column = pd.DataFrame({column_name: row_as_column})  # Convert to a column DataFrame
        return new_column  # Return only the new column as the DataFrame

    # If it's not a single row, return the original data as it is
    return data


def broadcasting_with_ranges(original_df: pd.DataFrame, 
                             id_row_range: tuple, 
                             id_col_range: tuple, 
                             item_row_range: tuple, 
                             item_col_range: tuple):
    """
    Broadcasts IDs and items based on ranges in the original DataFrame and generates two DataFrames:
    1. Broadcasted DataFrame with `id` and `item`.
    2. Broadcasted DataFrame with `id_idx` and `item_idx`.

    Parameters:
    original_df (pd.DataFrame): The original dataset.
    id_row_range (tuple): Tuple with start and end row indices for IDs (inclusive).
    id_col_range (tuple): Tuple with start and end column indices for IDs (inclusive).
    item_row_range (tuple): Tuple with start and end row indices for items (inclusive).
    item_col_range (tuple): Tuple with start and end column indices for items (inclusive).

    Returns:
    tuple: (broadcasted_df, indices_df)
    """
    # Extract IDs and their indices
    ids = original_df.iloc[id_row_range[0]:id_row_range[1], id_col_range[0]:id_col_range[1]]
    ids_flat = ids.stack().reset_index(drop=True)
    id_indices = ids.stack().index

    # Extract items and their indices
    items = original_df.iloc[item_row_range[0]:item_row_range[1], item_col_range[0]:item_col_range[1]]
    items_flat = items.stack().reset_index(drop=True)
    item_indices = items.stack().index

    # Repeat IDs and items to create a Cartesian product
    repeated_ids = ids_flat.repeat(len(items_flat)).reset_index(drop=True)
    repeated_id_indices = pd.Index(id_indices.repeat(len(items_flat)))

    repeated_items = items_flat.values.tolist() * len(ids_flat)
    repeated_item_indices = pd.Index(item_indices.to_list() * len(ids_flat))

    # Create the final DataFrames
    broadcasted_df = pd.DataFrame({
        'id': repeated_ids,
        'item': repeated_items
    })

    indices_df = pd.DataFrame({
        'id_idx': repeated_id_indices.map(lambda x: (x[0], x[1])),  # Convert to tuples
        'item_idx': repeated_item_indices.map(lambda x: (x[0], x[1]))
    })

    return broadcasted_df, indices_df

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Dataset", "ID", "Item", "Resp", "Optional Data", "Review and Save", "Feedback"])

with tab1:
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file is not None:
        # Load the data
        if st.session_state.df is None:
            st.session_state.df = pd.read_csv(uploaded_file, header=None)
            st.rerun()
        # Create two columns for the buttons in tab2 and tab3
        else:
            # Create two columns for the buttons
            st.title("Extend DataFrame:")
            st.write("You can extend the dataframe by adding a column or a row.")
            col1, col2 = st.columns(2)
            
            # Add Column button
            if col1.button("Add Column", key="add_col"):
                # Create a new column of zeros at the beginning
                new_df = st.session_state.df.copy()
                # Get the current number of columns
                current_cols = len(new_df.columns)
                # Insert new column with 0s instead of range
                new_df.insert(0, current_cols, range(len(new_df)))
                # Reindex columns from 0 to n
                new_df.columns = range(len(new_df.columns))
                st.session_state.df = new_df
                st.dataframe(st.session_state.df)
                st.rerun()
                
            # Add Row button    
            if col2.button("Add Row", key="add_row"):
                # Create a new row of zeros at the beginning
                new_df = st.session_state.df.copy()
                new_row = pd.DataFrame([range(0, len(new_df.columns))])
                new_row.columns = new_df.columns
                st.session_state.df = pd.concat([new_row, new_df]).reset_index(drop=True)
                st.dataframe(st.session_state.df)
                st.rerun()

        st.write("DataFrame:")
        st.dataframe(st.session_state.df)




with tab2:
    st.header("Map IDs")
    if st.session_state.df is not None:
        data = st.session_state.df
        st.title("Interactive ID Mapping")
        st.write("Please specify the location of IDs in your dataset. Use the input boxes below to indicate the range of rows and columns.")

        
        # Input fields for range selection
        start_row = st.number_input("ID Start Row Number :", min_value=0, max_value=len(data), value=0)
        finish_row = st.number_input(f"ID Finish Row Number (Last row is {len(data) - 1}):", min_value=start_row, max_value=len(data), value=start_row)
        start_col = st.number_input("ID Start Column Number :", min_value=0, max_value=len(data.columns), value=0)
        finish_col = st.number_input(f"ID Finish Column Number (Last column is {len(data.columns) - 1}):", min_value=start_col, max_value=len(data.columns), value=start_col)
        

        # Adjusting for 0-indexing in Python
        start_row_idx = start_row
        finish_row_idx = finish_row + 1
        start_col_idx = start_col
        finish_col_idx = finish_col + 1

        # Highlight the selected area
        highlighted_data = data.style.apply(
            lambda row: [
                highlight(cell, row.name, col_idx) for col_idx, cell in enumerate(row)
            ], axis=1
        )
        
        st.subheader("Highlighted Dataset Preview")
        st.write(highlighted_data)
        
        # Confirm selection
        if st.button("Confirm Selection"):
            selected_ids = data.iloc[start_row_idx:finish_row_idx, start_col_idx:finish_col_idx]
            st.session_state.id_row_range = (start_row_idx,finish_row_idx)
            st.session_state.id_col_range = (start_col_idx,finish_col_idx)
            st.success("Selection Confirmed!")
            st.write("Here are the selected IDs:")
            st.write(selected_ids)
            # updated_df = process_row_as_column(selected_ids, start_row=0, end_row=1)
            selected_ids.rename(columns={selected_ids.columns[0]: "id"}, inplace=True)
            st.session_state.irw_dataframe = selected_ids
            st.rerun()
    else:
        st.write("No data uploaded.")

with tab3:
    st.header("Map items")
    if st.session_state.df is not None:
        data = st.session_state.df
        st.title("Interactive item Mapping")
        st.write("Please specify the location of items in your dataset. Use the input boxes below to indicate the range of rows and columns.")

        
        # Input fields for range selection
        start_row = st.number_input("Item Start Row Number:", min_value=0, max_value=len(data), value=0)
        finish_row = st.number_input(f"Item Finish Row Number: (Last row is {len(data) - 1})", min_value=start_row, max_value=len(data), value=start_row)
        start_col = st.number_input("Item Start Column Number:", min_value=0, max_value=len(data.columns), value=0)
        finish_col = st.number_input(f"Item Finish Column Number: (Last column is {len(data.columns) - 1})", min_value=start_col, max_value=len(data.columns), value=start_col)
        

        # Adjusting for 0-indexing in Python
        start_row_idx = start_row
        finish_row_idx = finish_row + 1
        start_col_idx = start_col
        finish_col_idx = finish_col + 1

        # Highlight the selected area
        highlighted_data = data.style.apply(
            lambda row: [
                highlight(cell, row.name, col_idx) for col_idx, cell in enumerate(row)
            ], axis=1
        )
        
        st.subheader("Highlighted Dataset Preview")
        st.write(highlighted_data)
        
        # Confirm selection
        if st.button("Confirm Items Selection"):
            selected_items = data.iloc[start_row_idx:finish_row_idx, start_col_idx:finish_col_idx]
            st.success("Selection Confirmed!")
            st.write("Here are the selected items:")
            st.write(selected_items)
            st.session_state.item_row_range = (start_row_idx,finish_row_idx)
            st.session_state.item_col_range = (start_col_idx,finish_col_idx)
            items = process_row_as_column(selected_items, start_row=0, end_row=1, column_name="item")
            st.write(items)
            updated_df, indices_df = broadcasting_with_ranges(st.session_state.df, st.session_state.id_row_range, st.session_state.id_col_range, 
                                                  st.session_state.item_row_range, st.session_state.item_col_range)
            st.session_state.irw_dataframe = updated_df    
            st.session_state.indices_df = indices_df      
            st.rerun()
    else:
        st.write("No data uploaded.")

def map_resp(original_df, indices_df, id_orientation, item_orientation):
    # Extract values based on the intersections
    resp_values = []

    for id_idx, item_idx in zip(indices_df['id_idx'], indices_df['item_idx']):
        # Handle the id_idx based on the id_orientation (row or column)
        if id_orientation == "Row":
            row_idx = id_idx[0]  # Row position from id
            col_idx = item_idx[1]  # Column position from item
        else:  # id_orientation == "Column"
            row_idx = item_idx[0]  # Row position from item
            col_idx = id_idx[1]  # Column position from id
        
        # Convert indices to integers
        row_idx = int(row_idx)
        col_idx = int(col_idx)
        
        # Extract the value from the original dataframe at the given position
        try:
            resp = original_df.iat[row_idx, col_idx]
            resp_values.append(resp)
        except IndexError as e:
            st.error(f"Index error at position ({row_idx}, {col_idx}). Please check your data layout selection.")
            raise e

    # Create the 'resp' DataFrame
    resp_df = pd.DataFrame({'resp': resp_values})
    return resp_df

with tab4:
    if not st.session_state.indices_df.empty:
        st.markdown("""
        ### Select Your Data Layout

        Please choose the layout that matches your data structure:
        """)

        # Create example DataFrames for visualization
        example_1 = pd.DataFrame({
            'ID': ['Student1', 'Student2', 'Student3'],
            'Item1': [1, 0, 1],
            'Item2': [0, 1, 1],
            'Item3': [1, 1, 0]
        })

        example_2 = pd.DataFrame({
            'Items': ['Item1', 'Item2', 'Item3'],
            'Student1': [1, 0, 1],
            'Student2': [0, 1, 1],
            'Student3': [1, 1, 0]
        })

        # Create two columns for the layout options
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Layout Option 1")
            st.markdown("IDs as rows, Items as columns:")
            st.dataframe(example_1)
            option_1_selected = st.button("Select Layout 1")

        with col2:
            st.subheader("Layout Option 2")
            st.markdown("Items as rows, IDs as columns:")
            st.dataframe(example_2)
            option_2_selected = st.button("Select Layout 2")

        # Handle layout selection
        if option_1_selected:
            id_orientation = "Row"
            item_orientation = "Column"
            resp_df = map_resp(st.session_state.df, st.session_state.indices_df, id_orientation, item_orientation)
            st.session_state.irw_dataframe = pd.concat([st.session_state.irw_dataframe.reset_index(drop=True), 
                                                      resp_df.reset_index(drop=True)], axis=1)
            st.success("Layout 1 selected and responses mapped!")
            st.rerun()

        if option_2_selected:
            id_orientation = "Column"
            item_orientation = "Row"
            resp_df = map_resp(st.session_state.df, st.session_state.indices_df, id_orientation, item_orientation)
            st.session_state.irw_dataframe = pd.concat([st.session_state.irw_dataframe.reset_index(drop=True), 
                                                      resp_df.reset_index(drop=True)], axis=1)
            st.success("Layout 2 selected and responses mapped!")
            st.rerun()
    else:
        st.write("Please complete the ids and items mapping")

with tab5:

    st.markdown("""
    ### Optional Data (Under Construction)

    The **Optional Data** section is currently under construction.  
    Possible mappings include:

    - `rt`  
    - `date`  
    - `qmatrix`  
    - `rater`  
    - `wave`  
    - `treat`  

    Stay tuned for updates as we continue to enhance this feature.
    """)

with tab6:
    st.title("Review and Save")

    # Divide the page into two columns
    left_col, right_col = st.columns(2)

    # Left column: Review the dataset
    with left_col:
        st.subheader("Review Your Created Dataset")
        st.write("Below is the dataset you have created. Please review it before downloading.")
        st.dataframe(st.session_state.irw_dataframe)

    # Right column: Download the dataset
    with right_col:
        st.subheader("Download Your Dataset")
        st.write("Click the button below to download the dataset in CSV format.")
        
        # Convert DataFrame to CSV
        csv = st.session_state.irw_dataframe.to_csv(index=False).encode('utf-8')
        
        # Download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="created_dataset.csv",
            mime="text/csv"
        )
with tab7:
    # Tab 7: Feedback Page
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
        st.session_state.feedback_data_url = st.text_input("Link to your dataset", placeholder="Paste the dataset link here")
        
        # Input for detailed comment
        st.session_state.feedback_comments = st.text_area(
            "Detailed Comment", 
            placeholder="Explain how you planned to treat the data and why it wasn't possible using the tool"
        )
        # Input for detailed comment
        st.session_state.contact_info = st.text_area(
            "Contact Info", 
            placeholder="Please provide a contact information in case we need to get further clarifications (e.g) John Doe, johndoe@gmail.com"
        )
    # For "Yes" response, display a thank-you message
    elif st.session_state.feedback_response == "Yes":
        st.success("We're glad the tool met your needs! Thank you for using it.")
        # Button to submit feedback
    if st.button("Submit Feedback"):
        if st.session_state.feedback_response == "No" and not (st.session_state.feedback_data_url and st.session_state.feedback_comments):
            st.error("Please fill in both the dataset link and detailed comments.")
        else:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read()

            user_data = [st.session_state.feedback_nps, st.session_state.feedback_comments, st.session_state.feedback_data_url, st.session_state.contact_info]
            df.loc[len(df)] = user_data

            conn.update(data=df)

            st.success("Thank you for your feedback! We'll review it and keep improving the tool.")



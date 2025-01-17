# import streamlit as st
# import pandas as pd

# # Define expected columns
# expected_columns = {
#     "Mandatory": ["id", "item", "resp"],
#     "Optional": ["rt", "date", "qmatrix", "rater", "wave", "treat"],
# }

# # Helper functions for data treatment
# def merge_columns(data, selected_columns, new_column_name):
#     data[new_column_name] = data[selected_columns].astype(str).agg("_".join, axis=1)
#     return data

# def calculate_score(data, selected_columns, score_column_name):
#     data[score_column_name] = data[selected_columns].sum(axis=1)
#     return data

# def fix_date_format(data, selected_column, new_column_name, date_format="%Y-%m-%d"):
#     data[new_column_name] = pd.to_datetime(data[selected_column], errors="coerce").dt.strftime(date_format)
#     return data

# def convert_rt_to_seconds(data, selected_column, new_column_name):
#     data[new_column_name] = pd.to_numeric(data[selected_column], errors="coerce") / 1000
#     return data

# def create_qmatrix(data, selected_columns, new_column_name):
#     data[new_column_name] = data[selected_columns].apply(lambda row: " | ".join(row.dropna()), axis=1)
#     return data

# # Streamlit layout
# st.title("Dataset Standardization and Transformation App")
# st.write("Upload your dataset, map columns, and apply transformations to standardize your data.")

# # File upload
# uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# if uploaded_file:
#     try:
#         # Load data
#         data = pd.read_csv(uploaded_file)
#         st.write("Dataset Preview:")
#         st.dataframe(data.head())

#         # Column mapping
#         st.subheader("Map Columns")
#         mappings = {}

#         # Handle mandatory columns first
#         for col in expected_columns["Mandatory"]:
#             st.markdown(f"### Map for `{col}`")
#             if col == "id" or col == "item":
#                 # Option to select columns as either row names or as columns
#                 selection_type = st.radio(
#                     f"Is `{col}` a column header or a column?",
#                     ("Column Header", "Column")
#                 )

#                 if selection_type == "Column Header":
#                     headers = [header for header in data.columns]
#                     selected_column = st.multiselect(f"Select header(s) for `{col}`", options=headers)
#                     mappings[col] = [selected_column]
#                 elif selection_type == "Column":
#                     selected_columns = st.multiselect(
#                         f"Select column(s) for `{col}`", options=data.columns
#                     )
#                     mappings[col] = selected_columns

#                 if col == "id":
#                                         # Handle missing ID
#                     if "id" not in mappings or not mappings["id"]:
#                         st.warning(
#                             "No column mapped for `id`. The row index will be used as `id`."
#                         )
#                         data["id"] = data.index
#                         mappings["id"] = ["id"]
#             else:
#                 selected_columns = st.multiselect(
#                     f"Select columns for `{col}`", options=data.columns
#                 )
#                 mappings[col] = selected_columns



#         # Data treatment options
#         st.subheader("Data Treatment")
#         selected_action = st.selectbox(
#             "Select an action to treat the data:",
#             [
#                 "None",
#                 "Merge Columns",
#                 "Calculate Score",
#                 "Fix Date Format",
#                 "Convert RT to Seconds",
#                 "Create QMatrix",
#             ],
#         )

#         if selected_action != "None":
#             if selected_action == "Merge Columns":
#                 columns_to_merge = st.multiselect(
#                     "Select columns to merge", options=data.columns
#                 )
#                 new_column_name = st.text_input("Enter the new column name")
#                 if st.button("Apply Merge"):
#                     data = merge_columns(data, columns_to_merge, new_column_name)
#                     st.success(f"Columns merged into `{new_column_name}`.")
#             elif selected_action == "Calculate Score":
#                 columns_for_score = st.multiselect(
#                     "Select columns to calculate score", options=data.columns
#                 )
#                 score_column_name = st.text_input("Enter the new score column name")
#                 if st.button("Calculate Score"):
#                     data = calculate_score(data, columns_for_score, score_column_name)
#                     st.success(f"Score calculated in `{score_column_name}`.")
#             elif selected_action == "Fix Date Format":
#                 selected_column = st.selectbox(
#                     "Select the date column", options=data.columns
#                 )
#                 new_column_name = st.text_input("Enter the new column name")
#                 date_format = st.text_input(
#                     "Enter the date format (default: %Y-%m-%d)", value="%Y-%m-%d"
#                 )
#                 if st.button("Fix Date Format"):
#                     data = fix_date_format(data, selected_column, new_column_name, date_format)
#                     st.success(f"Date format fixed in `{new_column_name}`.")
#             elif selected_action == "Convert RT to Seconds":
#                 selected_column = st.selectbox(
#                     "Select the RT column", options=data.columns
#                 )
#                 new_column_name = st.text_input("Enter the new column name")
#                 if st.button("Convert RT"):
#                     data = convert_rt_to_seconds(data, selected_column, new_column_name)
#                     st.success(f"RT converted to seconds in `{new_column_name}`.")
#             elif selected_action == "Create QMatrix":
#                 columns_for_qmatrix = st.multiselect(
#                     "Select columns to create QMatrix", options=data.columns
#                 )
#                 new_column_name = st.text_input("Enter the new QMatrix column name")
#                 if st.button("Create QMatrix"):
#                     data = create_qmatrix(data, columns_for_qmatrix, new_column_name)
#                     st.success(f"QMatrix created in `{new_column_name}`.")

#             # Display updated DataFrame
#             st.write("Updated Dataset:")
#             st.dataframe(mappings)

#         # Download button
#         st.download_button(
#             "Download Updated Dataset",
#             data.to_csv(index=False),
#             file_name="updated_dataset.csv",
#             mime="text/csv",
#         )

#     except Exception as e:
#         st.error(f"Error processing the file: {e}")
# else:
#     st.info("Please upload a CSV file to begin.")

import streamlit as st
import pandas as pd

# Title
st.title("IRW Data Transformation App")

# Step 1: File Upload
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file is not None:
    # Load the data
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded DataFrame:")
    st.dataframe(df)

    # Step 2: Ask about ID
    st.subheader("Map ID (unique identifier)")
    id_input_type = st.radio(
        "Is the ID information in:",
        options=["A specific column", "The headers (column names)"]
    )
    
    if id_input_type == "A specific column":
        id_column = st.selectbox(
            "Select the ID column (default is the index if not provided):",
            options=[None] + list(df.columns),
            index=0
        )
        if id_column is None:
            st.warning("ID column not selected. Using the DataFrame index as ID.")
            df["temp_id"] = df.index
            id_column = "temp_id"
    else:
        st.warning("The ID is expected to be in the column headers (row index used as values).")
        id_headers = [col for col in df.columns]
        id_column = None  # This will be handled during transformation.

    # Step 3: Ask about Items
    st.subheader("Map Items")
    item_input_type = st.radio(
        "Is the item information in:",
        options=["A specific column", "The headers (column names)"]
    )

    if item_input_type == "A specific column":
        item_column = st.selectbox(
            "Select the Item column (default is the index if not provided):",
            options=[None] + list(df.columns),
            index=0
        )
        if item_column is None:
            st.warning("Item column not selected. Using the DataFrame index as Item.")
            df["temp_item"] = df.index
            item_column = "temp_item"
    else:
        item_headers = st.multiselect(
            "Select the headers that contain item information:",
            options=df.columns,
            default=df.columns.tolist()
        )
        if not item_headers:
            st.error("You must select at least one header for the item information.")
            st.stop()

    # Step 4: Transform the DataFrame
    st.subheader("Transformed Data")

    if id_input_type == "A specific column" and item_input_type == "A specific column":
        # Both ID and Item are specific columns
        transformed_df = df[[id_column, item_column]].rename(
            columns={id_column: "id", item_column: "item"}
        )
        transformed_df = pd.melt(
            transformed_df, id_vars=["id"], var_name="item", value_name="resp"
        )

    elif id_input_type == "A specific column" and item_input_type == "The headers (column names)":
        # ID is a column, Items are in headers
        transformed_df = pd.melt(
            df,
            id_vars=[id_column],
            value_vars=item_headers,
            var_name="item",
            value_name="resp"
        ).rename(columns={id_column: "id"})

    elif id_input_type == "The headers (column names)" and item_input_type == "A specific column":
        # Items are in a column, IDs are in headers
        transformed_df = pd.melt(
            df.set_index(item_column),
            var_name="id",
            value_name="resp",
            ignore_index=False
        ).reset_index().rename(columns={"index": "item"})

    else:
        # Both ID and Items are in headers
        transformed_df = pd.melt(
            df,
            var_name="id",
            value_name="resp",
            ignore_index=False
        ).reset_index().rename(columns={"index": "item"})

    # Drop NaN responses
    transformed_df.dropna(subset=["resp"], inplace=True)

    # Show the transformed DataFrame
    st.write(transformed_df)
    st.write("Transformed data contains:")
    st.write(f"- **{len(transformed_df['id'].unique())} unique IDs**")
    st.write(f"- **{len(transformed_df['item'].unique())} unique items**")

    # Step 5: Transformation Options
    st.subheader("Transformation Options")

    # Dummy transformations
    transform_option = st.selectbox(
        "Choose a transformation to apply to the data:",
        options=[
            "None",
            "Normalize a column (values between 0 and 1)",
            "Change date format (e.g., YYYY-MM-DD to DD/MM/YYYY)",
            "Round numeric columns",
            "Custom transformation (for prototype)"
        ]
    )

    def normalize_column(df, column):
        # Min-Max normalization formula
        min_val = df[column].min()
        max_val = df[column].max()
        
        # Apply the normalization
        df[column] = (df[column] - min_val) / (max_val - min_val)
        return df

    if transform_option == "Normalize a column (values between 0 and 1)":
        column_to_normalize = st.selectbox("Select the column to normalize:", options=transformed_df.columns)
        if column_to_normalize:
            transformed_df = normalize_column(transformed_df, column_to_normalize)
            st.write(f"Normalized column: **{column_to_normalize}**")
            st.dataframe(transformed_df)

    elif transform_option == "Change date format (e.g., YYYY-MM-DD to DD/MM/YYYY)":
        date_column = st.selectbox("Select the column with dates:", options=transformed_df.columns)
        if date_column:
            # Dummy implementation, assuming valid dates
            transformed_df[date_column] = pd.to_datetime(transformed_df[date_column]).dt.strftime("%d/%m/%Y")
            st.write(f"Changed date format for column: **{date_column}**")
            st.dataframe(transformed_df)

    elif transform_option == "Round numeric columns":
        numeric_columns = transformed_df.select_dtypes(include="number").columns
        if numeric_columns.any():
            decimal_places = st.slider("Select number of decimal places:", min_value=0, max_value=5, value=2)
            transformed_df[numeric_columns] = transformed_df[numeric_columns].round(decimal_places)
            st.write(f"Rounded numeric columns to {decimal_places} decimal places")
            st.dataframe(transformed_df)
        else:
            st.warning("No numeric columns found to round.")

    elif transform_option == "Custom transformation (for prototype)":
        st.info("This is a placeholder for a custom transformation.")
        st.write("Imagine this does something amazing!")

    else:
        st.write("No transformation selected.")

    # Download button
    st.download_button(
        "Download Updated Dataset",
        df.to_csv(index=False),
        file_name="processed_dataset.csv",
        mime="text/csv",
    )

    # Feedback Section
    st.subheader("Feedback")

    # Ask if the user was able to complete their task
    task_completed = st.radio(
        "Were you able to do everything you wanted with the data?",
        options=["Yes", "No"]
    )

    if task_completed == "No":
        # Ask the user to describe what they wanted to do
        st.write("Please describe what you were trying to do:")
        user_description = st.text_area("Describe the task you wanted to complete:", height=150)
        
        # Ask the user to provide a link to the data (if available)
        st.write("If possible, please share a link to the dataset or provide more details:")
        data_link = st.text_input("Data link (e.g., Google Drive, Dropbox, etc.):")
        
        # Submit button for feedback
        if st.button("Submit Feedback"):
            if user_description and data_link:
                st.success("Thank you for your feedback! We'll work on improving the app.")
            else:
                st.warning("Please provide both a description and a link to the data.")
    else:
        st.write("Great! We're glad you were able to process the data as needed.")

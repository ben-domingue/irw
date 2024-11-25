## Load the 'redivis' package (ensure it's installed)
## If it's not installed, you can do that with: devtools::install_github("redivis/redivis-r", ref="main")

## Get a sample dataset from the Redivis platform
## Access the user "datapages" on Redivis
dataset <- redivis::user("datapages")$dataset("item_response_warehouse", version = "v4.0")

# Extract the specific table named "kim2023" from the dataset
## Then convert this table into a data frame for easier data manipulation
df <- dataset$table("kim2023")$to_data_frame()

## Now 'df' contains the data from the "kim2023" table as a data frame
## You can proceed to analyze 'df' or perform data operations.

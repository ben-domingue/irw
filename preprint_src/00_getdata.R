## Load the 'redivis' package (ensure it's installed)
## If it's not installed, you can do that with: devtools::install_github("redivis/redivis-r", ref="main")

## Get a sample dataset from the Redivis platform
## Access the user "datapages" on Redivis
dataset <- redivis::user("datapages")$dataset("item_response_warehouse")

# Extract the specific table named "gilbert_meta_2" from the dataset
## Then convert this table into a data frame for easier data manipulation
df <- dataset$table("gilbert_meta_2")$to_data_frame()

## Now 'df' contains the data from the "gilbert_meta_2" table as a data frame
## You can proceed to analyze 'df' or perform data operations.

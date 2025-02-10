library(redivis)
library(tibble)

# fetch all tables
dataset <- redivis::organization("datapages")$dataset("Item Response Warehouse")
dataset_tables <- dataset$list_tables()


# Extract table names and variables, storing variables as concatenated strings
table_vars_df <- tibble(
  table_name = sapply(dataset_tables, function(table) table$name),
  variables = sapply(dataset_tables, function(table) {
    var_list <- table$list_variables()
    paste(sapply(var_list, function(v) v$name), collapse = ", ")  # Concatenate variables
  })
)

save(table_vars_df,file="table_vars_df.Rdata")

# Read the new dataset
data <- read.csv('Non_parametric_mixture_modeling.csv')

# Retain only the specified columns
filtered_data <- data[, c('subject', 'version', 'rt', 'acc')]

# Rename the columns
colnames(filtered_data) <- c('id', 'item', 'rt', 'resp')

# Sort the dataset by 'item' column
sorted_data <- filtered_data[order(filtered_data$item), ]

# Calculate the frequency count of each 'id'
id_frequency <- table(sorted_data$id)

# Create a vector of new 'id' values based on frequency counts
new_ids <- rep(names(id_frequency), times = id_frequency)

# Update the 'id' column in the dataset with new 'id' values
sorted_data$id <- as.integer(new_ids)

#rename
df <- sorted_data

# Save the cleaned and sorted dataset to a Rdata file
save(df, file = 'Non_parametric_mixture_modeling_exp1_Cleaned.RData')

# Set the variable not_data to the string "metadata"
not_data <- "metadata"

# Retrieve the dataset named "Item Response Warehouse" from the Redivis organization "datapages"
dataset <- redivis::organization("datapages")$
    dataset("Item Response Warehouse")

# List the tables available in the dataset
dataset_tables <- dataset$list_tables()

# Print the number of tables in the dataset
print(length(dataset_tables))

# Extract the names of the tables into a vector using sapply
names <- sapply(dataset_tables, function(x) x$name)

# Find indices of tables that contain the string "metadata"
ii <- grep("metadata", names)

# Assign names to the dataset_tables object for easier reference
names(dataset_tables) <- names

# If any tables contain "metadata", remove them from dataset_tables
if (length(ii) > 0) dataset_tables <- dataset_tables[-ii]   

# Define a function that retrieves the variables from each table
f <- function(table) table$list_variables()

# Apply the function to each table in dataset_tables to get their variables
nms <- lapply(dataset_tables, f)

# Define a function to check if a table contains a variable named "rt"
f <- function(x) {
    nm <- sapply(x, function(x) x$name)  # Extract names of variables
    "rt" %in% nm  # Check if "rt" is among the variable names
}

# Apply the function to the list of variable names to identify tables containing "rt"
test <- sapply(nms, f)

# Select only the tables that contain the "rt" variable
rt_data <- dataset_tables[test]

# Define a processing function for each table containing "rt"
proc <- function(table) {
    # Convert the table to a data frame
    df <- table$to_data_frame()

    # Replace "NA" strings with actual NA values in 'resp' and 'rt' columns
    df$resp <- ifelse(df$resp == "NA", NA, df$resp)
    df$rt <- ifelse(df$rt == "NA", NA, df$rt)

    # Remove rows where 'resp' or 'rt' is NA
    df <- df[!is.na(df$resp), ]
    df <- df[!is.na(df$rt), ]

    # Convert 'rt' to numeric and filter for values > 0 and < 30 minutes (1800 seconds)
    z <- as.numeric(df$rt)
    z <- z[z > 0 & z < 60 * 30]

    # Take the logarithm of the filtered 'rt' values
    z <- log(z)

    # Standardize the values to have mean 0 and standard deviation 1
    z <- (z - mean(z)) / sd(z)

    # Generate a Q-Q plot data
    qq <- qqnorm(z, plot.it = FALSE)
    qq <- cbind(qq$x, qq$y)  # Combine theoretical and sample quantiles
    qq <- qq[order(qq[, 1]), ]  # Sort by theoretical quantiles

    # Return a subset of the Q-Q plot data with 500 points evenly spaced
    qq[(seq(1, nrow(qq), length.out = 500)), ]
}

# Apply the 'proc' function to each table containing 'rt' and store the results in 'dens'
dens <- lapply(rt_data, proc)
##save(dens,file="/tmp/dens.Rdata")

# Create a PDF file to save the Q-Q plots
pdf("~/Dropbox/Apps/Overleaf/IRW/rt.pdf", width = 3, height = 2.2)

# Set color with transparency for the lines to be plotted
cc <- col2rgb("red")
cc <- rgb(cc[1], cc[2], cc[3], max = 255, alpha = 45)  # Red color with alpha

# Set graphical parameters for the plot layout
par(mgp = c(2, 1, 0), mar = c(3, 3, .1, .1))

# Initialize an empty plot with specified x and y limits
plot(NULL, xlim = c(-6, 6), ylim = c(-6, 6),
     xlab = "theoretical quantiles", ylab = "sample quantiles")

# Draw a reference line (y=x) for comparison
abline(0, 1, lwd = 2)

# Loop through density data and add lines for each density distribution
for (i in 1:length(dens)) lines(dens[[i]], col = cc)

# Close the PDF device
dev.off()

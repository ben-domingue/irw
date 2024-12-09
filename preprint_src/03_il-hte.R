# Load the dataset from the redivis package
dataset <- redivis::organization("datapages")$dataset("Item Response Warehouse")

# List all tables in the dataset
dataset_tables <- dataset$list_tables()

# Rename the tables using their names for easier access
names(dataset_tables) <- sapply(dataset_tables, function(x) x$name)

# Define a function to list variables for a given table
f <- function(table) table$list_variables()

# Apply the function to all tables to get a list of variable names
nms <- lapply(dataset_tables, f)

# Define a function to check if "treat" is among the variable names
f <- function(x) {
    nm <- sapply(x, function(x) x$name)  # Extract names of variables
    "treat" %in% nm  # Check if "treat" is in the names
}

# Apply the function to identify tables that contain the "treat" variable
test <- sapply(nms, f)

# Filter the dataset tables to only include those that contain "treat"
rct_tables <- dataset_tables[test]

# Define a function to perform item-level Harmonic Treatment Effect (IL-HTE) analysis
il_hte <- function(tab) {
    nm <- tab$name  # Get the name of the current table
    df <- tab$to_data_frame()  # Convert the table to a data frame
    df$resp <- as.numeric(df$resp)  # Ensure the response variable is numeric
    print(nm)  # Print the name of the table
    print(head(df))  # Display the first few rows of the data frame
    
    # Filter for only wave 1 if the "wave" variable exists
    if ("wave" %in% names(df)) df <- df[df$wave == 1,]

    ## Downsample if there are more than 5000 unique IDs
    ids <- unique(df$id)
    if (length(ids) > 5000) {
        ids <- sample(ids, 5000)  # Randomly sample to reduce to 5000
        df <- df[df$id %in% ids,]  # Filter the data frame to keep only sampled IDs
    }
    
    ## Only keep dichotomous responses (0/1)
    f <- function(x) length(unique(x$resp[!is.na(x$resp)]))  # Function to check unique responses
    ll <- split(df, df$item)  # Split data frame by item
    nn <- sapply(ll, f)  # Count unique responses per item
    nms <- names(nn)[nn == 2]  # Identify items with exactly 2 unique responses
    
    # Filter the data frame to include only items with 2 unique responses
    if (length(nms) > 2) df <- df[df$item %in% nms,] else return(NULL)  # Return NULL if not enough items
    
    # Fit a 1PL IL-HTE model using lme4 package
    m <- lme4::glmer(resp ~ treat + (1 | id) + (treat | item), df, family = 'binomial') 
    print(summary(m))  # Print the model summary
    
    # Return the table name, random effects, and fixed effects from the model
    list(nm, lme4::ranef(m), lme4::fixef(m))
}

# Set seed for reproducibility
set.seed(1013010)

# Apply the IL-HTE function to the first 10 RCT tables
L <- lapply(rct_tables[1:10], il_hte)

# Remove NULL results from the results list
L <- L[!sapply(L, is.null)]
##save(L,file="ilhte.Rdata")

# Generate a figure of treatment effects, similar to the result in provided link
pdf("~/Dropbox/Apps/Overleaf/IRW/ilhte.pdf", width = 4, height = 2.2)

# order things
te <- sapply(L, function(x) x[[3]][2])  # Overall treatment effect
L<-L[order(te)]

# Extract random effects and treatment effect estimates
est <- sapply(L, function(x) x[[2]]$item[, 2])  # Item-level effects
treatment.effect <- sapply(L, function(x) x[[3]][2])  # Overall treatment effect

# Set up plot parameters
par(mgp = c(2, 1, 0), mar = c(3, 10, 1, 1))  # Margins and spacing adjustments

# Create an empty plot
plot(NULL, xlim = c(-1, 2.5), ylim = c(1, length(L)), yaxt = 'n', ylab = '', xlab = "Item-level treatment effects")
abline(v = 0, col = 'gray')  # Add a vertical line at x = 0 for reference

# Plot treatment effects for each item
for (i in 1:length(L)) {
    xv <- est[[i]] + treatment.effect[i]  # Calculate adjusted treatment effects
    points(xv, rep(i, length(xv)), pch = 19, cex = .5)  # Add points to the plot
    points(treatment.effect[i],i,col=rgb(0.93,0,0,alpha=.4),cex=1.5,pch=19)
    mtext(side = 2, line = 0.2, at = i, L[[i]][[1]], cex = .8, las = 2)  # Add item names to y-axis
}

# Close the PDF device
dev.off()

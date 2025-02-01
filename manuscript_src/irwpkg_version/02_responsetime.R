# Select only the tables that contain the "rt" variable
rt_data <- irwpkg::irw_filter(has_rt=TRUE)

# Define a processing function for each table containing "rt"
proc <- function(table) {
    # Convert the table to a data frame
    df <- irwpkg::irw_fetch(table)
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
dens <- lapply(rt_data[1:3], proc)
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

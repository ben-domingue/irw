## Preparing data for analysis
# Create a new variable 'item' in the data frame 'df' by concatenating "item_" 
# in front of the existing values in the 'item' column
df$item <- paste("item_", df$item, sep = "")

## Reformatting to typical response matrix format
# Load the 'irw' library, which provides tools for working with item response data
library(irw)

# Convert the long format data frame 'df' into a response matrix format suitable for analysis
resp <- irw::long2resp(df)

# Remove the 'id' column from the response matrix, as it's typically not needed for subsequent analyses
resp$id <- NULL

## Cronbach's alpha
# Calculate Cronbach's alpha to assess the internal consistency reliability of the response matrix
psych::alpha(resp)

## Dimensionality analysis
# Perform a dimensionality analysis using the Paran method to determine the number of underlying dimensions in the data
paran::paran(resp)

## Basic factor analysis
# Conduct factor analysis with the covariance matrix of the response matrix
# Here, instruct to extract 3 factors
psych::fa(cov(resp), nfactors = 3)

## Basic unidimensional IRT analysis
# Perform a unidimensional Item Response Theory analysis using the Rasch model on the response matrix
mirt::mirt(resp, 1, "Rasch")

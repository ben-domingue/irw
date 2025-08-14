setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

df <- read_csv("study1data.csv")
# Check if all rows with equal values of 'self_condition' and 'peer_condition'
all(df$self_condition == df$peer_condition, na.rm = TRUE) # Returned TRUE

# Convert to long format
df_long <- df %>%
  mutate(id=row_number()) %>%
  pivot_longer(cols = starts_with("self_BFI_"),
               names_to = "item",
               values_to = "resp") %>%
  select(id, itemcov_format = self_condition, item, resp)

write_csv(df_long, "bfi2_zhang_2025.csv")

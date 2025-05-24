library(tidyverse)
library(haven)

df <- read_sav('MPIS_ Validation Data.sav')

# Standardize column names
names(df) <- tolower(names(df))

# Covert to long format
df_long <- df %>%
  mutate(cov_injustice = injustice) %>%
pivot_longer(cols = starts_with("in_"),
             names_to = "item",
             values_to = "resp") %>%
  select(id, item, resp, cov_injustice)

# Export data
write.csv(df_long, "perceived_injustice_mourin.csv", row.names = FALSE)

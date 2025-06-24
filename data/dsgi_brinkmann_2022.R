library(readxl)
library(tidyr)

df <- read_xlsx("Final CFA data.xlsx")

df$id <- seq(1, nrow(df))

df <- df %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = 'resp')

write.csv(df, "dsgi_brinkmann_2022.csv", row.names = FALSE)

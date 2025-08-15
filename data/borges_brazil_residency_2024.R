library(tidyr)
library(dplyr)

df1 <- read.csv("Dataset 1. Raw responses of 3,223 applicants to 120 multiple-choice items of computer-based testing for residency in a hospital in Brazil", check.names = FALSE)
df1a <- read.csv("Dataset 3. Correct options for 120 items of the computer-based testing",check.names = FALSE)

df1 <- df1 %>%
  rename(id = ID) %>%
  select(-CAD) %>%
  pivot_longer(-id, names_to = "item", values_to = "resp_raw")

df1a <- df1a %>%
  pivot_longer(cols = everything(), names_to = "item", values_to = "corr_resp")

scored1 <- df1 %>%
  left_join(df1a, by = "item") %>%
  mutate(resp = ifelse(resp_raw == corr_resp, 1, 0))

scored1 <- scored1 %>%
  select(-corr_resp)


df2 <- read.csv("Dataset 2. Raw responses of 1, 994 applicants to 100 multiple choice items of paper-based testing for residency in a hospital in Brazil", check.names = FALSE)
df2a <- read.csv("Dataset 4. Correct options or 100 items for paper-based testing",check.names = FALSE)

df2 <- df2 %>%
  rename(id = ID) %>%
  select(-CADERNO) %>%
  pivot_longer(-id, names_to = "item", values_to = "resp_raw")

df2a <- df2a %>%
  pivot_longer(cols = everything(), names_to = "item", values_to = "corr_resp")

scored2 <- df2 %>%
  left_join(df2a, by = "item") %>%
  mutate(resp = ifelse(resp_raw == corr_resp, 1, 0))

scored2 <- scored2 %>%
  select(-corr_resp)


write.csv(scored1, "borges_brazil_residency_2024_cbt.csv", row.names = FALSE)
write.csv(scored2, "borges_brazil_residency_2024_pbt.csv", row.names = FALSE)

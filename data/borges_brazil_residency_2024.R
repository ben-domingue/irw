# Borges et al. (2024), residency-exam CBT (2020) and PBT (2022), Ribeirao Preto.
# Source: https://doi.org/10.7910/DVN/YJP1ZM (CC0). Ingested in #1020; X handling #1366, #2513.
#
# resp_raw keeps the option exactly as recorded, including the two non-option
# codes the deposit uses: "X" (CBT 1,914 cells, PBT 54) and "_" (PBT only, 79).
# Neither is documented in the deposit or the paper (doi:10.3352/jeehp.2024.21.32);
# they read as blank/omitted or invalid marks. Both score resp = 0, as a blank
# does on the exam, and both stay in resp_raw so an omission remains
# distinguishable from a wrong option (IRW standard, resp_raw: "including
# whatever codes the original source used for an omitted or unreadable
# response"; same convention as the ENEM "." and "*" codes in
# data/nominal/enem.R). Until #2513 this script set "X" to NA in resp_raw, and
# the published tables disagreed with each other: the CBT table (irw 459) carries
# the literal string "NA" for its 1,914 X cells, while the PBT table carries the
# raw option in a column named `text` (not `resp_raw`) with X and "_" intact.
# resp is identical to this script's output in both (checked 2026-09-28).

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

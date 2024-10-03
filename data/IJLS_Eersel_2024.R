library(dplyr)
library(tidyr)

df <- read.table("IJLS [dataset].dat", header = TRUE, sep = "\t")

df <- df %>%
  rename(id = ID)

# --------- IJLS reactions
df_ijls <- df %>%
  select(id, contains("IJLS")) %>%
  pivot_longer(cols = IJLS_1:IJLS_9_T2,
               names_to = "item",
               values_to = "resp")
df_ijls$wave <- 0
df_ijls$wave[grepl("T2", df_ijls$item)] <- 1
df_ijls$item[grepl("T2", df_ijls$item)] <- substr(df_ijls$item[grepl("T2", df_ijls$item)], 1, 6)

df_ijls <- df_ijls %>%
  select(id, item, wave, resp) %>%
  filter(!is.na(resp))

# --------- Optimism
df_lot <- df %>%
  select(id, contains("Lot"), -matches("Sum|sum")) %>%
  pivot_longer(cols = Lot_r_1:Lot_r_6,
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))


# --------- Depression
df_d <- df %>%
  select(id, D1:D7) %>%
  pivot_longer(cols = D1:D7,
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

# --------- Anxiety
df_a <- df %>%
  select(id, A1:A7) %>%
  pivot_longer(cols = A1:A7,
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))


# --------- Intolerance of uncertainty
df_ius <- df %>%
  select(id, contains("IUS")) %>%
  pivot_longer(cols = IUS_1:IUS_12,
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

# --------- Quality of life
df_icecap <- df %>%
  select(id, contains("ICECAP"), -matches("Sum|sum")) %>%
  pivot_longer(cols = ICECAP1r:ICECAP5r,
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

# --------- Denial and Acceptance
df_bc <- df %>%
  select(id, BC_2, BC_7, BC_10, BC_12) %>%
  pivot_longer(c(BC_2,BC_7, BC_10, BC_12),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))


# --------- Work
df_w <- df %>%
  select(id, contains("WorkCen"), contains("UWES"), contains("commit"), -matches("Sum|sum")) %>%
  pivot_longer(c(WorkCen_1, WorkCen_2, WorkCen_3R, UWES_1, UWES_2, UWES_3, commit_1, commit_2, commit_3),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))


write.csv(df_ijls, "IJLS_Eersel_2024_IJLSreaction.csv", row.names=FALSE)
write.csv(df_lot, "IJLS_Eersel_2024_Optimism.csv", row.names=FALSE)
write.csv(df_d, "IJLS_Eersel_2024_Depression.csv", row.names=FALSE)
write.csv(df_a, "IJLS_Eersel_2024_Anxiety.csv", row.names=FALSE)
write.csv(df_bc, "IJLS_Eersel_2024_DenialAcceptance.csv", row.names=FALSE)
write.csv(df_ius, "IJLS_Eersel_2024_IUS.csv", row.names=FALSE)
write.csv(df_icecap, "IJLS_Eersel_2024_ICECAP.csv", row.names=FALSE)
write.csv(df_w, "IJLS_Eersel_2024_Work.csv", row.names=FALSE)



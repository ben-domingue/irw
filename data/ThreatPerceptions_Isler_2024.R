library(readxl)
library(dplyr)
library(tidyr)

# ---------- EXPERIMENT 1 ----------

df1 <- read_xlsx("Experiment 1 Data.xlsx")

df1 <- df1 %>%
  select(ID, 
         interested:repulsed,
         CRT1)

colnames(df1) <- tolower(colnames(df1))

df1 <- df1 %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")

df1$experiment <- "1"
df1$id <- paste0(df1$id, "_1")

# ---------- EXPERIMENT 2 ----------

df2 <- read_xlsx("Experiment 2 Data.xlsx")

df2 <- df2 %>%
  select(ID,
         interested:repulsed,
         CRT1)

colnames(df2) <- tolower(colnames(df2))

df2 <- df2 %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")

df2$experiment <- "2"
df2$id <- paste0(df2$id, "_2")

# ---------- EXPERIMENT 3 ----------

df3 <- read_xlsx("Experiment 3 Data.xlsx")

df3 <- df3 %>%
  select(ID,
         interested:repulsed) %>%
  rename("inspired" = "inspiredâBelowarewordsth")

colnames(df3) <- tolower(colnames(df3))

df3 <- df3 %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")

df3$experiment <- "3"
df3$id <- paste0(df3$id, "_3")

# ---------- EXPERIMENT 4 ----------

df4 <- read_xlsx("Experiment 4 Data.xlsx")

df4 <- df4 %>%
  select(ID,
         CRT1,
         CRT2,
         CRT3,
         interested:repulsed)

colnames(df4) <- tolower(colnames(df4))

df4 <- df4 %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")

df4$experiment <- "4"
df4$id <- paste0(df4$id, "_4")


combined <- bind_rows(df1, df2, df3, df4)

write.csv(combined, "ThreatPerceptions_Isler_2024.csv", row.names=FALSE)



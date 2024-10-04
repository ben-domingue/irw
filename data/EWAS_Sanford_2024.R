library(haven)
library(dplyr)
library(labelled)
library(tidyr)

# study 1

df <- read_sav("2024 Sanford EWAS Study 1.sav")
df$id <- seq(1, nrow(df))
df <- remove_labels(df)

df <- df %>%
  select(id, Mea1, Mea2, Mea3, Mea4, Mea5, Mea6, Sat1, Sat2, Sat3, Sat4, 
         Sat5, Sat6, Enri1, Enri2, Enri3, Enri4, Enri5, Enri6, Enga1, Enga2,
         Enga3, Enga4, Enga5, Enga6, Prod1, Prod2, Prod3, Prod4, Prod5, Prod6) %>%
  mutate(across(everything(), ~ as.numeric(as.character(.)))) %>%
pivot_longer(c(Mea1, Mea2, Mea3, Mea4, Mea5, Mea6, Sat1, Sat2, Sat3, Sat4, 
             Sat5, Sat6, Enri1, Enri2, Enri3, Enri4, Enri5, Enri6, Enga1, Enga2,
             Enga3, Enga4, Enga5, Enga6, Prod1, Prod2, Prod3, Prod4, Prod5, Prod6),
             names_to = "item",
             values_to = "resp") %>%
  filter(!is.na(resp)) %>%
  mutate(item = tolower(item))

df$study <- 1

#study 2

df2 <- read_sav("2024 Sanford EWAS Study 2.sav")
df2$id <- seq(1, nrow(df2))
df2 <- remove_labels(df2)

df2 <- df2 %>%
  select(id, prod1, enri2, enga3, sat1, mea2, enri3) %>%
  mutate(across(everything(), ~ as.numeric(as.character(.)))) %>%
  pivot_longer(c(prod1, enri2, enga3, sat1, mea2, enri3),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

df2$study <- 2

df_comb <- bind_rows(df, df2)

# dff <- df_comb %>% filter(study == 1)
# print(dff)

# study 2 - flourish

dffl <- read_sav("2024 Sanford EWAS Study 2.sav")
dffl$id <- seq(1, nrow(dffl))
dffl <- remove_labels(dffl)

dffl <- dffl %>%
  select(id, Flourish1, Flourish2, Flourish3,
         Flourish4, Flourish5, Flourish6, Flourish7, Flourish8) %>%
  mutate(across(everything(), ~ as.numeric(as.character(.)))) %>%
  pivot_longer(c(Flourish1, Flourish2, Flourish3,
                 Flourish4, Flourish5, Flourish6, Flourish7, Flourish8),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp)) %>%
  mutate(item = tolower(item))

write.csv(df_comb, "EWAS_Sanford_2024.csv", row.names=FALSE)
write.csv(dffl, "EWAS_Sanford_2024_Flourish.csv", row.names=FALSE)
        
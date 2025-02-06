library(readxl)
library(dplyr)
library(tidyr)

# ---------- EXPERIMENT 1 ----------

df1 <- read_xlsx("Experiment 1 Data.xlsx")

colnames(df1) <- tolower(colnames(df1))

df1 <- df1 %>%
  select(id, 
         interested:repulsed,
         crt1,
         cognitive_manipulation,
         incentive_manipulation)

df1 <- df1 %>%
  pivot_longer(-c(id, cognitive_manipulation, incentive_manipulation),
               names_to = "item",
               values_to = "resp")

df1_cog <- df1 %>%
  select(id, cognitive_manipulation, item, resp) %>%
  rename(treat = cognitive_manipulation)

df1_inc <- df1 %>%
  select(id, incentive_manipulation, item, resp) %>%
  rename(treat = incentive_manipulation)

# df1$id <- paste0(df1$id, "_1")

# ---------- EXPERIMENT 2 ----------

df2 <- read_xlsx("Experiment 2 Data.xlsx")

colnames(df2) <- tolower(colnames(df2))

df2 <- df2 %>%
  select(id, 
         interested:repulsed,
         crt1,
         cognitive_manipulation,
         picture_manipulation)

df2 <- df2 %>%
  pivot_longer(-c(id, cognitive_manipulation, picture_manipulation),
               names_to = "item",
               values_to = "resp")

df2_cog <- df2 %>%
  select(id, cognitive_manipulation, item, resp) %>%
  rename(treat = cognitive_manipulation)

df2_pic <- df2 %>%
  select(id, picture_manipulation, item, resp) %>%
  rename(treat = picture_manipulation)

# df2$id <- paste0(df2$id, "_2")

# ---------- EXPERIMENT 3 ----------

df3 <- read_xlsx("Experiment 3 Data.xlsx")

colnames(df3) <- tolower(colnames(df3))

df3 <- df3 %>%
  select(id,
         interested:repulsed,
         cognitive_manipulation) %>%
  rename("inspired" = "inspiredâbelowarewordsth")

df3 <- df3 %>%
  pivot_longer(-c(id, cognitive_manipulation),
               names_to = "item",
               values_to = "resp")

df3_cog <- df3 %>%
  select(id, cognitive_manipulation, item, resp) %>%
  rename(treat = cognitive_manipulation)

# df3$id <- paste0(df3$id, "_3")

# ---------- EXPERIMENT 4 ----------

df4 <- read_xlsx("Experiment 4 Data.xlsx")

colnames(df4) <- tolower(colnames(df4))

df4 <- df4 %>%
  select(id,
         crt1,
         crt2,
         crt3,
         interested:repulsed,
         cognitive_manipulation)

df4 <- df4 %>%
  pivot_longer(-c(id, cognitive_manipulation),
               names_to = "item",
               values_to = "resp")

df4_cog <- df4 %>%
  select(id, cognitive_manipulation, item, resp) %>%
  rename(treat = cognitive_manipulation)

# df4$id <- paste0(df4$id, "_4")


# combined <- bind_rows(df1, df2, df3, df4)

# df_panas <- combined %>%
#   filter(!grepl("crt", item))
# 
# df_crt <- combined %>%
#   filter(grepl("crt", item))

df1_cog_panas <- df1_cog %>%
  filter(!grepl("crt", item))

df1_cog_crt <- df1_cog %>%
  filter(grepl("crt", item))

df1_inc_panas <- df1_inc %>%
  filter(!grepl("crt", item))

df1_inc_crt <- df1_inc %>%
  filter(grepl("crt", item))

df2_cog_panas <- df2_cog %>%
  filter(!grepl("crt", item))

df2_cog_crt <- df2_cog %>%
  filter(grepl("crt", item))

df2_pic_panas <- df2_pic %>%
  filter(!grepl("crt", item))

df2_pic_crt <- df2_pic %>%
  filter(grepl("crt", item))

df3_cog_panas <- df3_cog %>%
  filter(!grepl("crt", item))

df4_cog_panas <- df4_cog %>%
  filter(!grepl("crt", item))

df4_cog_crt <- df4_cog %>%
  filter(grepl("crt", item))

write.csv(df1_cog_panas, "threatperceptions_isler_2024_experiment1_cognitive_panas.csv", row.names=FALSE)
write.csv(df1_cog_crt, "threatperceptions_isler_2024_experiment1_cognitive_crt.csv", row.names=FALSE)
write.csv(df1_inc_panas, "threatperceptions_isler_2024_experiment1_incentive_panas.csv", row.names=FALSE)
write.csv(df1_inc_crt, "threatperceptions_isler_2024_experiment1_incentive_crt.csv", row.names=FALSE)

write.csv(df2_cog_panas, "threatperceptions_isler_2024_experiment2_cognitive_panas.csv", row.names=FALSE)
write.csv(df2_cog_crt, "threatperceptions_isler_2024_experiment2_cognitive_crt.csv", row.names=FALSE)
write.csv(df2_pic_panas, "threatperceptions_isler_2024_experiment2_picture_panas.csv", row.names=FALSE)
write.csv(df2_pic_crt, "threatperceptions_isler_2024_experiment2_picture_crt.csv", row.names=FALSE)

write.csv(df3_cog_panas, "threatperceptions_isler_2024_experiment3_cognitive_panas.csv", row.names=FALSE)

write.csv(df4_cog_panas, "threatperceptions_isler_2024_experiment4_cognitive_panas.csv", row.names=FALSE)
write.csv(df4_cog_crt, "threatperceptions_isler_2024_experiment4_cognitive_crt.csv", row.names=FALSE)

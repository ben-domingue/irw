
library(readxl)
library(dplyr)
library(tidyr)
options(scipen = 999)


df <- read_excel("D:/Desktop/DEMOS_data.xlsx", skip = 1)


df_selected <- df %>% select(id = filename, accuracy_mean, intensity_mean, subj_move_mean, obj_move_mean)


df_long <- pivot_longer(df_selected, cols = -id, names_to = "item", values_to = "resp")


save(df_long, file = "D:/Desktop/DEMOS.RData")

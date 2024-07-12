#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
library(dplyr)
library(tidyr)
library(haven)

data_1a <- read_sav("Study 1a_MTurk_Data.sav")
data_1a <- data_1a %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_1b <- read_sav("Study 1b_PrimePanels_Data.sav")
data_1b <- data_1b %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_2 <- read_sav("Study 2_Imposters_Data.sav")
data_2 <- data_2 %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_3a <- read_sav("Study 3a_AA_Data.sav")
data_3a <- data_3a %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_3b <- read_sav("Study 3b_LE_Data.sav")
data_3b <- data_3b %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_3c <- read_sav("Study 3c_IM_Data.sav")
data_3c <- data_3c %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_1b <- data_1b[!is.na(data_1b$Age), ]
data_3c <- data_3c[!is.na(data_3c$Q4.4), ]
data_2 <- data_2[!is.na(data_2$Q57), ]

# Check if Q8 is correct
for (dataset in list("data_1b", "data_3a", "data_3b", "data_3c")) {
  assign(dataset, get(dataset) %>% mutate(Q8correct = ifelse(Q8 == 2, 1, 0)))
}

# make 'i dont know' NA
columns <- c("Q4","Q6","Q8","Q11","Q13","Q23","Q33","Q40","Q41","Q45","Q47","Q49","Q59","Q61","Q63","Q65","Q67","Q69","Q75")

for (dataset in list("data_1a", "data_1b", "data_2", "data_3a", "data_3b", "data_3c")) {
  for (col in columns) {
    correct_col <- paste0(col, "correct")
    assign(dataset, get(dataset) %>% mutate(!!correct_col := ifelse(is.na(get(col)), NA, get(correct_col))))
  }
}

data_1a <- rename(data_1a, age = Q57)
data_1b <- rename(data_1b, age = Age)
data_2 <- rename(data_2, age = Q57)
data_3a <- rename(data_3a, age = Q57)
data_3b <- rename(data_3b, age = Q4.4)
data_3c <- rename(data_3c, age = Q4.4)

for (dataset in list("data_1a", "data_1b", "data_2", "data_3a", "data_3b", "data_3c")) {
  assign(dataset, get(dataset) %>% rename(id = ResponseId))
}

# add group
data_1a <- mutate(data_1a, group = "1a")
data_1b <- mutate(data_1b, group = "1b")
data_2 <- mutate(data_2, group = "2")
data_3a <- mutate(data_3a, group = "3a")
data_3b <- mutate(data_3b, group = "3b")
data_3c <- mutate(data_3c, group = "3c")

select_columns <- c("Q4correct", "Q6correct", "Q61correct", "Q11correct", "Q23correct", "Q40correct", "Q63correct", 
                    "Q45correct", "Q67correct", "Q49correct", "Q69correct", "Q75correct", "Q47correct", "Q33correct", 
                    "Q65correct", "Q13correct", "Q8correct", "Q41correct", "Q59correct", "id", "age", "group")

data_1a <- select(data_1a, all_of(select_columns))
data_1b <- select(data_1b, all_of(select_columns))
data_2 <- select(data_2, all_of(select_columns))
data_3a <- select(data_3a, all_of(select_columns))
data_3b <- select(data_3b, all_of(select_columns))
data_3c <- select(data_3c, all_of(select_columns))

data_list <- list(data_1a, data_1b, data_2, data_3a, data_3b, data_3c)
long_data_list <- lapply(data_list, function(df) {
  df_long <- pivot_longer(df, cols = starts_with("Q"), names_to = "item", values_to = "resp")
  return(df_long)
})

AVI_S_data <- bind_rows(long_data_list)

save(AVI_S_data, file = "AVI-S.RData") ##bd note: saved as wooly_hartman2022 

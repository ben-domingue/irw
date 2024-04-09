#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
#study_1a1b3b3c
library(tidyr)
library(dplyr)
library(haven)

data_1a <- read_sav("Study 1a_MTurk_Data.sav")
data_1a <- data_1a %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_1b <- read_sav("Study 1b_PrimePanels_Data.sav")
data_1b <- data_1b %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))
data_1b <- data_1b[!is.na(data_1b$Age), ]

data_3b <- read_sav("Study 3b_LE_Data.sav")
data_3b <- data_3b %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data_3c <- read_sav("Study 3c_IM_Data.sav")
data_3c <- data_3c %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))
data_3c <- data_3c[!is.na(data_3c$Q4.4), ]


clean <- function(data, age_col, group_name) {
  
  questions <- c("Q4", "Q6", "Q11", "Q13", "Q23", "Q33", "Q40", "Q41", "Q45", "Q47", "Q49", "Q59", "Q61", "Q63", "Q65", "Q67", "Q69", "Q75")
  for(q in questions) {
    correct_col <- paste0(q, "correct")
    data[[correct_col]][is.na(data[[q]])] <- NA
  }
  
  # select and rename
  selected_cols <- paste0(questions, "correct")
  data <- data %>%
    select(ResponseId, all_of(selected_cols), age_col) %>%
    rename(id = ResponseId, age = age_col)
  names(data)[-which(names(data) == "age")][-1] <- gsub("correct", "", names(data)[-which(names(data) == "age")][-1])
  
  # add group
  data$group <- group_name
  
  return(data)
}

data_1a_cleaned <- clean(data_1a, "Q57", "1a")
data_1b_cleaned <- clean(data_1b, "Age", "1b")
data_3b_cleaned <- clean(data_3b, "Q4.4", "3b")
data_3c_cleaned <- clean(data_3c, "Q4.4", "3c")

# combine
data_combined <- bind_rows(data_1a_cleaned, data_1b_cleaned, data_3b_cleaned, data_3c_cleaned)


data1 <- data_combined %>%
  pivot_longer(
    -c(id, age, group),
    names_to = "item",
    values_to = "resp"
  )


save(data1, file = "vertifyage_study1a1b3b3c.RData")

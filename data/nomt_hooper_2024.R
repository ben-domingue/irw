library(tidyr)
library(dplyr)
library(stringr)

################## STUDY 1 ##################

df1 <- read.csv("Part1_individual trials.csv", check.names = FALSE)

df1 <- df1 %>%
  rename(id = S) %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")

unique(df1$item)
table(df1$resp)


################## STUDY 2 ##################


df2 <- read.csv("Part2_data.csv", check.names = FALSE)

df2 <- df2 %>%
  rename(group = GROUP, id = SS, cov_gender = Sex, cov_age = age, cov_nationality = Nationality, cov_country_of_birth = "Country of Birth", 
         cov_country_of_residence = "Current Country of Residence", cov_first_language = "First Language", cov_spanish_fluency = "Spanish", 
         cov_english_fluency = "English")

df2 <- df2 %>% 
  select(-c("Average Performance")) %>%
  pivot_longer(-c(id, group, cov_gender, cov_age, cov_nationality, cov_country_of_birth, 
                  cov_country_of_residence, cov_first_language, cov_spanish_fluency, 
                  cov_english_fluency),
               names_to = "item_obj",
               values_to = "resp") %>%
  mutate(across(c(cov_gender, cov_nationality, cov_country_of_birth, 
                  cov_country_of_residence, cov_first_language), 
                ~na_if(., "•")))

df2$item <- str_extract(df2$item_obj, "\\d+")

df2 <- df2 %>% mutate(item_obj = case_when(
  grepl("Accurate", item_obj) ~ "resp",
  grepl("Selection", item_obj) ~ "resp_raw",
  grepl("Rt", item_obj) ~ "rt"
))

df2 <- df2 %>%
  pivot_wider(names_from = 'item_obj',
              values_from = 'resp')

df2$rt <- df2$rt / 1000


write.csv(df1, "nomt_hooper_2024_study1.csv", row.names = FALSE)
write.csv(df2, "nomt_hooper_2024_study2.csv", row.names = FALSE)

library(dplyr)
library(tidyr)

df <- read.csv("Data to Share.csv")

df <- df %>%
  mutate(
    timestamp_clean = gsub(" MDT$", "", timestamp),
    timestamp_parsed = as.POSIXct(timestamp_clean, format = "%Y/%m/%d %I:%M:%S %p", tz = "America/Denver"),
    timestamp_unix = as.numeric(timestamp_parsed)
  ) %>%
  rename(cov_job = current_job, cov_commute_miles = commute_miles, cov_commute_leave_time = commute_leave_time,
         cov_gender = gender, cov_age = age, cov_race = race, cov_living_situation = living_situation,
         cov_income = hh_income, cov_edu = edu, cov_living_space = living_space, cov_covid = COVID, date = timestamp_unix)

df$id <- seq(1, nrow(df))

df <-df %>%
  select(id, date, starts_with("cov"), matches("(bc|dr|ac)$"), -starts_with("mod"),
         media_exag, face_cover_mandatory, business_shut_down,
         stay_home, physical_dist, ff_health, ff_stay_home, wfh_family, miss_commute, online_meeting,
         coworker_interact, social_interact, wfh_discipline, crowded_bus, transit_health,
         rideshare_stranger, avoid_share, save_money, transit_physical_distance,
         personal_space, online_shop_conv, physical_purchase, instore_groc_fun,
         online_groc_pref, store_enjoy, restaurant_fun)

df <- df %>%
  pivot_longer(-c(id, starts_with("cov"), date),
               names_to = "item",
               values_to = "resp")


df <- df %>% mutate(resp = case_when(
  resp == "Never"   ~ "0",
  resp == "Once a month or less"  ~ "1",
  resp == "A few times a month" ~ "2",
  resp == "1-2 days a week" ~ "3",
  resp == "3-4 days a week"   ~ "4",
  resp == "Everyday"  ~ "5",
  
  resp == "Strongly disagree"   ~ "0",
  resp == "Disagree"  ~ "1",
  resp == "Somewhat disagree" ~ "2",
  resp == "Somewhat agree" ~ "3",
  resp == "Agree"   ~ "4",
  resp == "Strongly agree"  ~ "5",
  resp == "N/A"  ~ NA,
  TRUE ~ resp 
))


write.csv(df, "covid_travel_mackenzie_2021.csv", row.names = FALSE)

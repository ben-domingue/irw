# Paper: https://link.springer.com/article/10.3758/s13428-024-02525-x#Sec18
# Data: https://researchbox.org/1892
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

# ------------ Study 1 Data ------------
brand_memory_df <- read_xlsx("Raw_Brand_Memory_Task_Prolific.xlsx")
brand_memory_df <- brand_memory_df |>
  slice(-1)
brand_prolific_df <- read_xlsx("Raw_Brand_Prolific.xlsx")
brand_prolific_df <- brand_prolific_df |>
  slice(-1)
logo_memory_df <- read_xlsx("Raw_Logo_Memory_Task_Prolific.xlsx")
logo_memory_df <- logo_memory_df |>
  slice(-1)
logo_prolific_df <- read_xlsx("Raw_Logo_prolific.xlsx")
logo_prolific_df <- logo_prolific_df |>
  slice(-1)

brand_memory_df <-brand_memory_df |>
  mutate(id= paste0("bm_", row_number()))
liking_bm_df <- brand_memory_df %>%
  select(ends_with("liking"), id, Gender, Age)
liking_bm_df <- remove_na(liking_bm_df)
liking_bm_df <- pivot_longer(liking_bm_df, cols=-c(id, Gender, Age), names_to="item", values_to="resp")
liking_bm_df <-liking_bm_df |>
  rename(cov_gender = Gender, cov_age = Age)
liking_bm_df$item_family <- "name"

brand_prolific_df <-brand_prolific_df  |>
  mutate(id= paste0("bp_", row_number()))
liking_bp_df <- brand_prolific_df %>%
  select(ends_with("liking"), id, Sex, Age)
liking_bp_df <- remove_na(liking_bp_df)
liking_bp_df <- pivot_longer(liking_bp_df, cols=-c(id, Sex,Age), names_to="item", values_to="resp")
liking_bp_df <-liking_bp_df |>
  rename(cov_gender = Sex,cov_age = Age)
liking_bp_df$item_family <- "name"

logo_memory_df <- logo_memory_df %>%
  mutate(id= paste0("lm_", row_number()))
liking_lm_df <- logo_memory_df  %>%
  select(ends_with("liking"), id,Gender, Age)
liking_lm_df <- remove_na(liking_lm_df)
liking_lm_df <- pivot_longer(liking_lm_df, cols=-c(id, Gender,Age), names_to="item", values_to="resp")
liking_lm_df <- liking_lm_df |>
  rename(cov_gender = Gender, cov_age = Age)
liking_lm_df$item_family <- "logo"

mapping <- c("2" = 1, "4" = 2, "5" = 3, "6" = 4, "7" = 5, "8" = 6, "9" = 7)
gender_mapping <- c("Female"=1, "Male"=2)
logo_prolific_df  <-logo_prolific_df   |>
  mutate(id= paste0("lp_", row_number()))

# ----- Liking -----
liking_lp_df <- logo_prolific_df  %>%
  select(ends_with("liking"), id, Sex, Age)
liking_lp_df <- remove_na(liking_lp_df)
liking_lp_df <- pivot_longer(liking_lp_df, cols=-c(id, Sex, Age), names_to="item", values_to="resp")
liking_lp_df <-liking_lp_df |>
  rename(cov_gender = Sex, cov_age = Age)
liking_lp_df <- liking_lp_df %>%
  mutate(resp = recode(resp, !!!mapping))
liking_lp_df$item_family <- "logo"

liking_df <- rbind(liking_bm_df, liking_bp_df,liking_lm_df,liking_lp_df)
liking_df <- liking_df |> 
  mutate(cov_gender = recode(cov_gender, !!!gender_mapping, .default = cov_gender),
         cov_gender = suppressWarnings(as.numeric(cov_gender))) 

liking_df$item <- tolower(liking_df$item)
save(liking_df, file="brand_brand_raffaelli_2024_liking_20.Rdata")
write.csv(liking_df, "brand_brand_raffaelli_2024_liking_20.csv", row.names=FALSE)

# ----- Recognition -----
recognition_bm_df <- brand_memory_df %>%
  select(ends_with("recognition"), id, Gender, Age)
recognition_bm_df  <- remove_na(recognition_bm_df)
recognition_bm_df  <- pivot_longer(recognition_bm_df , cols=-c(id, Gender, Age), names_to="item", values_to="resp")
recognition_bm_df <- recognition_bm_df |>
  rename(cov_gender = Gender, cov_age = Age)

recognition_lm_df <- logo_memory_df  %>%
  select(ends_with("recognition"), id,Gender, Age)
recognition_lm_df <- remove_na(recognition_lm_df)
recognition_lm_df <- pivot_longer(recognition_lm_df, cols=-c(id, Gender,Age), names_to="item", values_to="resp")
recognition_lm_df <- recognition_lm_df |>
  rename(cov_gender = Gender, cov_age = Age)

recognition_bm_df $ item_family <- "name"
recognition_lm_df $ item_family <- "logo"

recognition_df <- rbind(recognition_bm_df, recognition_lm_df)

recognition_df$item <- tolower(recognition_df$item)
save(recognition_df, file="brand_brand_raffaelli_2024_recognition_20.Rdata")
write.csv(recognition_df, "brand_brand_raffaelli_2024_recognition_20.csv", row.names=FALSE)

# ------------ Study 3 Data ------------
brand_logos24_df <- read_xlsx("Brand_Logos_Prolific_2024.xlsx")
brand_logos24_df <- brand_logos24_df |>
  slice(-1)
brand_prolific24_df <- read_xlsx("Brand_Name_Prolific_2024.xlsx")
brand_prolific24_df <- brand_prolific24_df |>
  slice(-1)

brand_logos24_df <- brand_logos24_df |>
  rename(cov_age=Age, cov_gender=Gender) |> 
  mutate(id=paste0("bl_", row_number()))
brand_prolific24_df <- brand_prolific24_df |>
  rename(cov_age=Age, cov_gender=Gender) |> 
  mutate(id=paste0("bp_", row_number()))

# ----- Liking -----
liking_bl24_df <- brand_logos24_df |>
  select(ends_with("Liking"), cov_age, cov_gender, id)
liking_bl24_df <- pivot_longer(liking_bl24_df, cols=-c(cov_age, cov_gender, id), names_to="item", values_to="resp")
liking_bl24_df$item_family <- "logo"

liking_bn24_df <- brand_prolific24_df |>
  select(ends_with("Liking"), cov_age, cov_gender, id)
liking_bn24_df <- pivot_longer(liking_bn24_df, cols=-c(cov_age, cov_gender, id), names_to="item", values_to="resp")
liking_bn24_df$item_family <- "name"

liking24_df <- rbind(liking_bn24_df, liking_bl24_df)
liking24_df$item <- tolower(liking24_df$item)
save(liking24_df, file="brand_brand_raffaelli_2024_liking_24.Rdata")
write.csv(liking24_df, "brand_brand_raffaelli_2024_liking_24.csv", row.names=FALSE)

# ----- Familiarity -----
familiarity_bl24_df <- brand_logos24_df |>
  select(ends_with("Familiarity"), cov_age, cov_gender, id)
familiarity_bl24_df <- pivot_longer(familiarity_bl24_df, cols=-c(cov_age, cov_gender, id), names_to="item", values_to="resp")
familiarity_bl24_df$item_family <- "logo"

familiarity_bn24_df <- brand_prolific24_df |>
  select(ends_with("Familiarity"), cov_age, cov_gender, id)
familiarity_bn24_df <- pivot_longer(familiarity_bn24_df, cols=-c(cov_age, cov_gender, id), names_to="item", values_to="resp")
familiarity_bn24_df$item_family <- "name"
familiarity24_df <- rbind(familiarity_bn24_df, familiarity_bl24_df)

modify_item_column <- function(df) {
  df <- df %>%
    mutate(item = gsub("^(\\d+)_Brand_(.*)$", "\\1_\\U\\2", item, perl = TRUE))
  return(df)
}
familiarity24_df <- modify_item_column(familiarity24_df)
familiarity24_df$item <- tolower(familiarity24_df$item)
save(familiarity24_df, file="brand_brand_raffaelli_2024_familiarity_24.Rdata")
write.csv(familiarity24_df, "brand_brand_raffaelli_2024_familiarity_24.csv", row.names=FALSE)
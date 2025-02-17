# Paper: https://web.archive.org/web/20190429102600id_/https://blogs.konradlorenz.edu.co/files/18009-final.pdf
# Data: https://osf.io/h3tfc/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

study1_df <- read_xls("PANAS_Database_Study1.xls")
study1_df <- study1_df |>
  rename(id=ID)
study2_df <- read_xls("PANAS_Database_Study2.xls")
study2_df <- study2_df |>
  rename(id=numero)
study3_df <- read_xls("PANAS_Database_Study3.xls")
study3_df <- study3_df |>
  rename(id=numero)
study4_df <- read_xls("PANAS_Database_Study4.xls")
study4_df <- study4_df |>
  rename(id = ID)

PANAS1_df <- study1_df %>%
  select(starts_with("PANAS"), id, Sex, Age, -ends_with("m"))
PANAS1_df  <- remove_na(PANAS1_df)
PANAS1_df <- pivot_longer(PANAS1_df, cols=-c(id, Sex, Age), names_to="item", values_to="resp")
PANAS1_df <- PANAS1_df |>
  rename(cov_sex = Sex, cov_age = Age)
PANAS1_df$group <- "University_Students1"

PANAS2_df <- study2_df %>%
  select(starts_with("PANAS"), id, sexo, edad, carrera, -ends_with("m"))
PANAS2_df  <- remove_na(PANAS2_df)
PANAS2_df <- pivot_longer(PANAS2_df, cols=-c(id, sexo, edad, carrera), names_to="item", values_to="resp")
PANAS2_df <- PANAS2_df |>
  rename(cov_sex = sexo, cov_age = edad, cov_career = carrera)
PANAS2_df$group <- "University_Students2"

PANAS3_df <- study3_df %>%
  select(starts_with("PANAS"), id, sexo, edad,  neducativo, -ends_with("m"))
PANAS3_df  <- remove_na(PANAS3_df)
PANAS3_df <- pivot_longer(PANAS3_df, cols=-c(id, sexo, edad, neducativo), names_to="item", values_to="resp")
PANAS3_df <- PANAS3_df |>
  rename(cov_sex = sexo, cov_age = edad, cov_educational = neducativo)
PANAS3_df$group <- "General Adult"

PANAS4_df <- study4_df %>%
  select(starts_with("PANAS"), id, Sexo, Edad, -ends_with("m"))
PANAS4_df  <- remove_na(PANAS4_df)
PANAS4_df <- pivot_longer(PANAS4_df, cols=-c(id,Sexo, Edad), names_to="item", values_to="resp")
PANAS4_df <- PANAS4_df |>
  rename(cov_sex = Sexo, cov_age = Edad)
PANAS4_df$group <- "Athletes"

Panas_df <- bind_rows(PANAS1_df, PANAS2_df, PANAS3_df, PANAS4_df)
Panas_df$resp <- ifelse(Panas_df$resp %in% c(1, 2, 3, 4, 5), Panas_df$resp, NA)

save(Panas_df, file="fcupanas_cffsdas_reyna_2018.Rdata")
write.csv(Panas_df, "fcupanas_cffsdas_reyna_2018.csv", row.names=FALSE)
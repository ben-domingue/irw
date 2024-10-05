# Paper: https://osf.io/preprints/psyarxiv/8fdma
# Data: https://osf.io/txn2y/
library(haven)
library(dplyr)
library(tidyr)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

remove_na2 <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

practioner_df <- read_sav("maia2_practitioners.sav")
student_df <- read_sav("maia2_students.sav")

# ------ Dataset Pre-process ------
practioner_df <- practioner_df |>
  rename(id=uid)
practioner_df[] <- lapply(practioner_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
student_df <- student_df |>
  rename(id=uid)
student_df[] <- lapply(student_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

# ------ Process MAIA2 Dataset ------
practioner_maia_df <- practioner_df |>
  select(starts_with("MAIA"), id, -MAIA2_i1)
practioner_maia_df <- practioner_maia_df |>
  rename(date=MAIA2_final)
practioner_maia_df  <- remove_na(practioner_maia_df )
practioner_maia_df$date <- as.numeric(as.POSIXct(practioner_maia_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
practioner_maia_df <- pivot_longer(practioner_maia_df, cols=-c(id, date), names_to="item", values_to="resp")

student_maia_df <- student_df |>
  select(starts_with("MAIA"), id)
student_maia_df <- student_maia_df |>
  rename(date=MAIA2_final)
student_maia_df  <- remove_na(student_maia_df )
student_maia_df$date <- as.numeric(as.POSIXct(student_maia_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))

student_maia_t2_df <- student_maia_df |>
  select(ends_with("_t2"), id)
student_maia_df <- student_maia_df |>
  select(-ends_with("_t2"))

colnames(student_maia_t2_df) <- gsub("_t2", "", colnames(student_maia_t2_df))
student_maia_t2_df <- remove_na(student_maia_t2_df)
student_maia_df <- pivot_longer(student_maia_df, cols=-c(id, date), names_to="item", values_to="resp")

student_maia_t2_df <- student_maia_t2_df |>
  rename(date=MAIA2_final)
student_maia_t2_df$date <- as.numeric(as.POSIXct(student_maia_t2_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
student_maia_t2_df <- pivot_longer(student_maia_t2_df, cols=-c(id, date), names_to="item", values_to="resp")

student_maia_df$wave <- 0
student_maia_t2_df$wave <- 1
practioner_maia_df$wave <- NA

# Merge the 2 trials
student_maia_df <- rbind(student_maia_df, student_maia_t2_df)

maia_df <- rbind(student_maia_df, practioner_maia_df)
save(maia_df, file="SV-MAIA2_Randelovic_2021_MAIA.Rdata")
write.csv(maia_df, "SV-MAIA2_Randelovic_2021_MAIA.csv", row.names=FALSE)

# ------ Process SHS Dataset ------
practioner_SHS_df <- practioner_df |>
  select(starts_with("SHS"), id, -SHS )
practioner_SHS_df <- remove_na(practioner_SHS_df)
practioner_SHS_df <- pivot_longer(practioner_SHS_df, cols=-c(id), names_to="item", values_to="resp")

student_SHS_df <- student_df |>
  select(starts_with("SHS"), id)
student_SHS_df <- student_SHS_df |>
  select(-ends_with("_t2"), -SHS)
student_SHS_df <- pivot_longer(student_SHS_df, cols=-c(id), names_to="item", values_to="resp")

student_SHS_t2_df <- student_df |>
  select(starts_with("SHS"), id)
student_SHS_t2_df <- student_SHS_t2_df |>
  select(ends_with("_t2"), id, -SHS_i1_t2)
student_SHS_t2_df <- remove_na2(student_SHS_t2_df)
student_SHS_t2_df <- student_SHS_t2_df |>
  rename(date=SHS_final_t2)
student_SHS_t2_df$date <- as.numeric(as.POSIXct(student_SHS_t2_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
student_SHS_t2_df <- pivot_longer(student_SHS_t2_df, cols=-c(id, date), names_to="item", values_to="resp")

student_SHS_df$date <- NA
practioner_SHS_df$date <- NA

student_SHS_df$wave <- 0
student_SHS_t2_df$wave <- 1
practioner_SHS_df$wave <- NA

# Merge the 2 trials
student_SHS_df <- rbind(student_SHS_df, student_SHS_t2_df)
SHS_df <- rbind(student_SHS_df, practioner_SHS_df)
save(SHS_df, file="SV-MAIA2_Randelovic_2021_SHS.Rdata")
write.csv(SHS_df, "SV-MAIA2_Randelovic_2021_SHS.csv", row.names=FALSE)

# ------ Process HEXACO-100 Dataset ------

student_hexaco_df <- student_df |>
  select(starts_with("hexaco"), id)
student_hexaco_df  <- remove_na2(student_hexaco_df )
student_hexaco_df <- pivot_longer(student_hexaco_df, cols=-c(id), names_to="item", values_to="resp")

save(student_hexaco_df, file="SV-MAIA2_Randelovic_2021_hexaco100.Rdata")
write.csv(student_hexaco_df, "SV-MAIA2_Randelovic_2021_hexaco100.csv", row.names=FALSE)

# ------ Process Delta Dataset ------

student_delta_df <- student_df |>
  select(starts_with("Delta"), id, -deltat)
student_delta_df  <- remove_na2(student_delta_df )
student_delta_df <- pivot_longer(student_delta_df, cols=-c(id), names_to="item", values_to="resp")

save(student_delta_df, file="SV-MAIA2_Randelovic_2021_delta.Rdata")
write.csv(student_delta_df, "SV-MAIA2_Randelovic_2021_delta.csv", row.names=FALSE)

# ------ Process MAAS Dataset ------
practitioner_MAAS_df <- practioner_df |>
  select(starts_with("MAAS"), id, -MAAS_i1, -maasM) |>
  rename(date=MAAS_final)
practitioner_MAAS_df <- remove_na2(practitioner_MAAS_df)
practitioner_MAAS_df$date <- as.numeric(as.POSIXct(practitioner_MAAS_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))

practitioner_MAAS_df <- pivot_longer(practitioner_MAAS_df, cols=-c(id, date), names_to="item", values_to="resp")

save(practitioner_MAAS_df, file="SV-MAIA2_Randelovic_2021_MAAS.Rdata")
write.csv(practitioner_MAAS_df, "SV-MAIA2_Randelovic_2021_MAAS.csv", row.names=FALSE)

# ------ Process HEXACO-60 Dataset ------

practioner_hexaco_df <- practioner_df |>
  select(starts_with("HEXACO"), id)
practioner_hexaco_df <- practioner_hexaco_df |>
  rename(date=HEXACO_60_final)
practioner_hexaco_df  <- remove_na(practioner_hexaco_df )
practioner_hexaco_df$date <- as.numeric(as.POSIXct(practioner_hexaco_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
practioner_hexaco_df <- pivot_longer(practioner_hexaco_df, cols=-c(id,date), names_to="item", values_to="resp")

save(practioner_hexaco_df, file="SV-MAIA2_Randelovic_2021_hexaco60.Rdata")
write.csv(practioner_hexaco_df, "SV-MAIA2_Randelovic_2021_hexaco60.csv", row.names=FALSE)

# ------ Process ERQ Dataset ------

practioner_ERQ_df <- practioner_df |>
  select(starts_with("ERQ"), id, -ERQ_i1, -ERQ_R, -ERQ_S)
practioner_ERQ_df <- practioner_ERQ_df |>
  rename(date= ERQ_final)
practioner_ERQ_df  <- remove_na(practioner_ERQ_df )
practioner_ERQ_df$date <- as.numeric(as.POSIXct(practioner_ERQ_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
practioner_ERQ_df <- pivot_longer(practioner_ERQ_df, cols=-c(id,date), names_to="item", values_to="resp")

save(practioner_ERQ_df, file="SV-MAIA2_Randelovic_2021_ERQ.Rdata")
write.csv(practioner_ERQ_df, "SV-MAIA2_Randelovic_2021_ERQ.csv", row.names=FALSE)

# ------ Process DASS Dataset ------

practioner_dass_df <- practioner_df |>
  select(starts_with("DASS"), id, -DASS_i1,-DASS_S,-DASS_A, -DASS_D)
practioner_dass_df <- practioner_dass_df |>
  rename(date=DASS_final)
practioner_dass_df$date <- as.numeric(as.POSIXct(practioner_dass_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
practioner_dass_df <- remove_na(practioner_dass_df)

practioner_dass_df <- pivot_longer(practioner_dass_df, cols=-c(id, date), names_to="item", values_to="resp")

save(practioner_dass_df, file="SV-MAIA2_Randelovic_2021_DASS.Rdata")
write.csv(practioner_dass_df, "SV-MAIA2_Randelovic_2021_DASS.csv", row.names=FALSE)

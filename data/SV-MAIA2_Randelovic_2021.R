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

# ------ Process GEI14 Dataset ------

student_GEI_df <- student_df |>
  select(starts_with("GEI"), id)
student_GEI_df  <- remove_na2(student_GEI_df )
student_GEI_df <- pivot_longer(student_GEI_df, cols=-c(id), names_to="item", values_to="resp")

save(student_GEI_df, file="SV-MAIA2_Randelovic_2021_GEI.Rdata")
write.csv(student_GEI_df, "SV-MAIA2_Randelovic_2021_GEI.csv", row.names=FALSE)

# ------ Process MAAS Dataset ------
practitioner_MAAS_df <- practioner_df |>
  select(starts_with("MAAS"), id, -MAAS_i1, -maasM) |>
  rename(date=MAAS_final)
practitioner_MAAS_df <- remove_na2(practitioner_MAAS_df)
practitioner_MAAS_df$date <- as.numeric(as.POSIXct(practitioner_MAAS_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))

practitioner_MAAS_df <- pivot_longer(practitioner_MAAS_df, cols=-c(id, date), names_to="item", values_to="resp")

save(practitioner_MAAS_df, file="SV-MAIA2_Randelovic_2021_MAAS.Rdata")
write.csv(practitioner_MAAS_df, "SV-MAIA2_Randelovic_2021_MAAS.csv", row.names=FALSE)
# ------ Process SOD14 Dataset ------

student_SOD_df <- student_df |>
  select(starts_with("SOD"), id)
student_SOD_df <- student_SOD_df |>
  select(-ends_with("SOD"))
student_SOD_df  <- remove_na2(student_SOD_df )
student_SOD_df <- pivot_longer(student_SOD_df, cols=-c(id), names_to="item", values_to="resp")

save(student_SOD_df, file="SV-MAIA2_Randelovic_2021_SOD.Rdata")
write.csv(student_SOD_df, "SV-MAIA2_Randelovic_2021_SOD.csv", row.names=FALSE)

# ------ Process PD12 Dataset ------

student_PD_df <- student_df |>
  select(starts_with("PD"), id)
student_PD_df <- student_PD_df |>
  select(-ends_with("PD"))
student_PD_df  <- remove_na2(student_PD_df )
student_PD_df <- pivot_longer(student_PD_df, cols=-c(id), names_to="item", values_to="resp")

save(student_PD_df, file="SV-MAIA2_Randelovic_2021_PD.Rdata")
write.csv(student_PD_df, "SV-MAIA2_Randelovic_2021_PD.csv", row.names=FALSE)

# ------ Process FA11 Dataset ------

student_FA_df <- student_df |>
  select(starts_with("FA"), id)
student_FA_df <- student_FA_df |>
  select(-ends_with("FA"))
student_FA_df  <- remove_na2(student_FA_df )
student_FA_df <- pivot_longer(student_FA_df, cols=-c(id), names_to="item", values_to="resp")

save(student_FA_df, file="SV-MAIA2_Randelovic_2021_FA.Rdata")
write.csv(student_FA_df, "SV-MAIA2_Randelovic_2021_FA.csv", row.names=FALSE)

# ------ Process EA10 Dataset ------

student_EA_df <- student_df |>
  select(starts_with("EA"), id)
student_EA_df <- student_EA_df |>
  select(-ends_with("EA"))
student_EA_df  <- remove_na2(student_EA_df )
student_EA_df <- pivot_longer(student_EA_df, cols=-c(id), names_to="item", values_to="resp")

save(student_EA_df, file="SV-MAIA2_Randelovic_2021_EA.Rdata")
write.csv(student_EA_df, "SV-MAIA2_Randelovic_2021_EA.csv", row.names=FALSE)

# ------ Process SA10 Dataset ------

student_SA_df <- student_df |>
  select(starts_with("SA"), id)
student_SA_df  <- remove_na2(student_SA_df )
student_SA_df <- pivot_longer(student_SA_df, cols=-c(id), names_to="item", values_to="resp")

save(student_SA_df, file="SV-MAIA2_Randelovic_2021_SA.Rdata")
write.csv(student_SA_df, "SV-MAIA2_Randelovic_2021_SA.csv", row.names=FALSE)

# ------ Process MT13 Dataset ------

student_MT_df <- student_df |>
  select(starts_with("MT"), id)
student_MT_df <- student_MT_df |>
  select(-ends_with("MT"))
student_MT_df  <- remove_na2(student_MT_df )
student_MT_df <- pivot_longer(student_MT_df, cols=-c(id), names_to="item", values_to="resp")

save(student_MT_df, file="SV-MAIA2_Randelovic_2021_MT.Rdata")
write.csv(student_MT_df, "SV-MAIA2_Randelovic_2021_MT.csv", row.names=FALSE)

# ------ Process M12 Dataset ------

student_M_df <- student_df[, c(paste0("M", 1:12), "id")]
student_M_df  <- remove_na2(student_M_df )
student_M_df <- pivot_longer(student_M_df, cols=-c(id), names_to="item", values_to="resp")

save(student_M_df, file="SV-MAIA2_Randelovic_2021_M.Rdata")
write.csv(student_M_df, "SV-MAIA2_Randelovic_2021_M.csv", row.names=FALSE)

# ------ Process P Dataset ------

student_P_df <- student_df[, c("id", paste0("P", 1:13))]
student_P_df  <- remove_na2(student_P_df )
student_P_df <- pivot_longer(student_P_df, cols=-c(id), names_to="item", values_to="resp")

save(student_P_df, file="SV-MAIA2_Randelovic_2021_P.Rdata")
write.csv(student_P_df, "SV-MAIA2_Randelovic_2021_P.csv", row.names=FALSE)

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

# ------ Process DEL20 Dataset ------

practioner_DEL20_df <- practioner_df |>
  select(starts_with("DEL20"), id, -DEL20_i1)
practioner_DEL20_df <- practioner_DEL20_df |>
  rename(date=DEL20_final)
practioner_DEL20_df  <- remove_na(practioner_DEL20_df )
practioner_DEL20_df$date <- as.numeric(as.POSIXct(practioner_DEL20_df$date, format="%Y-%m-%d %H:%M:%S", tz="UTC"))
practioner_DEL20_df <- pivot_longer(practioner_DEL20_df, cols=-c(id,date), names_to="item", values_to="resp")

save(practioner_DEL20_df, file="SV-MAIA2_Randelovic_2021_DEL20.Rdata")
write.csv(practioner_DEL20_df, "SV-MAIA2_Randelovic_2021_DEL20.csv", row.names=FALSE)

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
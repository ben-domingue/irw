# Paper:https://osf.io/kp572/
# Data: https://osf.io/kp572/
library(haven)
library(dplyr)
library(tidyr)

rm(list = ls())

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

study1_df <- read.csv("BFI-2 Full data (study 1).csv")

study1_df <- study1_df |> # The study excludes participants from 1000 onwards
  slice(1:1000)

study2_wave1_df <- read.csv("1st wave.csv") 
study2_wave2_df <- read.csv("2nd wave.csv")

study2_wave1_df<- study2_wave1_df |>
  slice(-1)

study2_wave1_df <- study2_wave1_df |>
  filter(finished == "1")

study2_wave2_df<- study2_wave2_df |>
  slice(-1)

study2_wave2_df <- study2_wave2_df |>
  filter(finished == "1")

study3_df <- read.csv("Study 3 data.csv") 

#--------- BFI data --------
study1_BFI_df <- study1_df  |>
  select(starts_with("BFI"))
study1_BFI_df <- study1_BFI_df %>%
  mutate(id = paste0("study1_", row_number()))
study1_BFI_df <- pivot_longer(study1_BFI_df, cols=-c(id), names_to="item", values_to="resp")
study1_BFI_df$group <-1

study3_BFI_df <- study3_df  |>
  select(starts_with("BFI"), Participant)
study3_BFI_df <- study3_BFI_df |>
  rename(id = Participant) |>
  mutate(id = paste0("study3_", .data$id))
study3_BFI_df <- pivot_longer(study3_BFI_df, cols=-c(id), names_to="item", values_to="resp")

study3_BFI_df$group <-3

BFI_df <- rbind(study1_BFI_df , study3_BFI_df)
save(BFI_df, file="SABFI2_Gallardo_Pujol_2018_BFI.Rdata")
write.csv(BFI_df, "SABFI2_Gallardo_Pujol_2018_BFI.csv", row.names=FALSE)

a <- table(BFI_df$resp)
print(a)
#--------- SWB data -------- 
study3_SWB_df <- study3_df  |>
  select(starts_with("SWB"), Participant)
study3_SWB_df <- study3_SWB_df |>
  rename(id = Participant) 
study3_SWB_df = remove_na(study3_SWB_df)
study3_SWB_df <- pivot_longer(study3_SWB_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_SWB_df, file="SABFI2_Gallardo_Pujol_2018_SWB.Rdata")
write.csv(study3_SWB_df, "SABFI2_Gallardo_Pujol_2018_SWB.csv", row.names=FALSE)

#-------- IntHapp data -------- 
study3_IntHapp_df <- study3_df  |>
  select(starts_with("IntHapp"), Participant)
study3_IntHapp_df <- study3_IntHapp_df |>
  rename(id = Participant) 
study3_IntHapp_df= remove_na(study3_IntHapp_df)
study3_IntHapp_df <- pivot_longer(study3_IntHapp_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_IntHapp_df, file="SABFI2_Gallardo_Pujol_2018_IntHapp.Rdata")
write.csv(study3_IntHapp_df, "SABFI2_Gallardo_Pujol_2018_IntHapp.csv", row.names=FALSE)

#-------- Constru data -------- 
study3_Constru_df <- study3_df  |>
  select(starts_with("Constru"), Participant)

study3_Constru_df <- study3_Constru_df |>
  rename(id = Participant) 
study3_Constru_df= remove_na(study3_Constru_df)
study3_Constru_df <- pivot_longer(study3_Constru_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_Constru_df, file="SABFI2_Gallardo_Pujol_2018_Constru.Rdata")
write.csv(study3_Constru_df, "SABFI2_Gallardo_Pujol_2018_Constru.csv", row.names=FALSE)

#-------- Tight data -------- 
study3_Tight_df <- study3_df  |>
  select(starts_with("Tight"), Participant)

study3_Tight_df <- study3_Tight_df |>
  rename(id = Participant) 
study3_Tight_df= remove_na(study3_Tight_df)
study3_Tight_df <- pivot_longer(study3_Tight_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_Tight_df, file="SABFI2_Gallardo_Pujol_2018_Tight.Rdata")
write.csv(study3_Tight_df, "SABFI2_Gallardo_Pujol_2018_Tight.csv", row.names=FALSE)

#-------- Trust data -------- 
study3_Trust_df <- study3_df  |>
  select(starts_with("Trust"), Participant)

study3_Trust_df <- study3_Trust_df |>
  rename(id = Participant) 
study3_Trust_df= remove_na(study3_Trust_df)
study3_Trust_df <- pivot_longer(study3_Trust_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_Trust_df, file="SABFI2_Gallardo_Pujol_2018_Trust.Rdata")
write.csv(study3_Trust_df, "SABFI2_Gallardo_Pujol_2018_Trust.csv", row.names=FALSE)

#-------- LOT data -------- 
study3_LOT_df <- study3_df  |>
  select(starts_with("LOT"), Participant)

study3_LOT_df <- study3_LOT_df |>
  rename(id = Participant) 
study3_LOT_df= remove_na(study3_LOT_df)
study3_LOT_df <- pivot_longer(study3_LOT_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_LOT_df, file="SABFI2_Gallardo_Pujol_2018_LOT.Rdata")
write.csv(study3_LOT_df, "SABFI2_Gallardo_Pujol_2018_LOT.csv", row.names=FALSE)

#-------- Honest data -------- 
study3_Honest_df <- study3_df  |>
  select(starts_with("Honest"), Participant)

study3_Honest_df <- study3_Honest_df |>
  rename(id = Participant) 
study3_Honest_df= remove_na(study3_Honest_df)
study3_Honest_df <- pivot_longer(study3_Honest_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_Honest_df, file="SABFI2_Gallardo_Pujol_2018_Honest.Rdata")
write.csv(study3_Honest_df, "SABFI2_Gallardo_Pujol_2018_Honest.csv", row.names=FALSE)

#-------- Micro data -------- 
study3_Micro_df <- study3_df  |>
  select(starts_with("Micro"), Participant)

study3_Micro_df <- study3_Micro_df |>
  rename(id = Participant) 
study3_Micro_df = remove_na(study3_Micro_df)
study3_Micro_df <- pivot_longer(study3_Micro_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_Micro_df, file="SABFI2_Gallardo_Pujol_2018_Micro.Rdata")
write.csv(study3_Micro_df, "SABFI2_Gallardo_Pujol_2018_Micro.csv", row.names=FALSE)

#-------- Narq data -------- 
study3_Narq_df <- study3_df  |>
  select(starts_with("Narq"), Participant)

study3_Narq_df <- study3_Narq_df |>
  rename(id = Participant) 
study3_Narq_df = remove_na(study3_Narq_df)
study3_Narq_df <- pivot_longer(study3_Narq_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_Narq_df, file="SABFI2_Gallardo_Pujol_2018_Narq.Rdata")
write.csv(study3_Narq_df, "SABFI2_Gallardo_Pujol_2018_Narq.csv", row.names=FALSE)

#-------- ReligionScale data -------- 
study3_ReligionScale_df <- study3_df  |>
  select(starts_with("ReligionScale"), Participant)

study3_ReligionScale_df <- study3_ReligionScale_df |>
  rename(id = Participant) 
study3_ReligionScale_df = remove_na(study3_ReligionScale_df)
study3_ReligionScale_df <- pivot_longer(study3_ReligionScale_df, cols=-c(id), names_to="item", values_to="resp")

save(study3_ReligionScale_df, file="SABFI2_Gallardo_Pujol_2018_ReligionScale.Rdata")
write.csv(study3_ReligionScale_df, "SABFI2_Gallardo_Pujol_2018_ReligionScale.csv", row.names=FALSE)
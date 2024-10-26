# Paper：
# Data: https://osf.io/hx8qt/

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

NA_data_df <- read_csv("dataCleaned_NA.csv")
BG_data_df <- read_csv("dataCleaned_BG.csv")

NA_data_df <- NA_data_df %>%
  rename(id = ID)
BG_data_df <- BG_data_df %>%
  rename(id = ID)

# ------- Process Risky-Choice Framing, Gain Frame Data ------
RCG_NA_df <- NA_data_df |>
  select(starts_with("RCG"), id, Group)
RCG_NA_df  <- remove_na(RCG_NA_df )
RCG_NA_df <- RCG_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
RCG_NA_df <- RCG_NA_df %>%
  select(-Group, everything(), Group)

RCG_BG_df <- BG_data_df |>
  select(starts_with("RCG"), id, Group)
RCG_BG_df <- RCG_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
RCG_BG_df <- RCG_BG_df %>%
  select(-Group, everything(), Group)

RCG_df <- rbind(RCG_NA_df, RCG_BG_df)

# ------ Process Attribute Framing, Positive Frame ------
AFP_NA_df <- NA_data_df |>
  select(starts_with("AFP"), id, Group)
AFP_NA_df  <- remove_na(AFP_NA_df )
AFP_NA_df <- AFP_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
AFP_NA_df <- AFP_NA_df %>%
  select(-Group, everything(), Group)

AFP_BG_df <- BG_data_df |>
  select(starts_with("AFP"), id, Group)
AFP_BG_df  <- remove_na(AFP_BG_df)
AFP_BG_df <- AFP_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
AFP_BG_df <- AFP_BG_df %>%
  select(-Group, everything(), Group)

AFP_df <- rbind(AFP_NA_df, AFP_BG_df)
RF_df <- rbind(AFP_df, RCG_df)

# ------- Process Risky-Choice Framing, Loss Frame Data ------ 
RCL_NA_df <- NA_data_df |>
  select(starts_with("RCL"), id, Group)
RCL_NA_df  <- remove_na(RCL_NA_df)
RCL_NA_df <- RCL_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
RCL_NA_df <- RCL_NA_df %>%
  select(-Group, everything(), Group)

RCL_BG_df <- BG_data_df |>
  select(starts_with("RCL"), id, Group)
RCL_BG_df  <- remove_na(RCL_BG_df)
RCL_BG_df <- RCL_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
RCL_BG_df <- RCL_BG_df %>%
  select(-Group, everything(), Group)

RCL_df <- rbind(RCL_NA_df, RCL_BG_df)
RF_df <- rbind(RF_df, RCL_df)

# ------ Process Attribute Framing, Negative Frame Data ------
AFN_NA_df <- NA_data_df |>
  select(starts_with("AFN"), id, Group)
AFN_NA_df  <- remove_na(AFN_NA_df)
AFN_NA_df <- AFN_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
AFN_NA_df <- AFN_NA_df %>%
  select(-Group, everything(), Group)

AFN_BG_df <- BG_data_df |>
  select(starts_with("AFN"), id, Group)
AFN_BG_df  <- remove_na(AFN_BG_df)
AFN_BG_df <- AFN_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
AFN_BG_df <- AFN_BG_df %>%
  select(-Group, everything(), Group)

AFN_df <- rbind(AFN_NA_df, AFN_BG_df)
RF_df <- rbind(RF_df, AFN_df)

save(RF_df, file="AOMT_BR_SF_EDPANAB_Geiger_2021_RF.Rdata")
write.csv(RF_df, "AOMT_BR_SF_EDPANAB_Geiger_2021_RF.csv", row.names=FALSE)

# ------ Process The Bullshit Receptivity Scale Data ------
BSR_NA_df <- NA_data_df |>
  select(starts_with("BSR"), id, Group)
BSR_NA_df  <- remove_na(BSR_NA_df )
BSR_NA_df <- BSR_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
BSR_NA_df <- BSR_NA_df %>%
  select(-Group, everything(), Group)

BSR_BG_df <- BG_data_df |>
  select(starts_with("BSR"), id, Group)
BSR_BG_df  <- remove_na(BSR_BG_df)
BSR_BG_df <- BSR_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
BSR_BG_df <- BSR_BG_df %>%
  select(-Group, everything(), Group)

BSR_df <- rbind(BSR_NA_df, BSR_BG_df)

# ------ Process Motivational Statements Data ------
MOT_NA_df <- NA_data_df |>
  select(starts_with("MOT"), id, Group)
MOT_NA_df  <- remove_na(MOT_NA_df)
MOT_NA_df <- MOT_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
MOT_NA_df <- MOT_NA_df %>%
  select(-Group, everything(), Group)

MOT_BG_df <- BG_data_df |>
  select(starts_with("MOT"), id, Group)
MOT_BG_df  <- remove_na(MOT_BG_df)
MOT_BG_df <- MOT_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
MOT_BG_df <- MOT_BG_df %>%
  select(-Group, everything(), Group)

MOT_df <- rbind(MOT_NA_df, MOT_BG_df)
BRS_df <- rbind(BSR_df, MOT_df)
save(BRS_df, file="AOMT_BR_SF_EDPANAB_Geiger_2021_BRS.Rdata")
write.csv(BRS_df, "AOMT_BR_SF_EDPANAB_Geiger_2021_BRS.csv", row.names=FALSE)

# ------ Process Actively Open-Minded Thinking Scale Data ------
AOT_NA_df <- NA_data_df |>
  select(starts_with("AOT"), id, Group)
AOT_NA_df  <- remove_na(AOT_NA_df)
AOT_NA_df <- AOT_NA_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
AOT_NA_df <- AOT_NA_df %>%
  select(-Group, everything(), Group)

AOT_BG_df <- BG_data_df |>
  select(starts_with("AOT"), id, Group)
AOT_BG_df  <- remove_na(AOT_BG_df)
AOT_BG_df <- AOT_BG_df %>%
  pivot_longer(cols = -c(id, Group), names_to = "item", values_to = "resp")
AOT_BG_df <- AOT_BG_df %>%
  select(-Group, everything(), Group)

AOT_df <- rbind(AOT_NA_df, AOT_BG_df)
save(AOT_df, file="AOMT_BR_SF_EDPANAB_Geiger_2021_AOT.Rdata")
write.csv(AOT_df, "AOMT_BR_SF_EDPANAB_Geiger_2021_AOT.csv", row.names=FALSE)

# Paper：https://osf.io/ad6b3/
# Data:https://pubmed.ncbi.nlm.nih.gov/34639633/

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) -1)), ]
  return(df)
}

data_df <- read_csv("PROMIS_UE_data.csv")
data_df  <- data_df %>%
  rename(id = RID)

# ------ Process Short Form Data ------
PROMIS_Physical_Function_Short_Form_df <- data_df |>
  select(PFA4:PFA11, id)
PROMIS_Physical_Function_Short_Form_df <- remove_na(PROMIS_Physical_Function_Short_Form_df )
PROMIS_Physical_Function_Short_Form_df <- PROMIS_Physical_Function_Short_Form_df  %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

# ------ Process Upper Extremity Data ------
PROMIS_Physical_Function_Upper_Extermity_df <- data_df |>
  select(QSD6, PFA14:PFM18, id)
PROMIS_Physical_Function_Upper_Extermity_df  <- remove_na(PROMIS_Physical_Function_Upper_Extermity_df)
PROMIS_Physical_Function_Upper_Extermity_df <- PROMIS_Physical_Function_Upper_Extermity_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

# ------ Process Flexibility Level Data------
Flexilevel_Scale_of_Shoulder_Function_df <- data_df |>
  select(QFLEXB1:QFLEXH15, id)
Flexilevel_Scale_of_Shoulder_Function_df  <- remove_na(Flexilevel_Scale_of_Shoulder_Function_df)
Flexilevel_Scale_of_Shoulder_Function_df <- Flexilevel_Scale_of_Shoulder_Function_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")
Flexilevel_Scale_of_Shoulder_Function_df$resp <- Flexilevel_Scale_of_Shoulder_Function_df$resp + 1

df <- rbind(PROMIS_Physical_Function_Short_Form_df, PROMIS_Physical_Function_Upper_Extermity_df)
df<- rbind(df, Flexilevel_Scale_of_Shoulder_Function_df)
save(Flexilevel_Scale_of_Shoulder_Function_df, file="PROMISPFUE_2.0E_Gershon_2019_PROMIS.Rdata")
write.csv(Flexilevel_Scale_of_Shoulder_Function_df, "PROMISPFUE_2.0E_Gershon_2019_PROMIS.csv", row.names=FALSE)


# Paper: 
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IBFK5H
library(haven)
library(dplyr)
library(tidyr)

rm(list = ls())

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

FACIT_df <- read_sav("NWHR0004_FINAL_OUTPUT.sav")

# ------ Dataset Pre-process ------
FACIT_df <- FACIT_df |>
  rename(id=CaseID)

FACIT_df[] <- lapply(FACIT_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

FACIT_df <- FACIT_df |>
  rename(date=STARTTIME)
FACIT_df$date <- as.numeric(as.POSIXct(FACIT_df$date, format="%a %b %d %H:%M:%S %Y", tz="UTC"))

FACIT_clinic10now1_df <- FACIT_df |>
  select(starts_with("clinic10now1"), id, date, -clinic10now1_t)
FACIT_clinic10now1_df <- remove_na(FACIT_clinic10now1_df)
FACIT_clinic10now1_df <- pivot_longer(FACIT_clinic10now1_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_clinic10now1_df[FACIT_clinic10now1_df == 2] <- 0
FACIT_clinic10now1_df[FACIT_clinic10now1_df == 8] <- NA
FACIT_clinic10now1_df[FACIT_clinic10now1_df == 9] <- NA

save(FACIT_clinic10now1_df, file="FACIT_YOUNT_2021_clinic10now1.Rdata")
write.csv(FACIT_clinic10now1_df, "FACIT_YOUNT_2021_clinic10now1.csv", row.names=FALSE)


FACIT_clinic10ever1_df <- FACIT_df |>
  select(starts_with("clinic10ever1"), id, date,-clinic10ever1_t)
FACIT_clinic10ever1_df <- remove_na(FACIT_clinic10ever1_df)
FACIT_clinic10ever1_df <- pivot_longer(FACIT_clinic10ever1_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_clinic10ever1_df[FACIT_clinic10ever1_df == 2] <- 0
FACIT_clinic10ever1_df[FACIT_clinic10ever1_df == 8] <- NA
FACIT_clinic10ever1_df[FACIT_clinic10ever1_df == 9] <- NA

save(FACIT_clinic10ever1_df, file="FACIT_YOUNT_2021_clinic10ever1.Rdata")
write.csv(FACIT_clinic10ever1_df, "FACIT_YOUNT_2021_clinic10ever1.csv", row.names=FALSE)

FACIT_othermeds_df <- FACIT_df |>
  select(starts_with("othermeds"), id, date, -othermeds1_t)
FACIT_othermeds_df  <- remove_na(FACIT_othermeds_df )
FACIT_othermeds_df  <- pivot_longer(FACIT_othermeds_df , cols=-c(id, date), names_to="item", values_to="resp")

FACIT_othermeds_df [FACIT_othermeds_df == 2] <- 0
FACIT_othermeds_df[FACIT_othermeds_df  == 8] <- NA
FACIT_othermeds_df [FACIT_othermeds_df == 9] <- NA

save(FACIT_othermeds_df , file="FACIT_YOUNT_2021_clinic10othermeds.Rdata")
write.csv(FACIT_othermeds_df , "FACIT_YOUNT_2021_clinic10othermeds.csv", row.names=FALSE)

#---------facitx data
FACIT_facitx_df <- FACIT_df |>
  select(starts_with("facitx"), id, date)
FACIT_facitx_df  <- remove_na(FACIT_facitx_df )
FACIT_facitx_df <- pivot_longer(FACIT_facitx_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_a2facitx_df <- FACIT_df |>
  select(starts_with("a2_facitx"), id, date)
FACIT_a2facitx_df  <- remove_na(FACIT_a2facitx_df )
FACIT_a2facitx_df <- pivot_longer(FACIT_a2facitx_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_facitx_df $wave <- 0
FACIT_a2facitx_df$wave <- 1

Facitx_df <- rbind(FACIT_facitx_df,FACIT_a2facitx_df )

Facitx_df[Facitx_df == 8] <- NA
Facitx_df[Facitx_df == 9] <- NA

save(Facitx_df, file="FACIT_YOUNT_2021_Facitx.Rdata")
write.csv(Facitx_df, "FACIT_YOUNT_2021_Facitx.csv", row.names=FALSE)

#---------facit2x data
FACIT_facit2x_df <- FACIT_df |>
  select(starts_with("facit2x"), id, date)
FACIT_facit2x_df  <- remove_na(FACIT_facit2x_df )
FACIT_facit2x_df <- pivot_longer(FACIT_facit2x_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_a2facit2x_df <- FACIT_df |>
  select(starts_with("a2_facit2x"), id, date)
FACIT_a2facit2x_df  <- remove_na(FACIT_a2facit2x_df )
FACIT_a2facit2x_df <- pivot_longer(FACIT_a2facit2x_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_facit2x_df $wave <- 0
FACIT_a2facit2x_df$wave <- 1

Facit2x_df <- rbind(FACIT_facit2x_df,FACIT_a2facit2x_df )
Facit2x_df[Facit2x_df == 8] <- NA
Facit2x_df[Facit2x_df == 9] <- NA

save(Facit2x_df, file="FACIT_YOUNT_2021_Facit2x.Rdata")
write.csv(Facit2x_df, "FACIT_YOUNT_2021_Facit2x.csv", row.names=FALSE)

#---------facit3x data
FACIT_facit3x_df <- FACIT_df |>
  select(starts_with("facit3x"), id, date)
FACIT_facit3x_df  <- remove_na(FACIT_facit3x_df )
FACIT_facit3x_df <- pivot_longer(FACIT_facit3x_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_a2facit3x_df <- FACIT_df |>
  select(starts_with("a2_facit3x"), id, date)
FACIT_a2facit3x_df  <- remove_na(FACIT_a2facit3x_df )
FACIT_a2facit3x_df <- pivot_longer(FACIT_a2facit3x_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_facit3x_df $wave <- 0
FACIT_a2facit3x_df$wave <- 1

Facit3x_df <- rbind(FACIT_facit3x_df,FACIT_a2facit3x_df )
Facit3x_df[Facit3x_df == 8] <- NA
Facit3x_df[Facit3x_df == 9] <- NA

save(Facit3x_df, file="FACIT_YOUNT_2021_Facit3x.Rdata")
write.csv(Facit3x_df, "FACIT_YOUNT_2021_Facit3x.csv", row.names=FALSE)

#---------facitox data
FACIT_facitox_df <- FACIT_df |>
  select(starts_with("facitox"), id, date)
FACIT_facitox_df  <- remove_na(FACIT_facitox_df )
FACIT_facitox_df <- pivot_longer(FACIT_facitox_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_a2facitox_df <- FACIT_df |>
  select(starts_with("a2_facitox"), id, date)
FACIT_a2facitox_df  <- remove_na(FACIT_a2facitox_df )
FACIT_a2facitox_df <- pivot_longer(FACIT_a2facitox_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_facitox_df $wave <- 0
FACIT_a2facitox_df$wave <- 1

Facitox_df <- rbind(FACIT_facitox_df,FACIT_a2facitox_df )

items_to_exclude <- c("facitox29_x", "facitox31_x", "facitox32_x", "facitox33_x"
                      ,"a2_facitox29_x","a2_facitox31_x","a2_facitox32_x","a2_facitox33_x")

# Replace 8 and 9 with NA only when 'item' column is not in items_to_exclude
Facitox_df <- Facitox_df |>
  mutate(resp = ifelse(!(item %in% items_to_exclude) & resp %in% c(8, 9), NA, resp))

save(Facitox_df, file="FACIT_YOUNT_2021_Facitox.Rdata")
write.csv(Facitox_df, "FACIT_YOUNT_2021_Facitox.csv", row.names=FALSE)

#-------randx data
FACIT_randx_df <- FACIT_df |>
  select(starts_with("randx"), id,date)
FACIT_randx_df <- remove_na(FACIT_randx_df)
FACIT_randx_df<- pivot_longer(FACIT_randx_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_randx_df[FACIT_randx_df == 8] <- NA
FACIT_randx_df[FACIT_randx_df == 9] <- NA

save(FACIT_randx_df, file="FACIT_YOUNT_2021_randx.Rdata")
write.csv(FACIT_randx_df, "FACIT_YOUNT_2021_randx.csv", row.names=FALSE)

#-------hadsx data
FACIT_hadsx_df <- FACIT_df |>
  select(starts_with("hadsx"), id, date)
FACIT_hadsx_df <- remove_na(FACIT_hadsx_df)
FACIT_hadsx_df <- pivot_longer(FACIT_hadsx_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_hadsx_df[FACIT_hadsx_df == 8] <- NA
FACIT_hadsx_df[FACIT_hadsx_df == 9] <- NA

save(FACIT_hadsx_df, file="FACIT_YOUNT_2021_hadsx.Rdata")
write.csv(FACIT_hadsx_df, "FACIT_YOUNT_2021_hadsx.csv", row.names=FALSE)

#------crqsasx data
FACIT_crqsasx_df <- FACIT_df |>
  select(starts_with("crqsasx"), id, date)
FACIT_crqsasx_df <- remove_na(FACIT_crqsasx_df )
FACIT_crqsasx_df <- pivot_longer(FACIT_crqsasx_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_crqsasx_df[FACIT_crqsasx_df == 8] <- NA
FACIT_crqsasx_df[FACIT_crqsasx_df == 9] <- NA
FACIT_crqsasx_df[FACIT_crqsasx_df == 98] <- NA
FACIT_crqsasx_df[FACIT_crqsasx_df == 99] <- NA


save(FACIT_crqsasx_df, file="FACIT_YOUNT_2021_crqsasx.Rdata")
write.csv(FACIT_crqsasx_df, "FACIT_YOUNT_2021_crqsasx.csv", row.names=FALSE)


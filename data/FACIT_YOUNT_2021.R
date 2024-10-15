# Paper: 
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IBFK5H
library(haven)
library(dplyr)
library(tidyr)

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

# ------ Process Clinic(now + ever) Datasets ------

FACIT_clinic10now1_df <- FACIT_df |>
  select(starts_with("clinic10now1"), id, date, -clinic10now1_t)
FACIT_clinic10now1_df <- remove_na(FACIT_clinic10now1_df)
FACIT_clinic10now1_df <- pivot_longer(FACIT_clinic10now1_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_clinic10now1_df[FACIT_clinic10now1_df == 2] <- 0
FACIT_clinic10now1_df[FACIT_clinic10now1_df == 8] <- NA
FACIT_clinic10now1_df[FACIT_clinic10now1_df == 9] <- NA

FACIT_clinic10ever1_df <- FACIT_df |>
  select(starts_with("clinic10ever1"), id, date,-clinic10ever1_t)
FACIT_clinic10ever1_df <- remove_na(FACIT_clinic10ever1_df)
FACIT_clinic10ever1_df <- pivot_longer(FACIT_clinic10ever1_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_clinic10ever1_df[FACIT_clinic10ever1_df == 2] <- 0
FACIT_clinic10ever1_df[FACIT_clinic10ever1_df == 8] <- NA
FACIT_clinic10ever1_df[FACIT_clinic10ever1_df == 9] <- NA

FACIT_clinic_df <- rbind(FACIT_clinic10ever1_df, FACIT_clinic10now1_df)

save(FACIT_clinic10ever1_df, file="FACIT_YOUNT_2021_clinic10.Rdata")
write.csv(FACIT_clinic10ever1_df, "FACIT_YOUNT_2021_clinic10.csv", row.names=FALSE)

#--------- Process Limitations(Facitx + Facit2x) Dataset ------
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
Facitx_df$resp <- as.integer(Facitx_df$resp)

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
Facit2x_df$resp <- as.integer(Facit2x_df$resp)

Facit_limitations_df <- rbind(Facit2x_df, Facitx_df)

save(Facit2x_df, file="FACIT_YOUNT_2021_limitations.Rdata")
write.csv(Facit2x_df, "FACIT_YOUNT_2021_limitations.csv", row.names=FALSE)

#------- Process hadsx Dataset ------
FACIT_hadsx_df <- FACIT_df |>
  select(starts_with("hadsx"), id, date)
FACIT_hadsx_df <- remove_na(FACIT_hadsx_df)
FACIT_hadsx_df <- pivot_longer(FACIT_hadsx_df, cols=-c(id, date), names_to="item", values_to="resp")

FACIT_hadsx_df[FACIT_hadsx_df == 8] <- NA
FACIT_hadsx_df[FACIT_hadsx_df == 9] <- NA

save(FACIT_hadsx_df, file="FACIT_YOUNT_2021_hadsx.Rdata")
write.csv(FACIT_hadsx_df, "FACIT_YOUNT_2021_hadsx.csv", row.names=FALSE)

#------ Process crqsasx Dataset ------
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

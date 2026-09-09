# Paper：https://pmc.ncbi.nlm.nih.gov/articles/PMC11392422/#sec002
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LGXP5A 

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

data_df <- read_sav("BAS2_Children_dataset.sav")
data_df <- data_df %>%
  rename(id = CODE)

# Two CODEs are held by two DIFFERENT CHILDREN each (#1842). `2_2BIMA` and
# `2_2BISE` appear twice in the source, and the pairs are not re-tests:
#
#   2_2BIMA   gender 2 vs 1, 30.0 kg / 1.30 m vs 27.5 kg / 1.33 m
#   2_2BISE   age 9 vs 8,    33.0 kg / 1.40 m vs 21.0 kg / 1.20 m
#
# 12 kg and 20 cm apart. That is the whole of this table's dup_id_item flag --
# 2 codes x 24 items = 48 rows -- and the block H prescription to dedupe it
# would have deleted two real children.
#
# There is no sample label to namespace with, as there was for the other #1842
# collisions, so the repeated code gets an occurrence suffix. The order within a
# code is arbitrary and it does not matter: they are anonymous, and the point is
# only that they stop being one person. "." is used because "_" occurs in the
# source codes.
#
# The source also carries Gender/Age/Weight/Height/BMI per row, which is what
# distinguishes them; none of it is currently shipped. Worth adding as cov_
# columns, but that is a separate change from making the ids honest.
dup_code <- data_df$id %in% data_df$id[duplicated(data_df$id)]
if (any(dup_code)) {
  n_dup <- length(unique(data_df$id[dup_code]))
  data_df$id[dup_code] <- paste0(data_df$id[dup_code], ".",
                                 ave(seq_len(sum(dup_code)),
                                     data_df$id[dup_code], FUN = seq_along))
  message(sprintf("PEPABAS2C: %d code(s) held by more than one child; suffixed %d row(s)",
                  n_dup, sum(dup_code)))
}
stopifnot(!anyDuplicated(data_df$id))

data_df[] <- lapply(data_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

data_df[] <- lapply(data_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

SPP_df <- data_df |>
  select(starts_with("SPP"), id)
SPP_df <- remove_na(SPP_df)
SPP_df <- pivot_longer(SPP_df, cols=-c(id), names_to="item", values_to="resp")

BAS_df <- data_df |>
  select(starts_with("BAS"),-ends_with("sum"),-ends_with("retest"), id)
BAS_df <- remove_na(BAS_df)
BAS_df <- pivot_longer(BAS_df, cols=-c(id), names_to="item", values_to="resp")

Body_df <- data_df |>
  select(starts_with("Body"),-ends_with("sum"),-ends_with("retest"), id)
Body_df <- remove_na(Body_df)
Body_df <- pivot_longer(Body_df, cols=-c(id), names_to="item", values_to="resp")

Body_df$resp <- as.numeric(Body_df$resp)
df <- rbind(Body_df, BAS_df)
df <- rbind(df, SPP_df)

# 99 is the study's missing code, and it must be removed explicitly rather than
# left to whichever file this is run against (#1842).
#
# The published table carries 5 rows with a NULL `resp` and no 99s, so the .sav
# the original build read had these cells stored as SPSS user-missing. Harvard
# Dataverse does not serve that .sav -- it ingested it to `.tab`, where the user
# missing values are materialised as the literal 99. So a rebuild from the
# archive would publish seven 99s as responses, and the current table publishes
# five NULLs; recoding here is correct against both files.
#
# Seven cells: SPP6, SPP16, SPP18, SPP22, Body_satisfaction1 and
# Body_satisfaction2 (x2). Two of them are the same respondent's only two Body
# items, which is why remove_na() drops that row entirely and the live table is
# 4,846 rather than 4,848.
MISSING_CODE <- 99
df$resp <- as.numeric(df$resp)
n_missing <- sum(df$resp == MISSING_CODE, na.rm = TRUE)
df <- df[!is.na(df$resp) & df$resp != MISSING_CODE, ]
message(sprintf("PEPABAS2C: dropped %d response(s) coded %d and any NA",
                n_missing, MISSING_CODE))

## No id+item pair may repeat once the collided codes are separated.
stopifnot(!anyDuplicated(df[, c("id", "item")]))
stopifnot(!any(is.na(df$resp)))

save(df, file="PEPABAS2C_Kubicka_2024.Rdata")
write.csv(df, "PEPABAS2C_Kubicka_2024.csv", row.names=FALSE)

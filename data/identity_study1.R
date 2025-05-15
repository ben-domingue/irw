# use packages
library(haven)
library(devtools)
library(redivis)
library(tidyverse)
library(readr)
library(dplyr)
library(tidyr)

# load dataset
df <- read_sav("IRS1.sav")

# convert column names to lowercase
names(df) <- tolower(names(df))

# renames covariates and adds id
df <- df %>%
  mutate(id = seq(1, n())) %>%
  rename(
    cov_gender = gender,
    cov_age = age,
    cov_education = education,
    cov_income = income,
    cov_identity = identity
  )

# convert to cvs
write_csv(df, "IRS1.csv")

# drops non-response variables from dataset
df <- df[ , !(names(df) %in% c("attentioncheck1", "attentioncheck2", "intergroupanxiety", "perceiveddiscrimination", "grit", "collectivese", "identitydemand", "identityresource", "interracialtrust", "behavioralavoidance", "perceivedstress", "groupidentification"))]

# drops recoded versions of original response variables
df <- df[ , !(names(df) %in% c("cse2r", "cse4r", "cse5r", "cse7r", "cse10r", "cse12r", "cse13r", "cse15r", "grit1r", "grit3r", "grit5r", "grit6r", "pss4r", "pss5r", "pss7r", "pss8r"))]

# generate item
question_cols <- c(
  "irsr1", "irsd1", "irsd2", "irsd3", "irsd4", "irsr2", "irsd5", "irsr3", "irsr4", "irsr5",
  "cse1", "cse2", "cse3", "cse4", "cse5", "cse6", "cse7", "cse8", "cse9", "cse10",
  "cse11", "cse12", "cse13", "cse14", "cse15", "cse16", "grit1", "grit2", "grit3",
  "grit4", "grit5", "grit6", "grit7", "grit8", "selfesteem", "pds1", "pds2", "pds3", "pds4",
  "pds5", "pds6", "pds7", "pds8", "pds9", "pia1", "pia2", "pia3", "pia4", "pit1",
  "pit2", "pit3", "pit4", "pba1", "pba2", "pba3", "pba4", "pba5", "pba6",
  "pba7", "pba8", "pba9", "pba10", "pba11", "pss1", "pss2", "pss3", "pss4", "pss5",
  "pss6", "pss7", "pss8", "pss9", "pss10", "gi1", "gi2", "gi3", "gi4"
)

# select and prepare data
dfQ_resp <- df %>%
  select(id, all_of(question_cols), starts_with("cov"))

# reshape the data
dfQ_resp <- df %>%
  select(id, all_of(question_cols), starts_with("cov")) %>%
  pivot_longer(
    cols = all_of(question_cols),
    names_to = "item",
    values_to = "resp"
  )

# takes off any unwanted labeling from item and resp columns
attr(dfQ_resp$item, "label") <- NULL
attr(dfQ_resp$resp, "label") <- NULL

# views final dataset
view(dfQ_resp)

### saves final dataset as cvs
write_csv(dfQ_resp, "identity_study1.csv")

# splits the main table into different files based on the construct
base_items <- c("irsr", "irsd", "cse", "grit", "selfesteem", "pds", "pia", "pit", "pba", "pss", "gi")

for (item_name in base_items) {
  assign(
    item_name,
    subset(dfQ_resp, grepl(paste0("^", item_name), item))
  )
}

### saves final datasets as cvs
write_csv(cse, "identity_study1_cse.csv")
write_csv(irsr, "identity_study1_irsr.csv")
write_csv(irsd, "identity_study1_irsd.csv")
write_csv(grit, "identity_study1_grit.csv")
write_csv(selfesteem, "identity_study1_selfesteem.csv")
write_csv(pds, "identity_study1_pds.csv")
write_csv(pia, "identity_study1_pia.csv")
write_csv(pit, "identity_study1_pit.csv")
write_csv(pba, "identity_study1_pba.csv")
write_csv(pss, "identity_study1_pss.csv")
write_csv(gi, "identity_study1_gi.csv")


### optional Stata Do Filescommands for reference

# check accuracy of commands by comparing total observations in combined datasets with dfQ_resp; should net to zero
nrow(dfQ_resp)-(nrow(cse)+nrow(irsr)+nrow(irsd)+nrow(grit)+nrow(selfesteem)+nrow(pds)+nrow(pia)+nrow(pit)+nrow(pba)+nrow(pss)+nrow(gi))

# views different datasets
view(dfQ_resp)
view(cse)
view(irsr)
view(irsd)
view(selfesteem)
view(pds)
view(pia)
view(pit)
view(pba)
view(pss)
view(gi)

# prints column names
print(colnames(dfQ_resp))

# clears environment
rm(list = ls())
# Paper: https://onlinelibrary.wiley.com/doi/epdf/10.1002/pam.22643
# Data: https://www.dropbox.com/scl/fo/jp41djskes00ssrbzm4ez/ABgU29_SZ3L4jpeNRIFVpHo?rlkey=tj7ojr4spweeupyyiidisi103&e=1&dl=0
library(haven)
library(dplyr)
library(tidyr)

ad_df <- read_dta("adolescent_cleaned.dta")
parent_df <- read_dta("parent_cleaned.dta")

# ------ Data Pre-process for Parent Data------
# Remove households that didn't give consents.
parent_df <- parent_df[parent_df$consent_disagree != 1, ]
# Remove households that didn't give correct info
parent_df <- parent_df[parent_df$multi_phone != 1, ]
parent_df <- parent_df[parent_df$wrong_vig != 1, ]
parent_df <- parent_df[parent_df$wrong_treatment != 1, ]
parent_df <- parent_df[parent_df$wrong_enum_gender != 1, ]

# ------ Process Parent Data ------
parent_df <- parent_df |>
  rename(id=HHID, treat=treatment) |>
  select(-starts_with("consent"), -starts_with("wrong"), -counsellor_willingnesstopay, -mh_child_time) |>
  select(id, treat, ends_with("major"), starts_with("mh"), starts_with("not"), starts_with("vig"), starts_with("covid"),
         starts_with("counsel"), starts_with("less"))

parent_df[] <- lapply(parent_df, function(x) as.numeric(as.character(x))) # Remove attributes
parent_df[parent_df == -98] <- NA
parent_df <- pivot_longer(parent_df, cols=-c(id, treat), names_to="item", values_to="resp")

save(parent_df, file="EEN_Lacey_2024_Parent.Rdata")
write.csv(parent_df, "EEN_Lacey_2024_Parent.csv", row.names=FALSE)

# ------ Data Pre-process for Children Data------
# Remove households that didn't give consents.
ad_df <- ad_df[ad_df$consent != 0, ]
# Remove households that didn't give correct info
ad_df <- ad_df[ad_df$multi_phone != 1, ]
ad_df <- ad_df[ad_df$wrong_vig != 1, ]
ad_df <- ad_df[ad_df$wrong_treatment != 1, ]
ad_df <- ad_df[ad_df$wrong_enum_gender != 1, ]

# ------ Process Children Data ------
ad_df <- ad_df |>
  rename(id=HHID, treat=combine_treat) |>
  select(id, treat, ends_with("major"), starts_with("man"), starts_with("counsel"),
         group_samesex, Howcomfortabledidyoufeel, helpline_willcall)
ad_df[] <- lapply(ad_df, function(x) as.numeric(as.character(x))) # Remove attributes
ad_df[ad_df == -98] <- NA
ad_df <- pivot_longer(ad_df, cols=-c(id, treat), names_to="item", values_to="resp")

save(ad_df, file="EEN_Lacey_2024_Children.Rdata")
write.csv(ad_df, "EEN_Lacey_2024_Children.csv", row.names=FALSE)

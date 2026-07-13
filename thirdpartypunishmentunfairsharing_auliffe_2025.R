library(dplyr)
library(tidyr)

data <- read.csv("/Users/rubinashrestha/Downloads/tpix.canada.csv")

data <- rename(data,
               id            = new.id,
               cov_age       = age.year,
               cov_age_calc  = age.calc,
               cov_age_group = age.group,
               cov_gender    = gender,
               cov_condition = condition,
               cov_site      = site
)

data_long <- pivot_longer(data,
                          cols = starts_with("t"),
                          names_to = "item",
                          values_to = "resp",
                          values_transform = list(resp = as.character)
)

data_long <- mutate(data_long, resp = na_if(resp, "."))
data_long <- filter(data_long, !is.na(resp))

write.csv(
  data_long,
  "/Users/rubinashrestha/Downloads/thirdpartypunishmentunfairsharing_auliffe_2025_canada.csv",
  row.names = FALSE
)

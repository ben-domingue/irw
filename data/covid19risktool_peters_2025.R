library(dplyr)
library(tidyr)

data <- read.csv("/Users/rubinashrestha/Downloads/YCR-dataPipeline--sid-100121--rids-3145-4111.csv")

# Convert dates to Unix time IN PLACE
data$submitdate <- as.numeric(
  as.POSIXct(data$submitdate, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
)
data$startdate <- as.numeric(
  as.POSIXct(data$startdate, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
)
data$datestamp <- as.numeric(
  as.POSIXct(data$datestamp, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
)

data <- rename(data,
               id = ï..id,
               submitdate_family = submitdate,
               datestamp_family = datestamp,
               cov_lastpage = lastpage,
               cov_language = startlanguage,
               cov_seed = seed,
               cov_country = country,
               cov_age = age,
               cov_gender = gender
)

data_long <- data %>%
  pivot_longer(
    cols = -id,
    names_to = "item",
    values_to = "resp",
    values_transform = list(resp = as.character)
  ) %>%
  mutate(resp = replace_na(resp, "0")) %>%
  mutate(resp = if_else(resp == "", "0", resp))

write.csv(
  data_long,
  "/Users/rubinashrestha/Downloads/covid19risktool_peters_2025_100121-3145-4111.csv",
  row.names = FALSE
)

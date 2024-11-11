library(readxl)
library(tidyr)
library(dplyr)

df2 <- read_xlsx('jeehp-21-18-suppl2.xlsx')
df3 <- read_xlsx('jeehp-21-18-suppl3.xlsx')

df3 <- df3 %>%
  mutate(joined_indicator = TRUE)

merged <- df2 %>%
  left_join(df3, by = c("taker_id", "item_code", "is_correct")) %>%
  mutate(SEM_type = ifelse(is.na(joined_indicator), "0.25", "0.25_0.3")) %>%
  select(taker_id, item_code, SEM_type, is_correct)

merged <- merged %>%
  rename(id = taker_id, item = item_code, resp = is_correct) %>%
  mutate(resp = recode(resp, "Y" = 1, "N" = 0))

write.csv(merged, "CAT_DongGiSeo_2024.csv", row.names=FALSE)

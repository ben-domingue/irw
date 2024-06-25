#paper. https://link.springer.com/article/10.3758/s13428-023-02124-2
#study 3
library(readr)
library(dplyr)
library(tidyr)

data <- read_csv("MIST - Sample 3 - Dataset (Wide).csv")

data1 <- data %>%
  select(id, ends_with(".T1")) %>%
  mutate(`time` = 'T1')%>%
  rename_at(vars(ends_with(".T1")), ~ sub(".T1", "", .))

data2 <- data %>%
  select(id, ends_with(".T2")) %>%
  mutate(`time` = 'T2')%>%
  rename_at(vars(ends_with(".T2")), ~ sub(".T2", "", .))

data1_long <- pivot_longer(data1, cols = -c(id, `time`), names_to = "item", values_to = "resp")
data2_long <- pivot_longer(data2, cols = -c(id, `time`), names_to = "item", values_to = "resp")

data_final <- bind_rows(data1_long, data2_long)

saveRDS(data_final, "MIST_study3.RData")         

write.csv(data_final, "MIST_study3.csv", row.names = FALSE)

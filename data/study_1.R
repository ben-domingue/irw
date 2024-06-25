#paper. https://link.springer.com/article/10.3758/s13428-023-02124-2
#study 1
library(dplyr)
library(tidyr)

data <- read.csv("MIST - Sample 1 - Clean Dataset.csv")

data <- data %>%
  mutate(id = row_number())

columns_list <- list(
  MIST = c("id", paste0("MIST_", 1:100)),
  BN = c("id", paste0("BN_R", 1:3), paste0("BN_I", 1:3),paste0("BN_P", 1:3),paste0("BN_C", 1:3),paste0("BN_D", 1:3),paste0("BN_E", 1:3),paste0("BN_T", 1:3)),
  BSR = c("id", paste0("BSR_", 1:10)),
  CR = c("id", paste0("CRT1_", 1:3), paste0("CRT2_", 1:4)),
  COVID_Compliance = c("id", paste0("COVID_Compliance_", 1:5)),
  MIST_T2 = c("id", paste0("MIST_", 1:20, "_T2")),
  CV19 = c("id", paste0("CV19_", 1:7))
)

for (name in names(columns_list)) {
  data1 <- data %>%
    select(all_of(columns_list[[name]])) %>%
    pivot_longer(cols = -id, names_to = "item", values_to = "resp")
  
  save(data1, file = paste0(name, ".RData"))
  write.csv(data1, paste0(name, ".csv"), row.names = FALSE)
}

factcheck_columns <- c("id", paste0("FactCheck_F", 1:15),paste0("FactCheck_T", 1:15), "StartDate")
factcheck_data <- data %>%
  select(all_of(factcheck_columns)) %>%
  mutate(Unix_time = as.numeric(as.POSIXct(StartDate, format="%Y-%m-%d %H:%M:%S", tz="UTC"))) %>%
  select(-StartDate) %>%
  pivot_longer(cols = -c(id, Unix_time), names_to = "item", values_to = "resp")

factcheck_columns_t2 <- c("id", paste0("FactCheck_F", 1:15, "_T2"),paste0("FactCheck_T", 1:15), "StartDate_T2")
factcheck_data_t2 <- data %>%
  select(all_of(factcheck_columns_t2)) %>%
  mutate(Unix_time = as.numeric(as.POSIXct(StartDate_T2, format="%Y-%m-%d %H:%M:%S", tz="UTC"))) %>%
  select(-StartDate_T2) %>%
  pivot_longer(cols = -c(id, Unix_time), names_to = "item", values_to = "resp")

factcheck_combined <- bind_rows(factcheck_data, factcheck_data_t2)

save(factcheck_combined, file = "FactCheck.RData")
write.csv(factcheck_combined, "FactCheck.csv", row.names = FALSE)

cmq_columns <- c("id", paste0("CMQ_", 1:5), "StartDate")
cmq_data <- data %>%
  select(all_of(cmq_columns)) %>%
  mutate(Unix_time = as.numeric(as.POSIXct(StartDate, format="%Y-%m-%d %H:%M:%S", tz="UTC"))) %>%
  select(-StartDate) %>%
  pivot_longer(cols = -c(id, Unix_time), names_to = "item", values_to = "resp")

cmq_columns_t2 <- c("id", paste0("CMQ_", 1:5, "_T2"), "StartDate_T2")
cmq_data_t2 <- data %>%
  select(all_of(cmq_columns_t2)) %>%
  mutate(Unix_time = as.numeric(as.POSIXct(StartDate_T2, format="%Y-%m-%d %H:%M:%S", tz="UTC"))) %>%
  select(-StartDate_T2) %>%
  pivot_longer(cols = -c(id, Unix_time), names_to = "item", values_to = "resp")

cmq_combined <- bind_rows(cmq_data, cmq_data_t2)

save(cmq_combined, file = "CMQ.RData")
write.csv(cmq_combined, "CMQ.csv", row.names = FALSE)

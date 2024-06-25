#paper. https://link.springer.com/article/10.3758/s13428-023-02124-2
#study 2a,2b,2c,2d
library(dplyr)
library(tidyr)
library(readr)

a <- read_csv("MIST - Sample 2A - Clean Dataset.csv")
b <- read_csv("MIST - Sample 2B - Clean Dataset.csv")
c <- read_csv("MIST - Sample 2C - Clean Dataset.csv")
d <- read_csv("MIST - Sample 2D - Clean Dataset.csv")

datasets <- list(a = a, b = b, c = c, d = d)
datasets <- lapply(datasets, function(df) {
  df %>% mutate(id = row_number())
})

a <- datasets$a

columns_a <- list(
  AOT = paste0("AOT_", 1:10),
  misinfo = paste0("misinfo_", 1:9),
  CV19 = c('CV19_Posters', 'CV19_SocialMedia', 'CV19_Media', 'CV19_Government', 'CV19_Workplace', 'CV19_Friends', 'CV19_WHO')
)

for (name in names(columns_a)) {
  data_a <- a %>%
    select(id, all_of(columns_a[[name]])) %>%
    pivot_longer(cols = -id, names_to = "item", values_to = "resp")
  
  save(data_a, file = paste0(name, ".RData"))
  write.csv(data_a, paste0(name, ".csv"), row.names = FALSE)
}

b <- datasets$b

columns_b <- list(
  DEPICT = paste0("DEPICT_", 1:12),
  CV = paste0("GV_", 1:18),
  BSR = paste0("BSR_", 1:10),
  CMQ = paste0("CMQ_", 1:5),
  BFI = paste0("BFI_", 1:30),
  DT = paste0("DT_", 1:28),
  MFQ = c(paste0("MFQ1_", 1:11), paste0("MFQ2_", 1:11)),
  SDO = paste0("SDO_", 1:8)
)

for (name in names(columns_b)) {
  data_b <- b %>%
    select(id, all_of(columns_b[[name]])) %>%
    pivot_longer(cols = -id, names_to = "item", values_to = "resp")
  
  save(data_b, file = paste0(name, ".RData"))
  write.csv(data_b, paste0(name, ".csv"), row.names = FALSE)
}

columns_mist <- paste0("MIST_", 1:20)

mist_datasets <- list(
  a = datasets$a,
  b = datasets$b,
  c = datasets$c,
  d = datasets$d
)

for (name in names(mist_datasets)) {
  data_mist <- mist_datasets[[name]] %>%
    select(id, all_of(columns_mist)) %>%
    mutate(group = paste0("2", name)) %>%
    pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
  
}

mist_combined <- bind_rows(
  mist_datasets$a %>% select(id, all_of(columns_mist)) %>% mutate(group = "2a") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  mist_datasets$b %>% select(id, all_of(columns_mist)) %>% mutate(group = "2b") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  mist_datasets$c %>% select(id, all_of(columns_mist)) %>% mutate(group = "2c") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  mist_datasets$d %>% select(id, all_of(columns_mist)) %>% mutate(group = "2d") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
)

save(mist_combined, file = "MIST.RData")
write.csv(mist_combined, "MIST.csv", row.names = FALSE)


columns_snt <- paste0("SNT_", 1:3)

snt_datasets <- list(
  a = datasets$a,
  c = datasets$c,
  d = datasets$d
)

for (name in names(snt_datasets)) {
  data_snt <- snt_datasets[[name]] %>%
    select(id, all_of(columns_snt)) %>%
    mutate(group = paste0("2", name)) %>%
    pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
  
}

snt_combined <- bind_rows(
  snt_datasets$a %>% select(id, all_of(columns_snt)) %>% mutate(group = "2a") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  snt_datasets$c %>% select(id, all_of(columns_snt)) %>% mutate(group = "2c") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  snt_datasets$d %>% select(id, all_of(columns_snt)) %>% mutate(group = "2d") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
)

save(snt_combined, file = "SNT.RData")
write.csv(snt_combined, "SNT.csv", row.names = FALSE)


columns_trust_b <- c('TRUST_Doctors', 'TRUST_Scientists', 'TRUST_Politicians', 'TRUST_Journalists', 'TRUST_Government', 'TRUST_Science', 'TRUST_Officials', 'TRUST_Media')
columns_trust_acd <- c('TRUST_Family', 'TRUST_Neighbourhood', 'TRUST_Peers', 'TRUST_OtherLanguage', 'TRUST_Strangers', 'TRUST_Immigrants', 'TRUST_Doctors', 'TRUST_Scientists', 'TRUST_Politicians', 'TRUST_Journalists', 'TRUST_Government', 'TRUST_Science', 'TRUST_Officials')

trust_datasets_b <- list(b = datasets$b)
trust_datasets_acd <- list(a = datasets$a, c = datasets$c, d = datasets$d)

for (name in names(trust_datasets_b)) {
  data_trust <- trust_datasets_b[[name]] %>%
    select(id, all_of(columns_trust_b)) %>%
    mutate(group = paste0("2", name)) %>%
    pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
  

}

for (name in names(trust_datasets_acd)) {
  data_trust <- trust_datasets_acd[[name]] %>%
    select(id, all_of(columns_trust_acd)) %>%
    mutate(group = paste0("2", name)) %>%
    pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
  
}

trust_combined <- bind_rows(
  trust_datasets_acd$a %>% select(id, all_of(columns_trust_acd)) %>% mutate(group = "2a") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  trust_datasets_b$b %>% select(id, all_of(columns_trust_b)) %>% mutate(group = "2b") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  trust_datasets_acd$c %>% select(id, all_of(columns_trust_acd)) %>% mutate(group = "2c") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp"),
  trust_datasets_acd$d %>% select(id, all_of(columns_trust_acd)) %>% mutate(group = "2d") %>% pivot_longer(cols = -c(id, group), names_to = "item", values_to = "resp")
)

save(trust_combined, file = "TRUST.RData")
write.csv(trust_combined, "TRUST.csv", row.names = FALSE)

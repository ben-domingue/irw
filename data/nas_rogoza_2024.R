library(haven)
library(dplyr)
library(tidyr)

################## STUDY 1 ##################

df1 <- read_sav("Study 1 NAS.sav")

df1$id <- seq(1, nrow(df1))

df1 <- df1 %>%
  rename(cov_age = Age, cov_gender = Gender, cov_education = Education) %>%
  pivot_longer(-c(id, cov_age, cov_gender, cov_education),
               names_to = "item",
               values_to = "resp")

df1 <- df1 %>%
  select(id, cov_age, cov_gender, cov_education, item, resp)


################## STUDY 2 ##################

df2 <- read_sav("Study 2 NAS.sav")

df2$id <- seq(1, nrow(df2))

df2 <- df2 %>%
  rename(cov_age = Age, cov_gender = Gender, cov_education = Education) %>%
  select(-c(NVS, NGS, NAS)) %>%
  pivot_longer(-c(id, cov_age, cov_gender, cov_education),
               names_to = "item",
               values_to = "resp") %>%
  select(id, cov_age, cov_gender, cov_education, item, resp)

df2_NVS <- df2 %>%
  filter(grepl("NVS", item))

df2_NAS <- df2 %>%
  filter(grepl("NAS", item))

df2_NGS <- df2 %>%
  filter(grepl("NGS", item))


################## STUDY 5 ##################

df5 <- read_sav("Study 5 NAS.sav")

df5 <- df5 %>%
  select(-c(NVS, NAS, NGS)) %>%
  rename(id = SEMAID, wave = Time) %>%
  pivot_longer(-c(id, wave),
               names_to = "item",
               values_to = "resp")

df5 <- df5 %>%
  mutate(resp = na_if(resp, 9999))

df5_NVS <- df5 %>%
  filter(grepl("NVS", item))

df5_NAS <- df5 %>%
  filter(grepl("NAS", item))

df5_NGS <- df5 %>%
  filter(grepl("NGS", item))

####################################

write.csv(df1, "nas_rogoza_2024_study1.csv", row.names=FALSE)
write.csv(df2_NVS, "nas_rogoza_2024_study2_nvs.csv", row.names=FALSE)
write.csv(df2_NAS, "nas_rogoza_2024_study2_nas.csv", row.names=FALSE)
write.csv(df2_NGS, "nas_rogoza_2024_study2_ngs.csv", row.names=FALSE)
write.csv(df5_NVS, "nas_rogoza_2024_study5_nvs.csv", row.names=FALSE)
write.csv(df5_NAS, "nas_rogoza_2024_study5_nas.csv", row.names=FALSE)
write.csv(df5_NGS, "nas_rogoza_2024_study5_ngs.csv", row.names=FALSE)

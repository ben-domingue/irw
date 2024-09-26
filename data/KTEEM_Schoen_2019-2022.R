
library(tidyr)
library(dplyr)
df1 <- read.csv("Documents/Stanford/IRT/K-TEEM/FS K-TEEM 2019 First Administration_clean data.csv")
df2 <- read.csv("Documents/Stanford/IRT/K-TEEM/FS K-TEEM 2019 Second Administration_clean data.csv")
df3 <- read.csv("Documents/Stanford/IRT/K-TEEM/FS K-TEEM 2020_clean data.csv")
df4 <- read.csv("Documents/Stanford/IRT/K-TEEM/FS K-TEEM 2021_clean data.csv")
df5 <- read.csv("Documents/Stanford/IRT/K-TEEM/FS K-TEEM 2022_clean data.csv")

#------ Process 2019 First Admin Dataset ------
df1 <- df1 %>%
  dplyr::rename(id = PublicID, group = DataCollectionWave) %>%
  pivot_longer(cols = c(RPD_6,	LG_1,	EE_1,	SMW_6,	NPT_14,	EE_2,	NPT_12,	ISS_2,	ES_3,	ISS_1,	NPT_15,	LG_2,	PO_7,	ISS_4,	NPT_1,	CMMI_2,	MSWP_1,	CMMI_4,	LG_5,	ES_7,	MSWP_3,	CCMI_3,	ES_2,	MSWP_2,	ISS_3,	RPD_4,	PO_2,	ES_5,	ISS_6,	ISS_5,	PO_9,	RPD_5),
               names_to = "item",
               values_to = "resp")

#------ Process 2019 Second Admin Dataset ------
df2 <- df2 %>%
  dplyr::rename(id = PublicID, group = DataCollectionWave) %>%
  pivot_longer(cols = c(RPD_6,	LG_1,	EE_1,	SMW_6,	NPT_14,	EE_2,	NPT_12,	ISS_2,	ES_3,	ISS_1,	NPT_15,	LG_2,	PO_7,	ISS_4,	NPT_1,	CMMI_2,	MSWP_1,	CMMI_4,	LG_5,	ES_7,	MSWP_3,	CCMI_3,	ES_2,	MSWP_2,	ISS_3,	RPD_4,	PO_2,	ES_5,	ISS_6,	ISS_5,	PO_9,	RPD_5),
               names_to = "item",
               values_to = "resp")

#------ Process 2020 Dataset ------
df3 <- df3 %>%
  dplyr::rename(id = PublicID, group = DataCollectionWave) %>%
  pivot_longer(cols = c(RPD_6,	LG_1,	EE_1,	SMW_6,	NPT_14,	EE_2,	NPT_12,	ISS_2,	ES_3,	ISS_1,	NPT_15,	LG_2,	PO_7,	ISS_4,	NPT_1,	CMMI_2,	MSWP_1,	CMMI_4,	LG_5,	ES_7,	MSWP_3,	CCMI_3,	ES_2,	MSWP_2,	ISS_3,	RPD_4,	PO_2,	ES_5,	ISS_6,	ISS_5,	PO_9,	RPD_5),
               names_to = "item",
               values_to = "resp")

#------ Process 2021 Dataset ------
df4 <- df4 %>%
  dplyr::rename(id = PublicID, group = DataCollectionWave) %>%
  pivot_longer(cols = c(RPD_6,	LG_1,	EE_1,	SMW_6,	NPT_14,	EE_2,	NPT_12,	ISS_2,	ES_3,	NPT_15,	LG_2,	PO_7,	ISS_4,	NPT_1,	CMMI_2,	MSWP_1,	CMMI_4,	LG_5,	ES_7,	MSWP_3,	CCMI_3,	ES_2,	MSWP_2,	ISS_3,	RPD_4,	PO_2,	ES_5,	ISS_6,	ISS_5,	PO_9,	RPD_5,	PO_3,	LG_4,	ISS_7),
               names_to = "item",
               values_to = "resp")

#------ Process 2022 Dataset ------
df5 <- df5 %>%
  dplyr::rename(id = PublicID, group = DataCollectionWave) %>%
  pivot_longer(cols = c(RPD_6,	LG_1,	EE_1,	SMW_6,	NPT_14,	EE_2,	NPT_12,	ISS_2,	ES_3,	NPT_15,	LG_2,	PO_7,	ISS_4,	NPT_1,	CMMI_2,	MSWP_1,	CMMI_4,	LG_5,	ES_7,	MSWP_3,	CCMI_3,	ES_2,	MSWP_2,	ISS_3,	RPD_4,	PO_2,	ES_5,	ISS_6,	ISS_5,	PO_9,	RPD_5,	LG_4,	ISS_7),
               names_to = "item",
               values_to = "resp")

df <- rbind(df1, df2, df3, df4, df5)

# Check if all rows are unique
duplicated_rows <- duplicated(df)
all_rows_unique <- !any(duplicated_rows)
all_rows_unique

write.csv(df, "KTEEM_Schoen_2019-2022.csv", row.names=FALSE)

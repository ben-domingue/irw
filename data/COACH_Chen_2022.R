library(openxlsx)
library(dplyr)
library(tidyr)
library(stringr)

df <- read.xlsx("Copy of COACH_raw_data_22_5_16.xlsx")

# unique_rows <- df %>%
#   distinct(Cohort, Group, Number, Village)
# 
# print(nrow(unique_rows) == nrow(df)) # check if the number of rows in unique_rows is the same as df

df$id <- seq(1, nrow(df))

df <- df %>%
  select(-c(Cohort, Group, Number, Village, `AIDS`, `Cerebrovascular.Disease`,"Chronic.Pulmonary.Disease" ,"Congestive.Heart.Failure","Connective.Tissue.Disease" ,"Dementia" ,"Hemiplegia" ,"Leukemia" ,"Malignant.Lymphoma","Myocardial.Infarction","Peripheral.Vascular.Disease","Ulcer.Disease","Diabetes.Mellitus" ,"Liver.Disease" ,"Chronic.Kidney.Disease" ,"Solid.Tumor","Antidepressant.Use", `Dropout`, `Sex`, `Age`, `Family_Information`, `Inhabiting_information`, 
            `Educational_level`, `Employment_status`, `Religion`, `Economic_satisfaction`, 
            `PCP_Baseline_BMI`, `PCP_Baseline_systolic_pressure`, `PCP_Baseline_diastolic_pressure`, 
            `PCP_First_Month_systolic_pressure`, `PCP_First_Month_diastolic_pressure`, 
            `PCP_Third_Month_systolic_pressure`, `PCP_Third_Month_diastolic_pressure`, 
            `PCP_Sixth_Month_systolic_pressure`, `PCP_Sixth_Month_diastolic_pressure`, 
            `PCP_Ninth_Month_systolic_pressure`, `PCP_Ninth_Month_diastolic_pressure`, 
            `PCP_Twelfth_Month_systolic_pressure`, `PCP_Twelfth_Month_diastolic_pressure`, 
            `PCP_Twelfth_Month_BMI`))
df <- df %>%
  mutate(across(-id, as.numeric))

df <- df %>%
  pivot_longer(cols = -id,  
               names_to = "item", 
               values_to = "resp") %>%
  filter(!is.na(resp)) %>%
  mutate(wave = case_when(
    str_detect(item, 'Baseline') ~ 1,
    str_detect(item, 'RA_Twelfth_Month_Treatment_Stigma') ~ 2,
    str_detect(item, 'RA_First_Month_HDRS') ~ 2,
    str_detect(item, 'RA_Third_Month_HDRS') ~ 3,
    str_detect(item, 'RA_Sixth_Month_HDRS') ~ 4,
    str_detect(item, 'RA_Ninth_Month_HDRS') ~ 5,
    str_detect(item, 'RA_Twelfth_Month_HDRS') ~ 6,
    str_detect(item, 'RA_Sixth_Month_WHOQOL_BREF') ~ 2,
    str_detect(item, 'RA_Twelfth_Month_WHOQOL_BREF') ~ 3,
    str_detect(item, 'RA_Sixth_Month_ADL') ~ 2,
    str_detect(item, 'RA_Twelfth_Month_ADL') ~ 3,
    str_detect(item, 'RA_Sixth_Month_IADL') ~ 2,
    str_detect(item, 'RA_Twelfth_Month_IADL') ~ 3,
    str_detect(item, 'RA_Sixth_Month_MOS_SSS_C') ~ 2,
    str_detect(item, 'RA_Twelfth_Month_MOS_SSS_C') ~ 3,
    str_detect(item, 'RA_Twelfth_Month_Social_Network') ~ 2,
    str_detect(item, 'PCP_First_Month_PHQ9') ~ 2,
    str_detect(item, 'PCP_Third_Month_PHQ9') ~ 3,
    str_detect(item, 'PCP_Sixth_Month_PHQ9') ~ 4,
    str_detect(item, 'PCP_Ninth_Month_PHQ9') ~ 5,
    str_detect(item, 'PCP_Twelfth_Month_PHQ9') ~ 6,
    TRUE ~ NA_real_
  )) %>%
  mutate(item = case_when(
    str_detect(item, 'Baseline') ~ str_replace(item, "(.?)Baseline", ""),
    str_detect(item, 'Month') ~ str_replace(item, "^([^_]+)_[^_]+_Month_(.*)", "\\1_\\2"),
    TRUE ~ item
  )) %>%
  select(id, item, wave, resp) %>%
  filter(!resp %in% c(6, 7, 11, 12, 21, 22, 32, 33, 55))

write.csv(df, "COACH_Chen_2022.csv", row.names=FALSE)

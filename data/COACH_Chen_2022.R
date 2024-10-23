library(openxlsx)
library(dplyr)
library(tidyr)
library(stringr)

df <- read.xlsx("Copy of COACH_raw_data_22_5_16.xlsx")

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
  mutate_all(tolower) %>%
  mutate(wave = case_when(
    str_detect(item, 'baseline') ~ 1,
    str_detect(item, 'ra_twelfth_month_treatment_stigma') ~ 2,
    str_detect(item, 'ra_first_month_hdrs') ~ 2,
    str_detect(item, 'ra_third_month_hdrs') ~ 3,
    str_detect(item, 'ra_sixth_month_hdrs') ~ 4,
    str_detect(item, 'ra_ninth_month_hdrs') ~ 5,
    str_detect(item, 'ra_twelfth_month_hdrs') ~ 6,
    str_detect(item, 'ra_sixth_month_whoqol_bref') ~ 2,
    str_detect(item, 'ra_twelfth_month_whoqol_bref') ~ 3,
    str_detect(item, 'ra_sixth_month_adl') ~ 2,
    str_detect(item, 'ra_twelfth_month_adl') ~ 3,
    str_detect(item, 'ra_sixth_month_iadl') ~ 2,
    str_detect(item, 'ra_twelfth_month_iadl') ~ 3,
    str_detect(item, 'ra_sixth_month_mos_sss_c') ~ 2,
    str_detect(item, 'ra_twelfth_month_mos_sss_c') ~ 3,
    str_detect(item, 'ra_twelfth_month_social_network') ~ 2,
    str_detect(item, 'pcp_first_month_phq9') ~ 2,
    str_detect(item, 'pcp_third_month_phq9') ~ 3,
    str_detect(item, 'pcp_sixth_month_phq9') ~ 4,
    str_detect(item, 'pcp_ninth_month_phq9') ~ 5,
    str_detect(item, 'pcp_twelfth_month_phq9') ~ 6,
    TRUE ~ NA_real_
  )) %>%
  mutate(item = case_when(
    str_detect(item, 'baseline') ~ str_replace(item, "(.?)baseline", ""),
    str_detect(item, 'month') ~ str_replace(item, "^([^_]+)_[^_]+_month_(.*)", "\\1_\\2"),
    TRUE ~ item
  )) %>%
  select(id, item, wave, resp) %>%
  filter(!resp %in% c(6, 7, 11, 12, 21, 22, 32, 33, 55))

df_treatment <- df %>% filter(grepl("treatment", item))
df_hdrs <- df %>% filter(grepl("hdrs", item))
df_whoqol <- df %>% filter(grepl("whoqol", item))
df_csq <- df %>% filter(grepl("customer", item)) %>%
          select (id, resp, item)
df_adl <- df %>% filter(grepl("_adl", item))
df_iadl <- df %>% filter(grepl("iadl", item))
df_mos <- df %>% filter(grepl("mos", item))
df_sns <- df %>% filter(grepl("social", item))
df_phq <- df %>% filter(grepl("phq", item))

write.csv(df_treatment, "COACH_Chen_2022_treatmentStigma.csv", row.names=FALSE)
write.csv(df_hdrs, "COACH_Chen_2022_HDRS.csv", row.names=FALSE)
write.csv(df_whoqol, "COACH_Chen_2022_WHOQOL_BREF.csv", row.names=FALSE)
write.csv(df_csq, "COACH_Chen_2022_CSQ.csv", row.names=FALSE)
write.csv(df_adl, "COACH_Chen_2022_ADL.csv", row.names=FALSE)
write.csv(df_iadl, "COACH_Chen_2022_IADL.csv", row.names=FALSE)
write.csv(df_mos, "COACH_Chen_2022_MOS_SSS_C.csv", row.names=FALSE)
write.csv(df_sns, "COACH_Chen_2022_SNS.csv", row.names=FALSE)
write.csv(df_phq, "COACH_Chen_2022_PHQ9.csv", row.names=FALSE)

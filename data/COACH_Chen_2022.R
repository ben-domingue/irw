library(openxlsx)
library(dplyr)
library(tidyr)
library(stringr)

## The deposited workbook (Harvard Dataverse doi:10.7910/DVN/6RWH41) has a
## TWO-ROW header. Row 2 carries the real column name for every column except
## the first five: the 15 Charlson comorbidity flags sit under a merged
## `Comorbidity` band, so their names are on row 2 while `Cohort`, `Group`,
## `Number`, `Village` are on row 1.
##
## read.xlsx() reads a single header row, so against the file AS DEPOSITED the
## comorbidity columns come back as X6..X20 and the select() below fails on
## names that do not exist -- this script could only ever run against a local
## copy whose top row had been removed by hand. Build the header from both rows
## instead: row 2 wins, row 1 fills the blanks. Verified to produce exactly the
## names this script goes on to reference.
XLSX <- "Copy of COACH_raw_data_22_5_16.xlsx"
hdr <- read.xlsx(XLSX, colNames = FALSE, rows = 1:2)
df  <- read.xlsx(XLSX, colNames = FALSE, startRow = 3)
.nm <- ifelse(is.na(hdr[2, ]) | trimws(as.character(hdr[2, ])) == "",
              as.character(hdr[1, ]), as.character(hdr[2, ]))
names(df) <- make.names(trimws(.nm), unique = TRUE)

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
df_whoqol <- df %>% filter(grepl("whoqol", item)) %>%
  filter(resp != 0)
df_csq <- df %>% filter(grepl("customer", item)) %>%
          select (id, resp, item)
df_adl <- df %>% filter(grepl("_adl", item)) %>%
  filter(resp != 0)
## The Lawton IADL prints a different number of options per item, and the
## deposit ships them: COACH_Code Book_Final_version.xlsx, sheet 2, one row per
## IADL item with its value labels. Transcribed here rather than inferred from
## observed maxima.
##
##   q1 Shopping 0-3   q2 Transportation 0-4   q3 Food preparation 0-3
##   q4 Housekeeping 0-4   q5 Laundry 0-2   q6 Telephone 0-3
##   q7 Own medication 0-3   q8 Finances 0-2
##
## 65 stored responses sit above their own item's ceiling (#1924), and they are
## only at the 6- and 12-month waves: at baseline every item's observed maximum
## equals its codebook ceiling exactly. A uniform 0-4 administration would show
## the extra levels at baseline too, so this is 0.12% data entry, not a wrong
## option mapping -- q8 alone carries 35 of them (3 x26, 4 x9) on a two-option
## item.
##
## Replaces `filter(resp != 5)`, which caught one of the 66 by coincidence: 5 is
## out of range for every IADL item, but so are 3 and 4 on q5/q8, and 12 on q3.
IADL_MAX <- c(ra_iadl_q1 = 3, ra_iadl_q2 = 4, ra_iadl_q3 = 3, ra_iadl_q4 = 4,
              ra_iadl_q5 = 2, ra_iadl_q6 = 3, ra_iadl_q7 = 3, ra_iadl_q8 = 2)

df_iadl <- df %>% filter(grepl("iadl", item))
## A renamed item must fail loudly: an unmatched name would give NA and drop
## every row of that item silently.
stopifnot(all(unique(df_iadl$item) %in% names(IADL_MAX)))
iadl_resp <- as.numeric(df_iadl$resp)
iadl_keep <- !is.na(iadl_resp) & iadl_resp >= 0 & iadl_resp <= IADL_MAX[df_iadl$item]
message(sprintf("IADL: dropped %d of %d response(s) outside the codebook range",
                sum(!iadl_keep), nrow(df_iadl)))
df_iadl <- df_iadl[iadl_keep, ]
df_mos <- df %>% filter(grepl("mos", item))
df_sns <- df %>% filter(grepl("social", item))
df_phq <- df %>% filter(grepl("phq", item)) %>%
  filter(resp != 4)

write.csv(df_treatment, "COACH_Chen_2022_treatmentStigma.csv", row.names=FALSE)
write.csv(df_hdrs, "COACH_Chen_2022_HDRS.csv", row.names=FALSE)
write.csv(df_whoqol, "COACH_Chen_2022_WHOQOL_BREF.csv", row.names=FALSE)
write.csv(df_csq, "COACH_Chen_2022_CSQ.csv", row.names=FALSE)
write.csv(df_adl, "COACH_Chen_2022_ADL.csv", row.names=FALSE)
write.csv(df_iadl, "COACH_Chen_2022_IADL.csv", row.names=FALSE)
write.csv(df_mos, "COACH_Chen_2022_MOS_SSS_C.csv", row.names=FALSE)
write.csv(df_sns, "COACH_Chen_2022_SNS.csv", row.names=FALSE)
write.csv(df_phq, "COACH_Chen_2022_PHQ9.csv", row.names=FALSE)

library(readr)
setwd("/Users/radhika/Google Drive Stanford/IRW/PISA/2015/")

## Get student information
library(haven)
library(dplyr)
library(tidyverse)
#student <- read_sas("PUF_SAS_COMBINED_CMB_STU_QQQ/cy6_ms_cmb_stu_qqq.sas7bdat")   
#names(student)
#write_csv(student, "student_info_2015.csv")

student= read_csv("student_info_2015.csv")
#student |> dplyr::select(contains("ST004"))
student=student |> 
  dplyr::select("CNTRYID","CNT","CNTSCHID","CNTSTUID" ,
                  "ST004D01T","ST001D01T", "SENWT" , "W_FSTUWT", "STRATUM") |>
  dplyr::rename(id= CNTSTUID, 
         gender= ST004D01T,
         grade = ST001D01T) |>
  mutate(gender = ifelse(gender==9, NA, gender),
         grade = ifelse(grade==96 | grade==99, NA, grade),
  ) 

df = read_csv("pisa2015_math.csv")
attr(df,which='id')<-student
# Time in seconds
head(df)

df = df |>
  filter(!is.na(resp)) |> select(-CNT, -CNTRYID)

save(df,file="pisa2015_math.Rdata")


df = read_csv("pisa2015_read.csv")
attr(df,which='id')<-student
# Time in seconds

save(df,file="pisa2015_read.Rdata")
#load("pisa2015_read.Rdata")

df = read_csv("pisa2015_science.csv")
# Time in seconds
attr(df,which='id')<-student
save(df,file="pisa2015_science.Rdata")
# load("pisa2015_science.Rdata")

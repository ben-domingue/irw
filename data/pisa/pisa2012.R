
### PISA 2012

### 

library(readr)
library(dplyr)
library(tidyverse)
library(EdSurvey)
#install.packages("SAScii")
library(SAScii)

filepath="/Users/radhika/Google Drive Stanford/IRW/PISA/2012/"
setwd(filepath)
library(haven)

# importing data in a readable format
dic_student = parse.SAScii(sas_ri = 'PISA2012_SAS_scored_cognitive_item.sas')
student <- read_fwf(file = 'INT_COG12_S_DEC03.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
#colnames(student) 
#glimpse(student)


df= student |>
  select(CNT, SUBNATIO,STIDSTD, SCHOOLID,BOOKID,TESTLANG,
         PM00FQ01:PS527Q04T) |>
  pivot_longer(
    cols= PM00FQ01:PS527Q04T,
    names_to= "item",
    values_to= "resp"
  )

unique(df$resp) #7= Not administered, 8= not reached
# error with resp=r
n_distinct(df$item)

#nrow(df2)
df = df |>
  rename(id = STIDSTD) |>
  mutate(resp = if_else(resp %in% c(7,8,9), NA, resp))


###### Add student weights
dic_student = parse.SAScii(sas_ri = 'PISA2012_SAS_student.sas')
student <- read_fwf(file = 'INT_STU12_DEC03.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
#names(student)
#glimpse(student)
# ST03Q01 gender is female=1, male=2, 7=N/A, 8= Invalid, 9= Missing
# Grade 9 = missing
# W_FSTUWT = Student final weight, CNTFAC1=Country weight factor for equal weights 
# CNTFAC= Country weight factor for normalised weights (sample size)
# VAR_UNIT= RANDOMLY ASSIGNED VARIANCE UNIT
# WVARSTRR = RANDOMIZED FINAL VARIANCE STRATUM (1-80)
#"SENWGT_STU" = Senate weight - sum of weight within the country is 1000

student = student |> select(contains("WT"), "STRATUM","WVARSTRR","VAR_UNIT","SENWGT_STU", "CNT", "STIDSTD",
                            "SCHOOLID","ST01Q01", "ST04Q01") |>
  rename(id= STIDSTD, 
         gender= ST04Q01,
         grade = ST01Q01) |>
  mutate(gender = ifelse(gender==9, NA, gender),
         grade = ifelse(grade==96 | grade==99, NA, grade),
         ) 

student = student |> distinct()
nrow(student)

df_student_attr1 = df |> select(id, CNT,
                               "BOOKID", "SUBNATIO", "SCHOOLID", "TESTLANG") |> distinct()
nrow(df_student_attr1)
df_student_attr= left_join(df_student_attr1, student, by=c("id", "CNT", "SCHOOLID"))
names(df_student_attr)= str_to_lower(names(df_student_attr))
#nrow(df_student_attr)
#summary(df)
df$id = paste0(df$CNT, df$SCHOOLID, df$id)

attr(df,which='id')<-df_student_attr
#df$id = paste0(df$cnt, df$schoolid, df$id)


df = df |> select(-"BOOKID", -"SUBNATIO", -"SCHOOLID", -"TESTLANG")
names(df)= str_to_lower(names(df))

names(df)
#load process data
#load("/Users/radhika/Google Drive Stanford/IRW/Process data/PISA/CMAT_logdata_realased/pisa2012_cba_math.Rdata")
#attr(df,which='process')<-process

df = df |>
  filter(!is.na(resp)) |> select(-cnt)

head(df)
save(df,file="pisa2012.Rdata")
# load("pisa2012.Rdata")
# table(substr(df$item,1,2))
# df_student_attr = attr(df,which='id')
df$subject =substr(df$item,1,2)
df = df |>
  mutate(subject = case_when(subject=="PS" ~ "science",
                             subject=="PR" ~ "read",
                             subject=="PM" ~ "math"
  ))
df0= df
table(df$subject)

for (sub in c("math", "read", "science")) {
  df = df0 |> filter(subject==sub) 
  name = paste0("pisa2012_", sub, ".Rdata")
  df = df |> dplyr::select(-subject)
  save(df,file=name)
}

# load("pisa2012_math.Rdata")
# load("pisa2012_read.Rdata")
# load("pisa2012_science.Rdata")

 


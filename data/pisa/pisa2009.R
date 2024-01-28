
### PISA 2009

### 
library(readr)
library(dplyr)
library(tidyverse)
#install.packages("SAScii")
library(SAScii)

filepath="/Users/radhika/Google Drive Stanford/IRW/PISA/2009/"
setwd(filepath)
library(haven)

# importing data in a readable format
dic_student = parse.SAScii(sas_ri = 'PISA2009_SAS_scored_cognitive_item.sas')
student <- read_fwf(file = 'INT_COG09_S_DEC11.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
#colnames(student) 
#glimpse(student)


df= student |>
  select(COUNTRY,CNT, SUBNATIO,STIDSTD, SCHOOLID,BOOKID,
         M033Q01:S527Q04T) |>
  pivot_longer(
    cols= M033Q01:S527Q04T,
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
dic_student = parse.SAScii(sas_ri = 'PISA2009_SAS_student.sas')
student <- read_fwf(file = 'INT_STQ09_DEC11.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
#glimpse(student)
# ST03Q01 gender is female=1, male=2, 7=N/A, 8= Invalid, 9= Missing
# Grade 9 = missing
# W_FSTUWT = Student final weight, CNTFAC1=Country weight factor for equal weights 
# CNTFAC= Country weight factor for normalised weights (sample size)
# RANDUNIT= RANDOMLY ASSIGNED VARIANCE UNIT
# WVARSTRR = RANDOMIZED FINAL VARIANCE STRATUM (1-80)

student = student |> select(contains("WT"), "CNTFAC","STRATUM","WVARSTRR","RANDUNIT", "COUNTRY", "CNT", "STIDSTD",
                            "SCHOOLID","ST01Q01", "ST04Q01", "TESTLANG") |>
  rename(id= STIDSTD, 
         gender= ST04Q01,
         grade = ST01Q01) |>
  mutate(gender = ifelse(gender==9, NA, gender),
         grade = ifelse(grade==96 | grade==99, NA, grade),
         ) 

student = student |> distinct()
nrow(student)

df_student_attr1 = df |> select(id, CNT,
                               "BOOKID", "SUBNATIO", "SCHOOLID") |> distinct()
nrow(df_student_attr1)
df_student_attr= inner_join(df_student_attr1, student, by=c("id", "CNT", "SCHOOLID"))
nrow(df_student_attr)
#summary(df)
attr(df,which='id')<-df_student_attr

df = df |> select(-"BOOKID", -"SUBNATIO", -"SCHOOLID")
df = df |>
  mutate(subject = case_when(subject=="S" ~ "science",
                             subject=="R" ~ "read",
                             subject=="M" ~ "math"
  ))
df = df |>
  filter(!is.na(resp)) |>
  mutate(id= paste0(CNT,id)) |> select(-CNT, -COUNTRY)

head(df)
save(df,file="pisa2009.Rdata")
#


# load("pisa2009.Rdata")
# table(substr(df$item,1,1))

df$subject =substr(df$item,1,1)
df = df |>
  mutate(subject = case_when(subject=="S" ~ "science",
                             subject=="R" ~ "read",
                             subject=="M" ~ "math"
  ))
df0= df
table(df$subject)


for (sub in c("math", "read", "science")) {
  df = df0 |> filter(subject==sub) 
  name = paste0("pisa2009_", sub, ".Rdata")
  df = df |> dplyr::select(-subject)
  save(df,file=name)
}



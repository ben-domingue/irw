
### PISA 2000
### Downloaded from: https://www.oecd.org/pisa/data/database-pisa2000.htm
### 
library(readr)
library(dplyr)
library(tidyverse)
#library(EdSurvey)
#install.packages("SAScii")
library(SAScii)

filepath="/Users/radhika/Google Drive Stanford/IRW/PISA/2003/"
setwd(filepath)
library(haven)

#setwd("~/")
# pisa2000 = read.csv("Year2000/intcogn_v4.txt", sep=" ")
# names(pisa2000)

# importing data in a readable format
dic_student = parse.SAScii(sas_ri = 'PISA2003_SAS_cognitive_item.sas')
student <- read_fwf(file = 'INT_cogn_2003_v2.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
#colnames(student) 
#glimpse(student)


##Drop the NA row
student= student[,-6]


df= student |>
  dplyr::select(COUNTRY,CNT, SUBNATIO,STIDSTD, SCHOOLID,BOOKID,MSCALE,SSCALE,PSCALE, M033Q01:X603Q03) |>
  pivot_longer(
    cols= M033Q01:X603Q03,
    names_to= "item",
    values_to= "resp_text"
  )

unique(df$resp_text)
n_distinct(df$item)

##############. CODEBOOK
# import codebook for scoring
codebook = read_csv("Cogn_CodeBook_2003_v2.csv")
codebook= codebook[,-c(4:7)]


codebook= codebook |> 
  dplyr::rename(score_rule = credit_text) |>
  filter((resp_text %in% c("0","1","2","3", "4","5", "6", "7", "8", "9", "n", "r") ))

codebook_optioncount= codebook |> 
  filter(resp_text %in% c("0","1","2","3", "4","5", "6", "7")) |>
  mutate(score_rule = ifelse(score_rule=="Fulll Credit" | score_rule=="Fulll Credit" | score_rule=="Full  Credit" | score_rule=="Full credit", "Full Credit", score_rule)) |>
  group_by(item) |>
  mutate(optioncount = n_distinct(score_rule)) |>
  dplyr::select(item, optioncount) |>
  distinct()

codebook= merge(codebook,codebook_optioncount)

## convert responses to scores
codebook = codebook |>
  mutate(resp = case_when(
    optioncount==3 & (str_detect(score_rule, "Full Credit")  ) ~ 2,
    optioncount==2 & (str_detect(score_rule, "Full Credit")) ~ 1,
    str_detect(score_rule, "No Credit")  ~ 0,
    str_detect(score_rule, "Partial Credit")  ~ 1,
                          T ~ NA
  )
  )  


df = left_join(df, codebook, by=c("item","resp_text"))
#nrow(df2)
df = df |>
  rename(id = STIDSTD)


#unique(codebook_cr$score_rule)
#unique(codebook_cr$resp_text)
#table(codebook_cr$score_rule, codebook_cr$resp)


###### Add student weights
dic_student = parse.SAScii(sas_ri = 'PISA2003_SAS_student.sas')
student <- read_fwf(file = 'INT_stui_2003_v2.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
# ST03Q01 gender is female=1, male=2, 7=N/A, 8= Invalid, 9= Missing
# Grade 97=N/A, 98= Invalid, 99=Miss
# W_FSTUWT = Student final weight, CNTFAC1=Country weight factor for equal weights 
# CNTFAC2= Country weight factor for normalised weights (sample size)
student = student |> dplyr::select(contains("WT"), contains("FAC"), "COUNTRY", "CNT", contains("ID"),"ST01Q01", "ST03Q01") |>
  dplyr::rename(id= STIDSTD, 
         gender= ST03Q01,
         grade = ST01Q01)

nrow(df)
df = left_join(df, student)




df_student_attr = df |> dplyr::select(id, CNT, contains("WT"), contains("FAC"), gender, grade,
                               starts_with("SCALE"), "BOOKID", "SUBNATIO", "SCHOOLID")
#summary(df)
attr(df,which='id')<-df_student_attr
names(df_student_attr)
df = df |> dplyr::select(-contains("WT"), -contains("FAC"), -gender, -grade,
                  -contains("scale"), -"BOOKID", -"SUBNATIO", -"SCHOOLID",
                  -score_rule, -optioncount, -resp_text)

df = df |>
  filter(!is.na(resp)) |>
  mutate(id= paste0(CNT,id)) |> select(-CNT, -COUNTRY)



save(df,file="pisa2003.Rdata")
#load("pisa2003.Rdata")
#load("/Users/radhika/Google Drive Stanford/IRW/PISA/2003/pisa2003.Rdata")
# table(substr(df$item,1,1))

df$subject =substr(df$item,1,1)

df$subject = ifelse(df$subject=="M", "math", ifelse(df$subject=="R", "read", ifelse(df$subject=="S","science", "problem_solving")))
df0= df
table(df$subject)

for (sub in c("math", "read", "science", "problem_solving")) {
  df = df0 |> filter(subject==sub) 
  name = paste0("pisa2003_", sub, ".Rdata")
  df = df |> dplyr::select(-subject)
  save(df,file=name)
}


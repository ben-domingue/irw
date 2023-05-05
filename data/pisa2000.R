
### PISA 2000
### Downloaded from: https://www.oecd.org/pisa/data/database-pisa2000.htm
### 
library(readr)
library(dplyr)
library(tidyverse)
library(EdSurvey)
#install.packages("SAScii")
library(SAScii)

filepath="/Users/radhika/Google Drive Stanford/IRW/PISA/2000/"
setwd(filepath)

#setwd("~/")
# pisa2000 = read.csv("Year2000/intcogn_v4.txt", sep=" ")
# names(pisa2000)

# importing data in a readable format
dic_student = parse.SAScii(sas_ri = 'PISA-2000-SAS-control-file-for-the-cognitive-item-data-file (1).sas')
student <- read_fwf(file = 'intcogn_v4.txt', col_positions = fwf_widths(dic_student$width), progress = T)
colnames(student) <- dic_student$varname
colnames(student) 


##The stuff below could be wrong, it is more an attempt to be somewhat right in case 
## anyone needs this in the future. But caution is advised 
names(student)[4]= "std_rem"
names(student)[6]= "subnation_rem"
names(student)[10:228] = names(student)[9:227]
#drop cols 8 &9
student= student[-c(8:9)]
names(student)[230]= "sscale_actual"
names(student)[229]= "rscale_actual"
names(student)[228]= "mscale_actual"
names(student)[232]= "cnt_rem"
names(student)[231]= "cnt_frst"

#student= student[-c(227)]


#Fix mistakes in file import
student= unite(student, CNT, cnt_frst,cnt_rem, sep="")
student= unite(student, STIDSTD, STIDSTD,std_rem, sep="")
student= unite(student, SUBNATIO, SUBNATIO,subnation_rem, sep="")

# Something is wrong with country numeric codes (COUNTRY) but I'm just dropping it for now
n_distinct(student$CNT)
n_distinct(student$COUNTRY)
unique(student$CNT)


df= student |>
  pivot_longer(
    cols= M033Q01:S305Q03T,
    names_to= "item",
    values_to= "resp_text"
  )

unique(df$resp_text)
n_distinct(df$item)
# import codebook for scoring
codebook = read_csv("PISA2000_Codebook_cognitive_item.csv")
codebook= codebook[c(2,4, 6)]
codebook= codebook[-c(1:5),]
names(codebook)= c("item", "itemtype",  "score_rule")
codebook= codebook |> filter(!is.na(item))

df = df |>
  select(-VER_COGN, SUBNATIO, MSCALE) |>
  rename(id= STIDSTD)

## Working with multiple choice (MC) items

codebook_mc = codebook |>
  filter(itemtype=="MC") |>
  mutate(correct_option = ifelse(str_detect(score_rule, "Full Credit"), 1,0)) |>
  filter(correct_option==1) |>
  mutate(correct_option_num= substr(score_rule,1,1)) 
  

nrow(codebook_mc)
unique(codebook_mc$score_rule)

# from data frame, change responses to scores
df_mc = inner_join(df, codebook_mc)
#names(df_mc)
df_mc= df_mc |>
  mutate(resp_text_na = ifelse(resp_text %in% c("n","r",8,9),"", resp_text),
         resp = case_when(resp_text_na==correct_option_num ~ 1,
                          resp_text_na=="" ~ NA,
                          T ~ 0
                          )
         )  |> select(CNT, SCHOOLID, contains("scale"), id, item, itemtype, resp,resp_text) 


## Working with all other option types: CR
codebook_cr = codebook |>
  filter(!itemtype=="MC") |>
  mutate(resp = case_when(str_detect(score_rule, "Full Credit")~ 2,
                                    str_detect(score_rule, "Partial Credit")~ 1,
                                    str_detect(score_rule, "No credit") | str_detect(score_rule, "No Credit")~ 0,
                          T ~ NA
                                    )
         ) |>
  mutate(resp_text= substr(score_rule,1,1)) 

#unique(codebook_cr$score_rule)
#unique(codebook_cr$resp_text)
#table(codebook_cr$score_rule, codebook_cr$resp)

df_cr = inner_join(df, codebook_cr)
#unique(df_cr$resp_text)
df_cr= df_cr |>
  select(CNT, SCHOOLID, contains("scale"), id, item, itemtype, resp, resp_text) 

df = rbind(df_cr, df_mc)

df_id = df |> select(CNT, SCHOOLID, item, id, contains("scale"), mscale_actual, rscale_actual, sscale_actual, itemtype, resp_text)
#summary(df)
attr(df,which='id')<-df_id
df = df |> select(-MSCALE,-SCHOOLID,-contains("actual"), -itemtype, -resp_text)
save(df,file="pisa2000.Rdata")

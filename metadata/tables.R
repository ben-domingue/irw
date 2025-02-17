##tables on redivis
library(redivis)
v1<- redivis::organization("datapages")$dataset("Item Response Warehouse",version='next')
tables<-v1$list_tables()
red<-sapply(tables,function(x) x$name)

##tables on sheet
irw_dict <- gsheet::gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=0#gid=0')
gs <- irw_dict[irw_dict$`Public Reshare?`=="Public",]

##biblio/redivis
## user <- redivis$user("bdomingu")
## dataset <- user$dataset("irw_meta:bdxt:latest")
## bib <- dataset$table("biblio:qahg")
## bib<-bib$to_tibble()
bib<-read.csv("biblio.csv")

##metadata/redivis
## user <- redivis$user("bdomingu")
## dataset <- user$dataset("irw_meta:bdxt:latest")
## met <- dataset$table("metadata:h5gs")
## met<-met$to_tibble()
met<-read.csv("metadata.csv")

L<-list(red=red,gs=gs$table,bib=bib$table,met=met$table)
x<-data.frame(table=tolower(red),red=1)
for (i in 2:4) {
    y<-data.frame(table=tolower(L[[i]]),zz=1)
    names(y)[2]<-names(L)[i]
    x<-merge(x,y,by='table',all=TRUE)
}

n<-rowSums(x[,-1],na.rm=TRUE)
x[order(n),]
dim(x)
base::table(n,useNA='always')

write.csv(x,'tables.csv',quote=FALSE,row.names=FALSE)

x[n<4,]




##art: do we need to add this? do we already have it?
##PEPABAS2C_Kubicka_2024: this is on redivis but nowhere else?
##tears: need to add to redivis?
##duolingo: need to add to redivis?
##genpsych_russell_2024_gpt3: add to google scholar.//genpsych_russell_2024_gpt3.5: is this a typo with the above? also needs to not have the period
##promispfue_2: not on google scholar//promispfue_2.0e_gershon_2019_promis maybe these need to be harmonized?

                                   table red gs bib met
34                                   art  NA  1   1  NA
129                     duolingo__listen  NA  1   1  NA
130                duolingo__reverse_tap  NA  1   1  NA
131          duolingo__reverse_translate  NA  1   1  NA
315           genpsych_russell_2024_gpt3   1 NA  NA   1
316         genpsych_russell_2024_gpt3.5  NA  1   1  NA
317         genpsych_russell_2024_gpt3.5  NA  1   1  NA
532             pepabas2c_kubicka_2024\n  NA NA   1  NA
615                         promispfue_2   1 NA  NA   1
616  promispfue_2.0e_gershon_2019_promis  NA  1   1  NA
733                                tears  NA  1   1  NA
774 veterans_affairs_ssvf_survey_2016-17  NA  1   1   1
775 veterans_affairs_ssvf_survey_2018-20  NA  1   1   1
776 veterans.affairs.ssvf.survey.2016-17   1 NA  NA  NA
777 veterans.affairs.ssvf.survey.2018-20   1 NA  NA  NA

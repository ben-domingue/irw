##tables on redivis
library(redivis)
v1<- redivis::organization("datapages")$dataset("Item Response Warehouse",version='latest')
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
x[n<4,]

cnt<-base::table(x$table)
names(cnt)[cnt>1]
for (i in 1:length(L)) {
    tab<-base::table(L[[i]])
    print(tab[tab>1])
}

                                  table red gs bib met
130                    duolingo__listen  NA  1   1  NA
131               duolingo__reverse_tap  NA  1   1  NA
132         duolingo__reverse_translate  NA  1   1  NA
316          genpsych_russell_2024_gpt3   1 NA  NA   1
317        genpsych_russell_2024_gpt3_5  NA  1   1  NA
318        genpsych_russell_2024_gpt3.5  NA NA   1  NA
319        genpsych_russell_2024_gpt3.5  NA NA   1  NA
616                        promispfue_2   1 NA  NA   1
617 promispfue_2_0e_gershon_2019_promis  NA  1   1  NA
618 promispfue_2.0e_gershon_2019_promis  NA NA   1  NA


##https://github.com/itemresponsewarehouse/Rpkg/issues/93#issuecomment-3001730454

library(gsheet)
irw_dict <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315')
z<-as.data.frame(irw_dict)
z<-z[,c("table","Derived License","Custom License...11")]
names(z)[2]<-'Derived_License'
names(z)[3]<-"Custom_License_Terms"

bib<-read.csv("biblio.csv")
bib$Derived_License<-NULL
dim(bib)
dim(z)
biblio<-merge(bib,z)
dim(biblio)

readr::write_csv(biblio, "biblio.csv")

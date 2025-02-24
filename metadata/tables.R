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


## ###################################################33
##eliminating duplicate biblio.csv entries

met<-read.csv("metadata.csv")
length(unique(met$table))
bib<-read.csv("biblio.csv")
tab<-base::table(bib$table)
nm<-names(tab)[tab>1]
hold<-bib[!(bib$table %in% nm),]
x<-bib[bib$table %in% nm,]
length(unique(x$table))
L<-split(x,x$table)
f<-function(z) {
    z2<-z[!is.na(z[,2]),]
    if (nrow(z2)==1) tr<-z2 else {
                                z2<-z[!is.na(z$Derived_License),]
                                if (nrow(z2)==1) tr<-z2
                            }
    tr
}
L<-lapply(L,f)
table(sapply(L,nrow))


bib<-data.frame(rbind(hold,do.call("rbind",L)))
length(unique(bib$table))
test<-tolower(bib$table) %in% tolower(met$table)
bib[!test,]

readr::write_csv(bib, "biblio.csv")

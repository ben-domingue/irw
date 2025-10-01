##tables on redivis
library(redivis)
red<-list()
for (dataset in c("item_response_warehouse","item_response_warehouse_2")) {
    v1<- redivis$organization("datapages")$dataset(dataset,version='latest')
    tables<-v1$list_tables()
    red[[dataset]]<-sapply(tables,function(x) x$name)
}
red<-do.call("c",red)

##tables on sheet
irw_dict <- gsheet::gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315')
gs <- irw_dict[irw_dict$`Public Reshare?`=="Public",]

##check for missing info
core_required_fields <- c("table.lower", "Description", "URL (for data)")

# Identify rows missing any core field
missing_core <- apply(irw_dict[, core_required_fields], 1, function(row) {
  any(is.na(row) | trimws(row) == "")
})
missing_license <- with(irw_dict, {
  is_public <- `Public Reshare?` == "Public"
  license_missing <- is.na(`Derived License`) | trimws(`Derived License`) == ""
  is_public & license_missing
})

# Combine both types of missing flags
flagged_rows <- irw_dict[missing_core | missing_license, ]

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

##tags
tag<-read.csv("tags.csv")

L<-list(red=red,gs=gs$table,bib=bib$table,met=met$table,tag=tag$table)
x<-data.frame(table=tolower(red),red=1)
for (i in 2:5) {
    y<-data.frame(table=tolower(L[[i]]),zz=1)
    names(y)[2]<-names(L)[i]
    x<-merge(x,y,by='table',all=TRUE)
}

##duplicated table names
cnt<-base::table(x$table)
names(cnt)[cnt>1]
for (i in 1:length(L)) {
    tab<-base::table(L[[i]])
    print(tab[tab>1])
}

##counting duplicates
n<-rowSums(x[,-1],na.rm=TRUE)
x[order(n),]
dim(x)
base::table(n,useNA='always')
z<-x[n<4,]
tmp<-z[,-6] ##no tag
nn<-rowSums(is.na(tmp))
z[nn<4,]



## ## ###################################################33
## ##eliminating duplicate biblio.csv entries

## met<-read.csv("metadata.csv")
## length(unique(met$table))
## bib<-read.csv("biblio.csv")
## tab<-base::table(bib$table)
## nm<-names(tab)[tab>1]
## hold<-bib[!(bib$table %in% nm),]
## x<-bib[bib$table %in% nm,]
## length(unique(x$table))
## L<-split(x,x$table)
## f<-function(z) {
##     z2<-z[!is.na(z[,2]),]
##     if (nrow(z2)==1) tr<-z2 else {
##                                 z2<-z[!is.na(z$Derived_License),]
##                                 if (nrow(z2)==1) tr<-z2
##                             }
##     tr
## }
## L<-lapply(L,f)
## table(sapply(L,nrow))


## bib<-data.frame(rbind(hold,do.call("rbind",L)))
## length(unique(bib$table))
## test<-tolower(bib$table) %in% tolower(met$table)
## bib[!test,]

## readr::write_csv(bib, "biblio.csv")



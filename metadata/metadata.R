#tables from last version of metadata
library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta:bdxt:v2_1")
table <- dataset$table("metadata:h5gs")
meta <- table$to_tibble()
dim(meta)
old.tables<-meta$dataset_name

##new tables
library(redivis)
v1<- redivis::organization("datapages")$dataset("Item Response Warehouse")
tables<-v1$list_tables()
new.tables<-sapply(tables,function(x) x$name)
length(new.tables)

##to add
toadd<-new.tables %in% old.tables
print("add")
new.tables[!toadd]
##to remove
torem<-old.tables %in% new.tables
print("remove")
old.tables[!torem]

##remove tables
dim(meta)
ii<-match(old.tables[!torem],meta$dataset_name)
if (length(ii)>0) {
    meta[ii,]
    meta<-meta[-ii,]
}
dim(meta)

f<-function(tab) {
    print(tab)
    variables <- tab$list_variables() 
    nms<-sapply(variables,function(x) x$get()$properties$name)
    stats<-lapply(variables,function(x) x$properties$statistics) #stats<-lapply(variables,function(x) x$get()$properties$statistics)
    names(stats)<-nms
    n_responses<-stats$resp$count
    if (is.null(n_responses)) {
        df <- tab$to_tibble()
        df<-df[!is.na(df$resp),]
        n_responses<-length(df$resp)
    }
    n_categories<-stats$resp$numDistinct
    n_participants<-stats$id$numDistinct
    n_items<-stats$item$numDistinct
    responses_per_participant = n_responses / n_participants
    responses_per_item = n_responses / n_items
    density = (sqrt(n_responses) / n_participants) * (sqrt(n_responses) / n_items)
    ##throttle
    i<-0
    while (i<10000000) i<-i+1
    ##
    data.frame(
            n_responses=n_responses,
            n_categories=n_categories,
            n_participants=n_participants,
            n_items=n_items,
            responses_per_participant=responses_per_participant,
            responses_per_item=responses_per_item,
            density=density
    )
}
out<-list()

nms<-new.tables[!toadd]
ii<-match(nms,new.tables)
if (length(ii)>0) {
    for (i in ii) {
        print(which(i==ii))
        out[[as.character(i)]]<-f(tables[[i]])
    }
    summaries<-data.frame(do.call("rbind",out))
    summaries$dataset_name<-nms[1:nrow(summaries)]
    library(tidyr)
    summaries_new<-as_tibble(summaries)
    length(ii)
    dim(summaries)
    head(meta)
    head(summaries_new)
    summaries<-as_tibble(rbind(meta,summaries_new))
} else summaries<-meta


str(summaries)
length(unique(summaries$dataset_name))

v1<- redivis::organization("datapages")$dataset("Item Response Warehouse")
tables<-v1$list_tables()

f  <- function(table) table$list_variables()
nms <- lapply(tables, f) # this seems to be the only part that's slow
nms

g <- function(x,variable) {
    nm <- sapply(x, function(x) x$name)  
    variable %in% nm  
}
                 
L<-list()
for (variable in c("rt","rater","wave","date","treat")) {
    L[[paste("has_",variable,sep='')]] <- sapply(nms, g,variable=variable)
}
L<-data.frame(do.call("cbind",L))
L$dataset_name<-sapply(tables,function(x) x$name)
head(L)
dim(L)                       
dim(summaries)
summaries<-merge(summaries,L)
head(summaries)
dim(summaries)

write.csv(summaries,'sum.csv',quote=FALSE,row.names=FALSE)



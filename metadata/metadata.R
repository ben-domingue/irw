#tables from last version of metadata
library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta:bdxt:v2_1")
table <- dataset$table("metadata:h5gs")
meta <- table$to_tibble()
meta<-meta[,c("dataset_name", "n_responses", "n_categories", "n_participants", 
"n_items", "responses_per_participant", "responses_per_item", 
"density")]
dim(meta)
old.tables<-meta$dataset_name
length(old.tables)

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
    dim(summaries_new)
    head(meta)
    head(summaries_new)
    nms.cols<-names(meta)
    for (nm in nms.cols) {
        test<-nm %in% names(summaries_new)
        if (!test) summaries_new[[nm]]<-NA
    }
    summaries_new<-summaries_new[,nms.cols]
    summaries<-as_tibble(rbind(meta,summaries_new))
} else {
    summaries<-meta
}

str(summaries)
length(unique(summaries$dataset_name))


#############get names for each dataset
library(redivis)
library(tibble)

# fetch all tables
dataset <- redivis::organization("datapages")$dataset("Item Response Warehouse")
dataset_tables <- dataset$list_tables()


# Extract table names and variables, storing variables as concatenated strings
table_vars_df <- tibble(
  dataset_name = sapply(dataset_tables, function(table) table$name),
  variables = sapply(dataset_tables, function(table) {
    var_list <- table$list_variables()
    paste(sapply(var_list, function(v) v$name), collapse = "| ")  # Concatenate variables
  })
)

x<-merge(summaries,table_vars_df,by='dataset_name')
dim(x)

write.csv(x,'metadata.csv',quote=FALSE,row.names=FALSE)

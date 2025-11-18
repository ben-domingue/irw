
##################################################################################
##Construct metadata.csv

##tables from last version of metadata
library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta:bdxt:latest")
table <- dataset$table("metadata:h5gs")
meta <- table$to_tibble()
meta<-meta[,c("table", "n_responses", "n_categories", "n_participants", 
              "n_items", "responses_per_participant", "responses_per_item", 
              "density")]
dim(meta)
old.tables<-meta$table
length(old.tables)

##new tables
tables<-new.tables<-list()
for (dataset in c("item_response_warehouse","item_response_warehouse_2")) {
     v1<- redivis$organization("datapages")$dataset(dataset)
     tabs<-v1$list_tables()
     new.tables[[dataset]]<-data.frame(table=sapply(tabs,function(x) x$name),dataset=dataset)
     tables[[dataset]]<-tabs
}
nt<-data.frame(do.call("rbind",new.tables))
new.tables<-nt$table
tables<-do.call("c",tables)

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
ii<-match(old.tables[!torem],meta$table)
if (length(ii)>0) {
  meta[ii,]
  meta<-meta[-ii,]
}
dim(meta)

f<-function(tab) {
  getvars<-function(tab) {
      variables <- tab$list_variables() 
      nms<-sapply(variables,function(x) x$get()$properties$name)
      stats<-lapply(variables,function(x) x$get_statistics() ) 
      ##
      names(stats)<-nms
      n_responses<-stats$resp$count
      if (is.null(n_responses)) {
          df <- tab$to_tibble()
          df<-df[!is.na(df$resp),]
          n_responses<-length(df$resp)
      }
      ##
      #n_categories<-stats$resp$numDistinct #see june 13 2025 email 'Redivis API deprecation notice for "statistics" property on variable.get endpoint'
      resp.index<-which(nms=="resp")
      variable<-variables[[resp.index]]
      out<-variable$get_statistics()
      out<-out$frequencyDistribution
      z<-lapply(out,function(x) x$value)
      z<-z[!sapply(z,is.null)]
      ncats<-as.numeric(unlist(z))
      n_categories<-length(ncats[!is.na(ncats)])
      ##
      n_participants<-stats$id$numDistinct
      n_items<-stats$item$numDistinct
      responses_per_participant = n_responses / n_participants
      responses_per_item = n_responses / n_items
      density = (sqrt(n_responses) / n_participants) * (sqrt(n_responses) / n_items)
      ##throttle
                                        #i<-0
                                        #while (i<10000000) i<-i+1
      ##
      testvec<-c(n_responses=n_responses,
                 n_categories=n_categories,
                 n_participants=n_participants,
                 n_items=n_items,
                 responses_per_participant=responses_per_participant,
                 responses_per_item=responses_per_item,
                 density=density)
      testvec
  }
  try.counter<-0
  while (try.counter<4) { #sometimes the download fails, this gives multiple tries to get that
      testvec<-getvars(tab)
      if (length(testvec)==7) try.counter<-100 else try.counter<-try.counter+1
  }
  return(testvec)
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
  summaries$table<-nms[1:nrow(summaries)]
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
length(unique(summaries$table))

##add dataset
summaries<-merge(summaries,nt)

##get variable names for each dataset
library(redivis)
library(tibble)


# fetch all tables
dataset_tables<-list()
for (dataset in unique(summaries$dataset)) {
    ds <- redivis$organization("datapages")$dataset(dataset) ##edited
    dataset_tables[[dataset]] <- ds$list_tables()
}
dataset_tables<-unlist(dataset_tables)

# Extract table names and variables, storing variables as concatenated strings
table_vars_df <- tibble(
  table = sapply(dataset_tables, function(table) table$name),
  variables = sapply(dataset_tables, function(table) {
    var_list <- table$list_variables()
    paste(sapply(var_list, function(v) v$name), collapse = "| ")  # Concatenate variables
  })
)

meta<-merge(summaries,table_vars_df,by='table')
dim(meta)
meta$variables<-tolower(meta$variables) ##https://github.com/itemresponsewarehouse/Rpkg/issues/109

##add longitudinal flag, https://github.com/ben-domingue/irw/issues/1167#issue-3519409612
i1<- grepl("wave",meta$variables)
i2<- grepl("date",meta$variables)
meta$longitudinal<-i1 | i2
                                        ##tabs.pkg<-irw_filter(longitudinal=TRUE,density=NULL) ##confirming
                                        ##tabs.meta<-meta$table[meta$longitudinal]

write.csv(meta,'metadata.csv',quote=FALSE,row.names=FALSE)

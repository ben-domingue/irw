
##################################################################################
##Construct metadata.csv

##tables from last version of metadata
library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta")
table <- dataset$table("metadata")
meta <- table$to_tibble()
if (!"variables" %in% names(meta)) meta$variables <- NA_character_ ##first run after this fix, or a historical gap -- forces a one-time refetch for those rows below rather than crashing
meta<-meta[,c("table", "n_responses", "n_categories", "n_participants",
              "n_items", "responses_per_participant", "responses_per_item",
              "density", "variables")]
dim(meta)
old.tables<-meta$table
length(old.tables)

##new tables
tables<-new.tables<-list()
for (dataset in c("item_response_warehouse","item_response_warehouse_2","item_response_warehouse_3","item_response_warehouse_4")) {
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
      had_error<-FALSE
      testvec<-tryCatch(getvars(tab), error=function(e) {
          message("  ! request failed (attempt ", try.counter+1, "/4): ", conditionMessage(e))
          had_error<<-TRUE
          NULL
      })
      if (had_error) Sys.sleep(5) #network failure -- back off before retrying
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

##get variable names -- only for tables missing them (newly added tables,
##or any historical row where 'variables' was never recorded). Reuse the
##already-known value for every other table instead of re-calling
##list_variables() for ~2000+ already-known tables on every single run
##(this loop used to do exactly that, unconditionally, and was the reason
##a plain run_pipeline.sh run could take 2+ hours -- see TODO.md). `tables`/
##`new.tables` (built above at the "new tables" step) already cover every
##currently-live table, old and new alike, so no need to re-fetch
##list_tables() a second time either.
need_vars <- which(is.na(summaries$variables) | summaries$variables=="")
if (length(need_vars)>0) {
  jj <- match(summaries$table[need_vars], new.tables)
  new_vars <- sapply(jj, function(i) {
    var_list <- tables[[i]]$list_variables()
    paste(sapply(var_list, function(v) v$name), collapse = "| ")
  })
  summaries$variables[need_vars] <- new_vars
}
meta <- summaries
dim(meta)
meta$variables<-tolower(meta$variables) ##https://github.com/itemresponsewarehouse/Rpkg/issues/109

##add longitudinal flag, https://github.com/ben-domingue/irw/issues/1167#issue-3519409612
i1<- grepl("wave",meta$variables)
i2<- grepl("date",meta$variables)
meta$longitudinal<-i1 | i2
                                        ##tabs.pkg<-irw_filter(longitudinal=TRUE,density=NULL) ##confirming
                                        ##tabs.meta<-meta$table[meta$longitudinal]

write.csv(meta,'metadata.csv',quote=FALSE,row.names=FALSE)


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
##incremental fetch cache. The loop below can run for hours (~550 tables on a
##big week) and used to accumulate everything in memory until the single
##write.csv() at the bottom, so any interruption -- a laptop shutdown, a
##dropped connection -- threw away the entire run. Each table's stats are now
##appended to metadata_fetch_cache.csv as soon as they come back, and a re-run
##reuses whatever is already there and fetches only the remainder. It is a
##pure cache: deleting the file just means the next run refetches. Entries
##older than cache.max.age.days are ignored so stale stats can't leak in.
cache.file<-'metadata_fetch_cache.csv'
stat.cols<-c("n_responses","n_categories","n_participants","n_items",
             "responses_per_participant","responses_per_item","density")
cache.cols<-c("table",stat.cols,"fetched_at")
cache.max.age.days<-30

read_cache<-function() {
  empty<-setNames(data.frame(matrix(numeric(0),nrow=0,ncol=length(cache.cols)),
                             stringsAsFactors=FALSE),cache.cols)
  if (!file.exists(cache.file)) return(empty)
  cc<-tryCatch(read.csv(cache.file,stringsAsFactors=FALSE),
               error=function(e) {
                 message("  ! unreadable ",cache.file,", ignoring it: ",conditionMessage(e))
                 NULL
               })
  if (is.null(cc) || nrow(cc)==0 || !all(cache.cols %in% names(cc))) return(empty)
  cc<-cc[,cache.cols]
  age<-difftime(Sys.time(),as.POSIXct(cc$fetched_at,tz="UTC"),units="days")
  cc<-cc[!is.na(age) & age<=cache.max.age.days,]
  cc[!duplicated(cc$table,fromLast=TRUE),] ##newest entry for a table wins
}

append_cache<-function(tabname,testvec) {
  row<-as.data.frame(c(list(table=tabname),as.list(testvec),
                       list(fetched_at=format(Sys.time(),tz="UTC"))),
                     stringsAsFactors=FALSE)
  had.file<-file.exists(cache.file)
  write.table(row[,cache.cols],cache.file,sep=",",row.names=FALSE,
              col.names=!had.file,append=had.file)
}

nms<-new.tables[!toadd]
if (length(nms)>0) {
  cached<-read_cache()
  cached<-cached[cached$table %in% nms,]
  if (nrow(cached)>0) message("resuming: ",nrow(cached)," of ",length(nms),
                              " tables already fetched in ",cache.file)
  todo<-nms[!(nms %in% cached$table)]
  for (k in seq_along(todo)) {
    print(paste0(k,"/",length(todo)," ",todo[k]))
    i<-match(todo[k],new.tables)
    testvec<-f(tables[[i]])
    if (length(testvec)==7) append_cache(todo[k],testvec) else
      message("  ! giving up on ",todo[k]," -- no stats after 4 attempts")
  }
  fetched<-read_cache()
  fetched<-fetched[fetched$table %in% nms,]
  dropped<-setdiff(nms,fetched$table)
  if (length(dropped)>0) message("no stats for ",length(dropped)," table(s), left out of metadata.csv: ",
                                 paste(dropped,collapse=", "))
}
library(tidyr)
if (length(nms)>0 && nrow(fetched)>0) {
  summaries_new<-as_tibble(fetched[,c("table",stat.cols)])
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

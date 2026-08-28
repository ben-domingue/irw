
##################################################################################
##Construct metadata.csv

##Write plain integers, never scientific notation. With R's default scipen=0,
##write.csv() emits whichever representation is shorter, so the biggest tables
##in the warehouse were being published at TWO significant digits: metadata.csv
##held enem_2023_1mil_cn as n_responses=4.5e+07 (really 44,986,496) and
##n_participants=1e+06 (really 999,722). A 2026-08-24 audit found 98 such cells
##across 43 tables, all of them the large enem_* shards. The values were correct
##in memory and only lost precision at write time, so this one line fixes every
##affected row on the next run.
options(scipen=999)

##tables from last version of metadata
library(redivis)
source("redivis_config.R")
user <- redivis$user(IRW_OWNER)
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
for (dataset in IRW_CORE_DATASETS) {
     v1<- redivis$organization(IRW_OWNER)$dataset(dataset)
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

##Server-side row count, used when a variable's precomputed `count` statistic
##comes back NULL. This used to be `df <- tab$to_tibble(); sum(!is.na(df$resp))`,
##i.e. download the entire table just to count its rows. Redivis caps *data
##export* at 200 GB per rolling 30 days per user and the core warehouse is
##181.8 GB across its four shards, so a handful of large tables falling into
##that fallback is enough to burn the month's allowance -- which is what
##happened on 2026-08-18 (204 GB used account-wide), blocking irw_fetch() for
##every user and every table until the window rolled over. Queries are not
##subject to the export cap, and this one returns a single row, so the same
##number now costs nothing against the quota.
##
##The filter is `resp IS NOT NULL` and nothing more, because that is exactly
##what the `count` statistic on the main path reports -- confirmed on
##polca_election (21,420 rows, 1,292 NULL resp, count = 20,128). Do NOT also
##exclude the literal "NA" token here: 310 of the 3,024 core tables have a
##string-typed `resp`, and on those the token is common (dscore_denver_
##weber_2019 is 118,589 of 142,899 rows). The `count` statistic counts those
##rows, the old to_tibble() fallback counted them too (R reads "NA" in a
##character column as the string "NA", not as NA), and the n_responses
##already published in metadata.csv includes them. Filtering the token out
##here would make the fallback disagree with the main path on exactly those
##tables. Dropping "NA" responses corpus-wide may well be the right call, but
##it is a deliberate change to what n_responses means, and it belongs on the
##main path, not hidden in a fallback.
count_resp_via_query<-function(tab) {
  ref<-tab$qualified_reference
  sql<-sprintf("SELECT COUNT(*) AS n FROM `%s` WHERE resp IS NOT NULL", ref)
  res<-redivis$query(sql)$to_tibble()
  n<-as.numeric(res$n[1])
  if (length(n)!=1 || is.na(n)) stop("count query returned no value for ",ref)
  n
}

f<-function(tab) {
  getvars<-function(tab) {
      variables <- tab$list_variables() 
      nms<-sapply(variables,function(x) x$get()$properties$name)
      stats<-lapply(variables,function(x) x$get_statistics() ) 
      ##
      names(stats)<-nms
      n_responses<-stats[["resp"]]$count ##[[ ]] not $: $ partial-matches e.g. a lone `resp_time`
      if (is.null(n_responses)) {
          message("  no server-side resp count for ",tab$name,"; counting via query")
          n_responses<-count_resp_via_query(tab)
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
  last.err<-NA_character_
  while (try.counter<4) { #sometimes the download fails, this gives multiple tries to get that
      had_error<-FALSE
      testvec<-tryCatch(getvars(tab), error=function(e) {
          message("  ! request failed (attempt ", try.counter+1, "/4): ", conditionMessage(e))
          had_error<<-TRUE
          last.err<<-conditionMessage(e)
          NULL
      })
      if (had_error) Sys.sleep(5) #network failure -- back off before retrying
      if (length(testvec)==7) try.counter<-100 else try.counter<-try.counter+1
  }
  ##the refresh pass below needs to tell "this table is gone" apart from "the
  ##network flaked", so carry the last error message back with the result
  if (length(testvec)!=7) attr(testvec,"last.error")<-last.err
  return(testvec)
}

##Does an error message mean the table genuinely no longer exists, as opposed
##to a transient network/API failure? Only a definite not-found is treated as
##dead; anything else leaves the existing row untouched. See the refresh pass
##below for why this distinction matters.
is_missing_table_error<-function(msg) {
  if (is.null(msg) || is.na(msg)) return(FALSE)
  grepl("not[ _]?found|404|does not exist|no such table", msg, ignore.case=TRUE)
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

##Rolling refresh of ALREADY-KNOWN tables.
##
##Until 2026-08-24 this script only ever fetched stats for tables that were new
##since the last run, so a table that got re-uploaded to Redivis kept its
##original metadata.csv row forever. A corpus scan on 2026-08-18 found 47 rows
##whose server-side count no longer matched what metadata.csv published --
##western_reserve_project was 1,445,422 on Redivis vs 1,066,535 published, and
##mhscdc_fried_2020_dass was out by exactly a factor of two. That scan also
##found 8 rows (enem_2023_1mil_* and enem_2024_1mil_*) that list_tables() still
##returns but which 404 on access, so the "remove tables" step near the top of
##this script cannot see them -- from its point of view they are still live.
##
##Both problems have the same cause (existing rows are never revisited) and the
##same fix: re-fetch a slice of the existing rows on every run. Counting is a
##query now rather than a table export, so this costs nothing against the
##200 GB/30-day export quota; the cost is API latency, hence the per-run cap.
##
##refresh.per.run tables are refreshed each run, oldest-first by last refresh,
##so the corpus is swept on a rolling basis. Set to 0 to disable the pass
##entirely. The log is deliberately a SEPARATE file from cache.file: the fetch
##cache expires after cache.max.age.days (it exists to resume an interrupted
##run), whereas the refresh log must persist indefinitely to drive the rotation.
refresh.per.run<-200
refresh.log.file<-'metadata_refresh_log.csv'
dead.tables.file<-'metadata_dead_tables.csv'

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

##---------------------------------------------------------------------------
##Rolling refresh pass (see refresh.per.run above for the why).
##Re-fetch stats for a slice of the tables that were ALREADY in metadata.csv,
##oldest-refreshed first, and update their rows in place. Tables fetched
##earlier in this same run are excluded -- their numbers are already current.
##---------------------------------------------------------------------------
read_refresh_log<-function() {
  empty<-data.frame(table=character(0),refreshed_at=character(0),stringsAsFactors=FALSE)
  if (!file.exists(refresh.log.file)) return(empty)
  rl<-tryCatch(read.csv(refresh.log.file,stringsAsFactors=FALSE),
               error=function(e) {
                 message("  ! unreadable ",refresh.log.file,", ignoring it: ",conditionMessage(e))
                 NULL
               })
  if (is.null(rl) || nrow(rl)==0 || !all(c("table","refreshed_at") %in% names(rl))) return(empty)
  rl<-rl[,c("table","refreshed_at")]
  rl[!duplicated(rl$table,fromLast=TRUE),] ##newest entry per table wins
}

if (refresh.per.run>0) {
  just.fetched<-if (length(nms)>0) nms else character(0)
  candidates<-setdiff(intersect(summaries$table,new.tables),just.fetched)
  rlog<-read_refresh_log()
  ##never-refreshed tables sort first, then oldest refresh first
  last.at<-rlog$refreshed_at[match(candidates,rlog$table)]
  last.time<-suppressWarnings(as.POSIXct(last.at,tz="UTC"))
  ord<-order(is.na(last.time)==FALSE, last.time, candidates) ##NA (never) first, then oldest, name as tiebreak
  todo.refresh<-head(candidates[ord],refresh.per.run)
  message("refresh pass: ",length(todo.refresh)," of ",length(candidates),
          " existing table(s) this run (refresh.per.run=",refresh.per.run,")")

  refreshed.rows<-list(); dead<-character(0); flaky<-character(0); changed<-list()
  for (k in seq_along(todo.refresh)) {
    tb<-todo.refresh[k]
    message("  refresh ",k,"/",length(todo.refresh)," ",tb)
    i<-match(tb,new.tables)
    testvec<-f(tables[[i]])
    if (length(testvec)==7) {
      old<-summaries[summaries$table==tb,stat.cols,drop=FALSE]
      new<-as.numeric(testvec[stat.cols])
      oldv<-suppressWarnings(as.numeric(unlist(old[1,])))
      if (length(oldv)==length(new) && !isTRUE(all.equal(oldv,new))) {
        changed[[tb]]<-data.frame(table=tb,
                                  column=stat.cols,
                                  old_value=oldv,
                                  new_value=new,
                                  stringsAsFactors=FALSE)[oldv!=new | is.na(oldv)!=is.na(new),]
      }
      for (cc in stat.cols) summaries[summaries$table==tb,cc]<-testvec[[cc]]
      refreshed.rows[[tb]]<-data.frame(table=tb,
                                       refreshed_at=format(Sys.time(),tz="UTC"),
                                       stringsAsFactors=FALSE)
    } else {
      err<-attr(testvec,"last.error")
      if (is_missing_table_error(err)) {
        dead<-c(dead,tb)
        message("  !! ",tb," is listed by list_tables() but does not resolve -- marking dead")
      } else {
        flaky<-c(flaky,tb)
        message("  ! ",tb," failed to refresh (kept as-is): ",if (is.null(err)) "unknown" else err)
      }
    }
  }

  ##report what actually moved -- this is the 47-stale-rows problem made visible
  if (length(changed)>0) {
    chg<-do.call("rbind",changed)
    message("refresh: ",length(changed)," table(s) had stats that no longer matched metadata.csv")
    print(utils::head(chg,40))
    write.csv(chg,'metadata_refresh_changes.csv',row.names=FALSE)
  } else message("refresh: no stat changes among the refreshed tables")

  ##dead tables: drop the row AND record it, so the enem_2023/2024-style rows
  ##cannot sit in metadata.csv indefinitely. Only definite not-found errors get
  ##here; transient failures land in `flaky` and leave the row alone.
  if (length(dead)>0) {
    message("refresh: dropping ",length(dead)," dead table(s) from metadata.csv: ",
            paste(dead,collapse=", "))
    prev.dead<-if (file.exists(dead.tables.file)) {
      tryCatch(read.csv(dead.tables.file,stringsAsFactors=FALSE),error=function(e) NULL)
    } else NULL
    dd<-data.frame(table=dead,detected_at=format(Sys.time(),tz="UTC"),stringsAsFactors=FALSE)
    if (!is.null(prev.dead) && all(c("table","detected_at") %in% names(prev.dead)))
      dd<-rbind(prev.dead[,c("table","detected_at")],dd)
    write.csv(dd[!duplicated(dd$table,fromLast=TRUE),],dead.tables.file,row.names=FALSE)
    summaries<-summaries[!(summaries$table %in% dead),]
  }
  if (length(flaky)>0)
    message("refresh: ",length(flaky)," table(s) failed transiently and were left unchanged: ",
            paste(flaky,collapse=", "))

  ##only log tables we actually refreshed, so a failure retries next run rather
  ##than going to the back of the queue
  if (length(refreshed.rows)>0) {
    newlog<-do.call("rbind",refreshed.rows)
    allog<-rbind(read_refresh_log(),newlog)
    write.csv(allog[!duplicated(allog$table,fromLast=TRUE),],refresh.log.file,row.names=FALSE)
  }
}

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

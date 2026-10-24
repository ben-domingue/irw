
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
##
##Start from the repo's metadata.csv, not the published irw_meta.metadata table.
##Until 2026-10-07 this read the published table, so any row corrected on main
##but not yet uploaded was silently reverted: #2830 fixed 10 rows from live
##Redivis on 2026-10-05 (Aspirations_Sonmez_2022 473 people, not 265), irw_meta
##was not re-uploaded, and that night's run (#2860) wrote the stale published
##values back because the rolling refresh below happened not to revisit them.
##The repo is what this script writes and what upload_meta.py ships, so it is
##the right base; published is still read, only to report where the two differ.
##A row that differs is EXPECTED after a merged-but-unuploaded pipeline PR; one
##where published is ahead of main means irw_meta was uploaded from a branch that
##never merged, and this run will overwrite it -- check those before merging.
library(redivis)
source("redivis_config.R")
user <- redivis$user(IRW_OWNER)
dataset <- user$dataset("irw_meta")
table <- dataset$table("metadata")
published <- as.data.frame(table$to_tibble())
base.cols<-c("table", "n_responses", "n_categories", "n_participants",
             "n_items", "responses_per_participant", "responses_per_item",
             "density", "variables")
repo <- if (file.exists("metadata.csv")) {
  tryCatch(read.csv("metadata.csv",stringsAsFactors=FALSE,colClasses=c(table="character",variables="character")),
           error=function(e) { message("  ! unreadable metadata.csv: ",conditionMessage(e)); NULL })
} else NULL
if (!is.null(repo) && nrow(repo)>0 && all(base.cols %in% names(repo))) {
  meta <- repo
  message("base: repo metadata.csv (",nrow(repo)," rows); published irw_meta.metadata has ",nrow(published))
  ##report, don't fail: the repo wins either way
  only.pub<-setdiff(published$table,repo$table)
  only.repo<-setdiff(repo$table,published$table)
  if (length(only.pub)>0) message("base: ",length(only.pub)," table(s) in published but not repo: ",paste(head(only.pub,40),collapse=", "))
  if (length(only.repo)>0) message("base: ",length(only.repo)," table(s) in repo but not published: ",paste(head(only.repo,40),collapse=", "))
  num.cols<-setdiff(intersect(base.cols,names(published)),c("table","variables"))
  both<-intersect(repo$table,published$table)
  r<-repo[match(both,repo$table),num.cols,drop=FALSE]
  p<-published[match(both,published$table),num.cols,drop=FALSE]
  differs<-sapply(seq_along(both),function(k) {
    a<-suppressWarnings(as.numeric(unlist(r[k,]))); b<-suppressWarnings(as.numeric(unlist(p[k,])))
    !isTRUE(all.equal(a,b))
  })
  if (any(differs)) {
    message("base: ",sum(differs)," table(s) whose stats differ between repo and published (repo kept): ",
            paste(head(both[differs],40),collapse=", "))
  } else message("base: repo and published agree on every shared row")
} else {
  ##no usable repo copy (fresh checkout of an old commit, or a broken file):
  ##fall back to published, which is what this script did before 2026-10-07
  message("  ! no usable metadata.csv in the working directory; starting from published irw_meta.metadata")
  meta <- published
}
if (!"variables" %in% names(meta)) meta$variables <- NA_character_ ##first run after this fix, or a historical gap -- forces a one-time refetch for those rows below rather than crashing
##One row per table. zhou_2025_peer_relationship carried two identical rows from the
##2026-09-10 rename (#2149) on, because each run started from the published table and
##nothing below removes a second copy of a name that is still live.
dup<-duplicated(meta$table)
if (any(dup)) {
  message("dropping ",sum(dup)," duplicate row(s) from the base metadata: ",
          paste(unique(meta$table[dup]),collapse=", "))
  meta<-meta[!dup,]
}
meta<-meta[,base.cols]
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

##Per-table statistics (count_resp_via_query, f, is_missing_table_error) live
##in table_stats.R, so metadata/refresh_rows.R computes the same numbers from
##the same statistics rather than reimplementing them. See its header.
source("table_stats.R")

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
##
##400, not 200, from 2026-10-18. The rotation only started persisting across
##Actions runs on 2026-10-02 (#2785 -- before that each run lost the log and
##re-refreshed the same slice), so as of 2026-10-18 it had covered 1,000 of
##5,880 rows and 4,881 tables had never been re-checked at all. At 200 a run
##and two runs a week that backlog is ~24 runs, about three months. It matters
##more than it used to because the per-table statistics this pass computes are
##what a psychometric-property filter would be built on (#1710): a column that
##fills over a quarter is not a filter anyone can use.
##
##Why 400 and not more: the pass is MEASURED at ~10.3 s/table, not the "~10
##min for 200" that was in circulation, nor the 45-60 min guessed in
##pipeline_logs/NEXT_RUN_NOTES.md. In run 38778585737 (2026-10-15) it ran
##17:48:11 -> 18:22:29 UTC for 200 tables -- 34 minutes -- inside a stage 01
##that took 44.5 minutes in total. So each extra 200 costs ~34 minutes of job
##time, forever, on every run. 400 puts stage 01 near 78 min and a heavy run
##near 150 against the 240-minute timeout; 600 would put a 692-new-table week
##within ~50 minutes of being cancelled, and a cancelled run costs a dispatch
##and a second review. With the Mon/Wed/Fri schedule, 400 sweeps the corpus in
##~15 runs, about five weeks. Raise it once a run at 400 has been timed.
refresh.per.run<-400
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
##The log records WHAT WAS SEEN as well as when, because the when alone cannot
##answer "is this row still a true statement about the table?". Redivis resets
##every table's `updatedAt` whenever the draft it sits in is touched
##(ARCHITECTURE.md section 4), so a timestamp comparison calls the whole corpus
##stale: all 1,031 tables in shards 7 and 8 reported an October 2026 `updatedAt`
##on 2026-10-24. The content `hash` does not move unless the table does, so
##`hash` here against the live `hash` is the freshness test that works, and it is
##what metadata/check_release_consistency.py compares. Rows written before this
##change carry no hash; the gate reports those as unknown rather than as stale,
##and they fill in as the rotation reaches them.
refresh.log.cols<-c("table","refreshed_at","num_rows","hash")
read_refresh_log<-function() {
  empty<-setNames(data.frame(matrix(character(0),nrow=0,ncol=length(refresh.log.cols)),
                             stringsAsFactors=FALSE),refresh.log.cols)
  if (!file.exists(refresh.log.file)) return(empty)
  rl<-tryCatch(read.csv(refresh.log.file,stringsAsFactors=FALSE),
               error=function(e) {
                 message("  ! unreadable ",refresh.log.file,", ignoring it: ",conditionMessage(e))
                 NULL
               })
  if (is.null(rl) || nrow(rl)==0 || !all(c("table","refreshed_at") %in% names(rl))) return(empty)
  for (cc in refresh.log.cols) if (!cc %in% names(rl)) rl[[cc]]<-NA ##logs written before the hash columns existed
  rl<-rl[,refresh.log.cols]
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
      ##...and the column list, which is the half of the row that used never to
      ##be revisited. See the attr() comment in getvars() above for what that
      ##cost in October 2026.
      vars.now<-attr(testvec,"variables")
      if (!is.null(vars.now) && nzchar(vars.now)) {
        vars.was<-summaries$variables[summaries$table==tb]
        if (length(vars.was)==1 && !identical(tolower(vars.was),tolower(vars.now)))
          message("    schema changed: ",tb," ",
                  length(strsplit(vars.was,"\\|")[[1]])," -> ",
                  length(strsplit(vars.now,"\\|")[[1]])," column(s)")
        summaries$variables[summaries$table==tb]<-vars.now
      }
      refreshed.rows[[tb]]<-data.frame(table=tb,
                                       refreshed_at=format(Sys.time(),tz="UTC"),
                                       num_rows=attr(testvec,"num_rows"),
                                       hash=attr(testvec,"hash"),
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
    allog<-rbind(read_refresh_log()[,refresh.log.cols],newlog[,refresh.log.cols])
    allog<-allog[!duplicated(allog$table,fromLast=TRUE),]
    ##sorted by table so the committed log diffs as changed timestamps, not moved rows
    write.csv(allog[order(allog$table),],refresh.log.file,row.names=FALSE)
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
##
##Filling a BLANK row is all this block does, and that is the whole of it: it
##cannot notice that a row which already has a column list has the WRONG one.
##That is why the refresh pass above rewrites `variables` for every table it
##visits, from a column list it already holds. The two together are what keep
##the published schema true -- this block for a table nobody has ever asked
##about, the refresh pass for one that has been rebuilt since.
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

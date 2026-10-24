##################################################################################
## Refresh metadata.csv rows for NAMED tables, now, instead of waiting for the
## rolling rotation in 01_metadata.R to reach them.
##
## WHY THIS EXISTS
##
## 01_metadata.R re-reads refresh.per.run (400) existing tables per run,
## never-refreshed first. That sweeps the corpus in about five weeks, which is
## fine for drift and useless for a row that is KNOWN to be wrong: review R-04
## (#3214) found number_pattern_game publishing n_items 255 against a true
## 25,499 -- a density of 1.765, which the site's own definition says cannot
## exceed 1 -- and review R-13 (#3213) found 58 tables publishing an
## n_responses larger than the number of rows their table has. Those rows are
## false statements about the data, and "the rotation will get there" is not an
## answer a reader of the catalog can use.
##
## metadata/check_release_consistency.py names exactly which rows those are
## (`--only counts`), so the two halves fit together: the gate finds a row the
## data contradicts, this script repairs it, and the gate's baseline comes down.
##
## It is deliberately NOT a second implementation of the statistics. The three
## functions it needs live in table_stats.R and are the ones the pipeline uses,
## so a row this script writes is the row the next pipeline run would write; a
## refresher with its own arithmetic would make the value flip between runs.
##
## USAGE (from src/metadata, with REDIVIS_API_TOKEN set)
##
##   Rscript refresh_rows.R number_pattern_game timss_tam
##   Rscript refresh_rows.R --file /tmp/tables.txt     # one name per line
##   Rscript refresh_rows.R --dry-run --file /tmp/tables.txt
##
## WHAT IT WRITES
##
##   metadata.csv              the seven statistics, `variables` and
##                             `longitudinal` for the named rows, and nothing
##                             else. Byte-for-byte the same file otherwise:
##                             CRLF, unquoted, blanks preserved.
##   metadata_refresh_log.csv  a row per table refreshed, with the live
##                             num_rows and content hash, so the gate's
##                             `freshness` check can tell afterwards whether the
##                             row still describes the table it was computed
##                             from. Timestamps cannot do that job -- Redivis
##                             resets updatedAt for every table in a draft when
##                             the draft is touched.
##
## It does NOT touch the per-item columns stage 19 adds (difficulty_spread and
## the three beside it); those have their own rotation in 19_item_classical.py.
## It does not upload anything: the irw_meta upload stays the explicit
## `upload_meta.py` step, and the release stays Ben's Publish click.
##################################################################################
options(scipen=999)  ##as 01_metadata.R: never publish a count in scientific notation

args<-commandArgs(trailingOnly=TRUE)
dry.run<-"--dry-run" %in% args
args<-args[args!="--dry-run"]
wanted<-character(0)
k<-1
while (k<=length(args)) {
  if (args[k]=="--file") {
    if (k==length(args)) stop("--file needs a path")
    wanted<-c(wanted,readLines(args[k+1]))
    k<-k+2
  } else {
    wanted<-c(wanted,args[k]); k<-k+1
  }
}
wanted<-unique(trimws(wanted))
wanted<-wanted[nzchar(wanted) & !startsWith(wanted,"#")]
if (length(wanted)==0) stop("name at least one table, or pass --file")

library(redivis)
source("redivis_config.R")
source("table_stats.R")

meta.file<-'metadata.csv'
log.file<-'metadata_refresh_log.csv'
stat.cols<-c("n_responses","n_categories","n_participants","n_items",
             "responses_per_participant","responses_per_item","density")

##Read every cell as a string and write every cell back unchanged except the
##ones refreshed below. read.csv would otherwise reformat untouched numbers
##(and turn an empty per-item cell into NA), which would put the whole file in
##the diff and hide the handful of rows that actually moved.
meta<-read.csv(meta.file,stringsAsFactors=FALSE,colClasses="character",
               na.strings=NULL,check.names=FALSE)
message("base: ",nrow(meta)," rows in ",meta.file)
missing<-setdiff(wanted,meta$table)
if (length(missing)>0)
  stop("not in ",meta.file,": ",paste(missing,collapse=", "),
       "\n(metadata.csv covers the core shards only; other families have their own CSVs)")

##Live table objects, from the shards metadata.csv actually describes.
want.datasets<-unique(meta$dataset[meta$table %in% wanted])
want.datasets<-intersect(IRW_CORE_DATASETS,want.datasets)
live<-list()
for (dataset in want.datasets) {
  tabs<-redivis$organization(IRW_OWNER)$dataset(dataset)$list_tables()
  names(tabs)<-sapply(tabs,function(x) x$name)
  live[names(tabs)]<-tabs
}
not.live<-setdiff(wanted,names(live))
if (length(not.live)>0)
  message("  ! not listed by the live shard(s), skipped: ",paste(not.live,collapse=", "))
wanted<-intersect(wanted,names(live))

moved<-list(); logged<-list(); failed<-character(0)
for (k in seq_along(wanted)) {
  tb<-wanted[k]
  message("refresh ",k,"/",length(wanted)," ",tb)
  testvec<-f(live[[tb]])
  if (length(testvec)!=7) {
    failed<-c(failed,tb)
    message("  ! no stats after 4 attempts, row left as it was: ",
            if (is.null(attr(testvec,"last.error"))) "unknown" else attr(testvec,"last.error"))
    next
  }
  i<-match(tb,meta$table)
  for (cc in stat.cols) {
    was<-meta[[cc]][i]
    now<-as.character(testvec[[cc]])
    if (!identical(was,now)) moved[[length(moved)+1]]<-
      data.frame(table=tb,column=cc,old_value=was,new_value=now,stringsAsFactors=FALSE)
    meta[[cc]][i]<-now
  }
  vars.now<-attr(testvec,"variables")
  if (!is.null(vars.now) && nzchar(vars.now)) {
    vars.now<-tolower(vars.now)  ##as 01_metadata.R, itemresponsewarehouse/Rpkg#109
    if (!identical(meta$variables[i],vars.now)) {
      moved[[length(moved)+1]]<-data.frame(table=tb,column="variables",
                                           old_value=meta$variables[i],
                                           new_value=vars.now,stringsAsFactors=FALSE)
      meta$variables[i]<-vars.now
    }
    ##the longitudinal flag is a function of the column list, so it has to move with it
    if ("longitudinal" %in% names(meta)) {
      lng<-if (grepl("wave",vars.now) || grepl("date",vars.now)) "TRUE" else "FALSE"
      if (!identical(meta$longitudinal[i],lng)) {
        moved[[length(moved)+1]]<-data.frame(table=tb,column="longitudinal",
                                             old_value=meta$longitudinal[i],
                                             new_value=lng,stringsAsFactors=FALSE)
        meta$longitudinal[i]<-lng
      }
    }
  }
  logged[[tb]]<-data.frame(table=tb,refreshed_at=format(Sys.time(),tz="UTC"),
                           num_rows=attr(testvec,"num_rows"),
                           hash=attr(testvec,"hash"),stringsAsFactors=FALSE)
}

if (length(moved)>0) {
  chg<-do.call("rbind",moved)
  message("moved: ",length(unique(chg$table))," table(s), ",nrow(chg)," cell(s)")
  print(chg,row.names=FALSE)
} else message("moved: nothing -- every refreshed row already matched the data")
if (length(failed)>0) message("failed: ",paste(failed,collapse=", "))

if (dry.run) {
  message("--dry-run: ",meta.file," and ",log.file," left alone")
} else {
  ##CRLF, unquoted, blanks as blanks: the canonical form of this file, as
  ##19_item_classical.py's write_csv leaves it. No cell in metadata.csv has ever
  ##contained a comma or a quote -- `variables` is pipe-separated for that very
  ##reason -- so quote=FALSE round-trips exactly.
  bad<-sapply(meta,function(col) any(grepl('[",]',col)))
  if (any(bad)) stop("a cell now contains a comma or a quote, which quote=FALSE would corrupt: ",
                     paste(names(meta)[bad],collapse=", "))
  write.table(meta,meta.file,sep=",",quote=FALSE,row.names=FALSE,na="",eol="\r\n")
  message("wrote ",meta.file)

  if (length(logged)>0) {
    refresh.log.cols<-c("table","refreshed_at","num_rows","hash")
    rl<-if (file.exists(log.file)) read.csv(log.file,stringsAsFactors=FALSE) else NULL
    if (!is.null(rl) && nrow(rl)>0) {
      for (cc in refresh.log.cols) if (!cc %in% names(rl)) rl[[cc]]<-NA  ##logs written before the hash columns existed
      rl<-rl[,refresh.log.cols]
    } else rl<-NULL
    newlog<-do.call("rbind",logged)
    allog<-if (is.null(rl)) newlog[,refresh.log.cols] else rbind(rl,newlog[,refresh.log.cols])
    allog<-allog[!duplicated(allog$table,fromLast=TRUE),]
    ##sorted by table, as 01_metadata.R writes it, so the diff is changed
    ##timestamps rather than moved rows
    write.csv(allog[order(allog$table),],log.file,row.names=FALSE)
    message("logged ",length(logged)," table(s) in ",log.file)
  }
}

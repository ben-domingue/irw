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
## 25,499, and with it a density of 1.765 against a true 0.018 -- and review
## R-13 (#3213) found 58 tables publishing an n_responses larger than the
## number of rows their table has. Those rows are
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
##   Rscript refresh_rows.R --family nom wilmer-mrmet-normative-data-set-2022_nom
##
## FAMILIES
##
##   --family core     metadata.csv          (the default)
##           comps     comps_metadata.csv
##           nom       nominal_metadata.csv
##           simsyn    simsyn_metadata.csv
##
## The three non-core families matter more than core does here, not less: core
## has 01_metadata.R's rolling refresh, so a stale row there is corrected within
## about five weeks on its own. 05_comps.R, 06_nominal.R and 07_simsyn.R have no
## refresh pass at all -- a row is written when the table first appears and
## never revisited -- so for those three catalogues this script is the ONLY way
## a published number gets corrected. #3213 found
## `wilmer-mrmet-normative-data-set-2022_nom` publishing 343,876 responses
## against 343,276 real rows and 40 categories against a true 4, and it had to
## be fixed by hand for exactly that reason.
##
## Each family's statistics come from family_stats.R, which holds the stage's
## own function, so a refreshed row is the row that stage would write. What gets
## written differs by family, because the catalogues differ: comps has two
## numbers and no column list, nominal has five and counts categories on `text`
## rather than `resp`, simsyn has the seven core ones.
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
family<-"core"
fi<-match("--family",args)
if (!is.na(fi)) {
  if (fi==length(args)) stop("--family needs one of: core, comps, nom, simsyn")
  family<-args[fi+1]
  args<-args[-c(fi,fi+1)]
}
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
source("family_stats.R")

##One row per catalogue. `stat.cols` is that catalogue's own column list and
##nothing more: writing a column a family does not have would add it to the CSV,
##and writing one it has but the stage does not compute would overwrite a real
##value with NA. `cols` is how many values the stage's function returns on
##success, which is how it reports failure after four attempts.
FAMILIES<-list(
  core=list(csv="metadata.csv", log="metadata_refresh_log.csv", fn=f, cols=7,
            datasets=NULL,  ##taken from the CSV's own `dataset` column
            stat.cols=c("n_responses","n_categories","n_participants","n_items",
                        "responses_per_participant","responses_per_item","density")),
  comps=list(csv="comps_metadata.csv", log="logs/comps_refresh_log.csv", fn=f_comps, cols=2,
             datasets=FAMILY_DATASETS$comps,
             stat.cols=c("n_responses","n_actors")),
  nom=list(csv="nominal_metadata.csv", log="logs/nominal_refresh_log.csv", fn=f_nominal, cols=5,
           datasets=FAMILY_DATASETS$nom,
           stat.cols=c("n_responses","n_participants","n_items",
                       "responses_per_participant","n_categories")),
  simsyn=list(csv="simsyn_metadata.csv", log="logs/simsyn_refresh_log.csv", fn=f_simsyn, cols=7,
              datasets=FAMILY_DATASETS$simsyn,
              stat.cols=c("n_responses","n_categories","n_participants","n_items",
                          "responses_per_participant","responses_per_item","density")))
if (!family %in% names(FAMILIES))
  stop("--family must be one of: ",paste(names(FAMILIES),collapse=", "))
cfg<-FAMILIES[[family]]
f<-cfg$fn
stats.len<-cfg$cols
meta.file<-cfg$csv
log.file<-cfg$log
stat.cols<-cfg$stat.cols
message("family: ",family," -> ",meta.file)

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
       "\n(each family has its own CSV; pass --family comps, nom or simsyn)")

##Live table objects. Core is spread over the shards its own CSV names, and the
##intersect() keeps a stale `dataset` cell from sending us to a dataset that is
##no longer a core shard. The other three families live in one dataset each, and
##nominal_metadata.csv has no `dataset` column at all, so the family says where
##to look.
if (is.null(cfg$datasets)) {
  want.datasets<-unique(meta$dataset[meta$table %in% wanted])
  want.datasets<-intersect(IRW_CORE_DATASETS,want.datasets)
} else {
  want.datasets<-cfg$datasets
}
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
  if (length(testvec)!=stats.len) {
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
  if (!is.null(vars.now) && nzchar(vars.now) && "variables" %in% names(meta)) {
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
  ##Only table_stats.R's core function carries the live num_rows and hash back,
  ##because only it is given the list_tables() properties to read them from. The
  ##three family functions return the statistics alone, so their log rows record
  ##that the refresh happened and leave the freshness columns blank rather than
  ##dropping them -- data.frame() silently discards a NULL argument, and the
  ##column would then be missing when this binds onto the existing log.
  or.na<-function(x) if (is.null(x) || length(x)==0) NA else x
  logged[[tb]]<-data.frame(table=tb,refreshed_at=format(Sys.time(),tz="UTC"),
                           num_rows=or.na(attr(testvec,"num_rows")),
                           hash=or.na(attr(testvec,"hash")),stringsAsFactors=FALSE)
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
  ##Unquoted, blanks as blanks, and the line ending the file already had. No
  ##cell in any of these CSVs has ever contained a comma or a quote --
  ##`variables` is pipe-separated for that very reason -- so quote=FALSE
  ##round-trips exactly.
  ##
  ##The ending is READ rather than assumed, because the four files disagree:
  ##metadata.csv and nominal_metadata.csv are CRLF (19_item_classical.py's
  ##write_csv, and 06_nominal.R), while comps_metadata.csv and
  ##simsyn_metadata.csv are LF. Writing CRLF unconditionally, as this did when it
  ##served core alone, converted every line of the two LF files and put the whole
  ##catalogue in the diff -- which is the exact failure the surrounding care
  ##about formatting exists to prevent, since it hides the handful of rows that
  ##actually moved.
  bad<-sapply(meta,function(col) any(grepl('[",]',col)))
  if (any(bad)) stop("a cell now contains a comma or a quote, which quote=FALSE would corrupt: ",
                     paste(names(meta)[bad],collapse=", "))
  first<-readLines(meta.file,n=1,warn=FALSE)
  raw1<-readBin(meta.file,"raw",n=nchar(first,type="bytes")+2L)
  eol<-if (length(raw1)>0 && any(raw1==as.raw(13))) "\r\n" else "\n"
  message("line ending: ",if (identical(eol,"\r\n")) "CRLF" else "LF"," (as found)")
  write.table(meta,meta.file,sep=",",quote=FALSE,row.names=FALSE,na="",eol=eol)
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

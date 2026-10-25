##################################################################################
## Per-table statistics, shared by the metadata pipeline and the targeted
## refresher.
##
## These three functions were defined inside 01_metadata.R until 2026-10-24.
## They moved here so that `refresh_rows.R` -- which re-reads a NAMED set of
## tables rather than waiting for the rolling rotation to reach them -- computes
## exactly the numbers the pipeline computes, from exactly the same Redivis
## statistics. A one-off refresher with its own arithmetic would disagree with
## the next pipeline run, and the row would flip back and forth; review R-04
## and R-13 (issues #3214, #3213) are about published numbers that are not true
## of the table, which a flip-flop would merely rename.
##
## Requires `redivis` and a sourced redivis_config.R, as 01_metadata.R does.
##################################################################################

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
      ##`density` is RESPONSES PER PERSON-ITEM CELL: n_responses over
      ##n_participants * n_items, written as a product of square roots only so
      ##that a billion-response table does not overflow the numerator.
      ##
      ##It is NOT the proportion of cells that are filled, and it is not bounded
      ##by 1. 768 of 6,720 core tables are above 1 (measured 2026-10-25), which
      ##is what a table with repeated measurements looks like: 700 of them carry
      ##an occasion column (wave, rater, trial_*, session, ...), 122 carry
      ##`date`, and the largest is hachenberger_2025_gonogo_main at 3,624.6 --
      ##a go/no-go task where each person-item is measured thousands of times.
      ##A value above 1 is therefore information about the design, never a
      ##defect, and nothing downstream may treat it as one. The proportion of
      ##distinct id-item cells filled is a different quantity, not computed
      ##here (ben-domingue/irw#3222, review R-21).
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
      ##Carry the live column list and the table's content hash back with the
      ##stats. Both are free here: `nms` is already in hand from the
      ##list_variables() call above, and $properties is populated by the
      ##list_tables() listing, so neither costs an API request.
      ##
      ##The column list matters because `variables` used to be written once,
      ##when a table first appeared, and never revisited -- the need_vars block
      ##at the bottom of this script only fills a row that is NA or empty. A
      ##table rebuilt with fewer columns therefore kept its ORIGINAL column
      ##list in the published catalog for ever. In October 2026 nineteen rows
      ##declared columns the data no longer had, and five of those removals had
      ##been removals of PERSONAL fields, so irw_meta was republishing the names
      ##of exactly the columns a correction had taken out. The refresh pass
      ##below now updates `variables` from this attribute, which makes the
      ##column list exactly as fresh as the seven numbers beside it.
      attr(testvec,"variables")<-paste(nms,collapse="| ")
      props<-tryCatch(tab$properties,error=function(e) NULL)
      attr(testvec,"hash")<-if (is.null(props$hash)) NA_character_ else as.character(props$hash)
      attr(testvec,"num_rows")<-if (is.null(props$numRows)) NA_real_ else as.numeric(props$numRows)
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

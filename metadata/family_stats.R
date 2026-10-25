##################################################################################
## family_stats.R -- the per-table statistics for the comps, nominal and simsyn
## catalogues, moved here verbatim so that the stage which writes a row and the
## refresher which revisits it compute the same numbers.
##
## WHY THIS FILE EXISTS
##
## 01_metadata.R (core) has had a rolling refresh pass since September 2026:
## every run re-fetches a slice of the rows it already has, so a table that was
## rebuilt gets its published counts corrected within a few weeks. 05_comps.R,
## 06_nominal.R and 07_simsyn.R have never had one. A row in those three
## catalogues is computed once, when the table first appears, and never
## revisited -- so a table replaced after that keeps its original numbers for
## ever, with nothing in the pipeline able to notice.
##
## That is not hypothetical. On 2026-10-24 the release gate (#3213) found
## `wilmer-mrmet-normative-data-set-2022_nom` publishing 343,876 responses
## against 343,276 real rows and 40 response categories against a true 4. There
## was no mechanism to fix it, so it was corrected by hand -- which is the
## argument for this file.
##
## The three functions below are the stages' own, moved without a line changed,
## and each stage now sources them. The arrangement is the one #3214 used for
## core: 01_metadata.R's statistics moved to table_stats.R, and
## refresh_rows.R sources that, so a refreshed row is byte-for-byte the row the
## next pipeline run would write. A refresher with its own arithmetic would make
## a value flip between runs, which is worse than a stale value because nothing
## distinguishes it from real movement in the data.
##
## Each family computes something different, and the differences are the point:
##   comps    n_responses from `winner`, plus n_actors, which needs a query
##            because the actors are spread over `agent_a` and `agent_b`.
##   nominal  the response column is `text`, not `resp`, and n_categories is
##            its distinct count. No density and no column list.
##   simsyn   the seven core statistics.
##
## Callers: 05_comps.R, 06_nominal.R, 07_simsyn.R, refresh_rows.R.
##################################################################################

##The datasets each family lives in, so the stages and the refresher cannot
##disagree about where a table is.
FAMILY_DATASETS<-list(comps="irw_competitions",
                      nom="irw_nominal",
                      simsyn="irw_simsyn")

##---- comps (05_comps.R) ----------------------------------------------------
count_actors_via_query<-function(tab) {
  ref<-tab$qualified_reference
  sql<-sprintf(paste("SELECT COUNT(DISTINCT agent) AS n FROM (",
                     "SELECT CAST(agent_a AS STRING) AS agent FROM `%s`",
                     "UNION ALL",
                     "SELECT CAST(agent_b AS STRING) AS agent FROM `%s` )"),
               ref, ref)
  res<-redivis$query(sql)$to_tibble()
  n<-as.numeric(res$n[1])
  if (length(n)!=1 || is.na(n)) stop("actor count query returned no value for ",ref)
  n
}

f_comps<-function(tab) {
    getvars<-function(tab) {
      variables <- tab$list_variables() 
      nms<-sapply(variables,function(x) x$get()$properties$name)
      stats<-lapply(variables,function(x) x$get_statistics() ) 
      ##
      names(stats)<-nms
      n_responses<-stats[["winner"]]$count
      ##
      n_actors<-count_actors_via_query(tab)
      testvec<-c(n_responses=n_responses,
                 n_actors=n_actors
                 )
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
      if (length(testvec)==2) try.counter<-100 else try.counter<-try.counter+1
  }
  return(testvec)
}

##---- nominal (06_nominal.R) ------------------------------------------------
f_nominal<-function(tab) {
    getvars<-function(tab) {
      variables <- tab$list_variables() 
      nms<-sapply(variables,function(x) x$get()$properties$name)
      stats<-lapply(variables,function(x) x$get_statistics() ) 
      ##
      names(stats)<-nms
      n_participants<-stats$id$numDistinct
      n_items<-stats$item$numDistinct
      n_responses<-stats$text$count
      responses_per_participant = n_responses / n_participants
      ##
      resp.index<-which(nms=="text")
      variable<-variables[[resp.index]]
      out<-variable$get_statistics()
      n_categories<-out$numDistinct
      ##
      testvec<-c(n_responses=n_responses,
                 n_participants=n_participants,
                 n_items=n_items,
                 responses_per_participant=responses_per_participant,
                 n_categories=n_categories
                 )
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
      if (length(testvec)==5) try.counter<-100 else try.counter<-try.counter+1
  }
  return(testvec)
}

##---- simsyn (07_simsyn.R) --------------------------------------------------
f_simsyn<-function(tab) {
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
      ##Responses per person-item cell, not the proportion of cells filled; see
      ##the comment on the same line in table_stats.R (#3222).
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

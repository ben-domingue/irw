## Retrying wrapper around gsheet::gsheet2tbl.
##
## The pipeline reads seven public Google Sheets. On 2026-09-04 a GitHub
## Actions run of the metadata pipeline died at stage 03 on one of them:
##
##   Failed to open '.../export?id=1v3toO6OPts...&gid=126134123':
##     The requested URL returned error: 400
##   Error: cannot open the connection
##
## after a four-minute stall -- and `set -e` in run_pipeline.sh turned that one
## refusal into a dead run, discarding the two and a half stages that had
## already succeeded.
##
## It was transient, and that was established rather than assumed: a probe
## fetched all seven sheets twice from a runner immediately afterwards and got
## HTTP 200 every time, the failing sheet included, byte-identical to a local
## fetch and in 0.4 seconds. Four other sheets had already fetched fine in the
## same failing run. Nothing is wrong with the sheets, their sharing, or the
## runner's route to them; Google simply refused one request.
##
## Unattended, that matters more than it used to. A human running the pipeline
## sees the error and runs it again. A weekly cron or workflow throws the run
## away and mails a failure, and the next attempt is a week later.
##
## This file deliberately defines a function called `gsheet2tbl`, masking the
## package's, so that existing call sites get retries without being edited --
## there are ten across seven scripts. Source it AFTER library(gsheet).
##
## It also reads EVERY column as character rather than letting readr guess.
##
## gsheet::gsheet2tbl hardcodes its own read_csv call and accepts no col_types,
## so guessing was not overridable at the call sites. readr infers a column's
## type from the first rows only, and a column that is blank there is guessed
## `logical` -- after which every real value further down fails to parse and is
## silently replaced with NA. The whole column arrives empty, with nothing in
## the pipeline output to say so.
##
## That is not hypothetical: the dictionary sheet's second `Custom License`
## column is blank until row 801, so all four tables carrying custom licence
## terms (ml_harper_2015, roar_gijbels2024, nit_must_2014 and
## bicb-j_ishiguro_2025) parsed as NA, and biblio.csv shipped
## `Custom_License_Terms` populated on 0 rows in pipeline run 34152997615 --
## the column #1732 exists to deliver. A `curl` of the same sheet showed all
## four present, which is what made this a parse bug rather than a sheet one.
##
## Every dictionary column is text as far as this pipeline is concerned, so
## forcing character costs nothing and closes the whole class: any sparse
## column in any of the seven sheets was one blank prefix away from the same
## silent emptying.
gsheet2tbl <- function(url, ..., .attempts = 4L, .waits = c(5, 15, 45)) {
  read_all_character <- function(url, ...) {
    readr::read_csv(I(gsheet::gsheet2text(url, format = "csv")),
                    col_types = readr::cols(.default = readr::col_character()),
                    ...)
  }
  for (i in seq_len(.attempts)) {
    result <- try(suppressMessages(read_all_character(url, ...)), silent = TRUE)
    if (!inherits(result, "try-error")) {
      if (i > 1L) message("  gsheet: succeeded on attempt ", i)
      return(result)
    }
    if (i < .attempts) {
      wait <- .waits[min(i, length(.waits))]
      message("  gsheet: attempt ", i, " of ", .attempts, " failed, retrying in ",
              wait, "s -- ", trimws(as.character(result)))
      Sys.sleep(wait)
    } else {
      ## Out of attempts: fail exactly as the package would, so the caller's
      ## error handling and the pipeline's logs are unchanged.
      stop("gsheet2tbl failed after ", .attempts, " attempts for ", url, ":\n",
           as.character(result), call. = FALSE)
    }
  }
}

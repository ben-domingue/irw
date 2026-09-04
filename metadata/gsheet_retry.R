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
gsheet2tbl <- function(url, ..., .attempts = 4L, .waits = c(5, 15, 45)) {
  for (i in seq_len(.attempts)) {
    result <- try(gsheet::gsheet2tbl(url, ...), silent = TRUE)
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

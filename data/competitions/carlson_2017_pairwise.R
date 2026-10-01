##Crowdsourced pairwise comparisons of texts (MTurk, 2015-2016), from
##Carlson, D., & Montgomery, J. M. (2017). A pairwise comparison framework for fast,
##flexible, and reliable human coding of political texts. American Political Science
##Review, 111(4), 835-843. https://doi.org/10.1017/S0003055417000302
##Replication data: Harvard Dataverse doi:10.7910/DVN/0ZRGEE, CC0 1.0 (Dataverse API,
##version 1), one file SentimentItReplication.tar. Issues #1173 / #1234.
##Run from a directory holding the extracted tar (APSRReplication/...). Only the batch
##returns are read; the Stan fits and the WiscAds .dta are not needed.
##
##Each study is one table. In every one a coder saw two texts and picked one:
##  movie_reviews  "choose the text ... from the most positive review" (497 snippets)
##  movie50        the same question on 50 review snippets (experiment 2 returns)
##  treebank       Stanford Sentiment Treebank snippets, positivity; experiment 1 had
##                 no training, experiment 2 required a certification (column experiment)
##  wiscads        2008 U.S. Senate campaign ads: "most negative towards the candidate(s)
##                 mentioned, or least positive about" them
##  human_rights   State Department report passages: "more significant levels of torture"
##  immigration    open-ended survey statements: "more fear, anxiety, or worry about the
##                 negative impact of immigrants or immigration on America"
##
##The texts are the agents. A comparison is two source rows (document_id, result); the
##first row is agent_a, the second agent_b, and winner is whichever has result 1.
##score_a/score_b carry that 0/1. homefield is blank (no side has an advantage).
##rater is the MTurk worker re-keyed to an integer, with one map across all six tables
##so a coder who worked on several studies keeps one number; raw worker ids are not
##published. date = completed_at in Unix seconds. comparison_id and batch_id are kept.
##
##Cleaning: exact duplicate rows are dropped (148 in wiscads, 950 in human_rights);
##then any comparison that is not exactly two rows with one winner is dropped and
##counted. In human_rights these are comparisons whose rows the README describes as
##"overlapped across a few documents"; they cannot be read as a single pair.

dir <- "APSRReplication/DataFiles/"
rd <- function(f) { e <- new.env(); load(paste0(dir, f), e); get(ls(e)[1], e) }
src <- list(
  movie_reviews = read.csv(paste0(dir, "Movie Reviews/allOutput.csv")),
  movie50 = read.csv(paste0(dir, "50Reviews/CombinedOutputExperiment2.csv")),
  treebank = rbind(cbind(read.csv(paste0(dir, "Treebank/CombinedOutput.csv")), experiment = 1),
                   cbind(read.csv(paste0(dir, "Treebank/CombinedOutputExperiment2.csv")), experiment = 2)),
  wiscads = rd("WiscAds2008/all_batches.Rdata"),
  human_rights = rd("HR data/all_batches_with_dups.Rdata"),
  immigration = rd("ImmigrationSurvey/PooledOutputWNewSys.Rdata"))
cols <- c("batch_id", "comparison_id", "document_id", "result", "worker_id", "completed_at")
## The .Rdata returns hold worker_id and completed_at as factors; unlist() would turn
## factors into their integer codes, so everything is made character first.
src <- lapply(src, function(x) {
  x <- x[, c(cols, intersect("experiment", names(x)))]
  x$worker_id <- as.character(x$worker_id)
  x$completed_at <- as.character(x$completed_at)
  x
})

workers <- sort(unique(unlist(lapply(src, function(x) x$worker_id))))

for (nm in names(src)) {
  x <- src[[nm]]
  n0 <- nrow(x)
  x <- x[!duplicated(x), ]
  ndup <- n0 - nrow(x)
  k <- table(x$comparison_id)
  s <- tapply(x$result, x$comparison_id, sum)
  good <- names(k)[k == 2 & s[names(k)] == 1]
  nbad <- length(k) - length(good)
  x <- x[as.character(x$comparison_id) %in% good, ]
  x <- x[order(x$comparison_id), ]
  a <- x[duplicated(x$comparison_id, fromLast = TRUE), ]  # first row of each pair
  b <- x[duplicated(x$comparison_id), ]                   # second row
  stopifnot(identical(a$comparison_id, b$comparison_id), all(a$worker_id == b$worker_id))
  df <- data.frame(agent_a = a$document_id, agent_b = b$document_id,
                   date = as.numeric(as.POSIXct(a$completed_at, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")),
                   score_a = a$result, score_b = b$result, homefield = "",
                   winner = ifelse(a$result == 1, "agent_a", "agent_b"),
                   rater = match(a$worker_id, workers),
                   comparison_id = a$comparison_id, batch_id = a$batch_id)
  if ("experiment" %in% names(a)) df$experiment <- a$experiment
  stopifnot(!anyNA(df$date), all(df$agent_a != df$agent_b))
  out <- paste0("carlson_2017_", nm, ".csv")
  write.csv(df, out, row.names = FALSE, na = "")
  cat(out, nrow(df), "comparisons,", length(unique(c(df$agent_a, df$agent_b))), "texts,",
      length(unique(df$rater)), "raters; dropped", ndup, "duplicate rows and", nbad,
      "comparisons not readable as one pair\n")
}

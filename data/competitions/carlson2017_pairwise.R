## Carlson & Montgomery (2017), "A Pairwise Comparison Framework for Fast, Flexible,
## and Reliable Human Coding of Political Texts", APSR 111(4).
## Replication data: https://doi.org/10.7910/DVN/0ZRGEE (SentimentItReplication.tar)
## Licence: CC0 1.0 (Harvard Dataverse API, checked 2026-09-30). Refs #1173, #1234.
## (github.com/haukelicht/scalar_measurement has no licence and was not used.)
##
## MTurk workers saw two documents and picked one. Documents are the agents; the picked
## document wins. One table per document set:
##   wiscads         2008 congressional ads; "most negative towards the candidate(s)"
##   hrtorture       State Dept human-rights report sentences; "more significant levels of torture"
##   immigration     open-ended survey answers; "more fear, anxiety, or worry about ... immigration"
##   moviereviews    full movie reviews; "comes from the most positive review"
##   treebank        Stanford Sentiment Treebank snippets; experiment 1 untrained, 2 certified
##                   workers. The question is not recorded in the replication files.
##   reviews50       50 movie reviews (apiTest.csv), experiment 2 of the SI; "most positive"
##   dennisschwartz50 50 Dennis Schwartz review snippets (DS50.2.csv); "most positive"
##
## Choices:
## - agent_a/agent_b keep the source's row order within a comparison (it is not winner-first).
## - rater: MTurk worker ids are recoded to integers. The same worker gets the same number
##   in every table, so raters can be linked across studies.
## - date: completed_at, in Unix seconds.
## - wiscads: 74 comparisons appear twice as exact duplicate rows; the duplicates are dropped.
## - hrtorture: the source file ("all_batches_with_dups") expands each comparison over
##   every document id sharing its text (e.g. 27 ids for one boilerplate sentence). Ids
##   with identical text are collapsed to the smallest id. After that, each of the 16,046
##   comparisons has exactly one winner and one loser.
## - No scores and no homefield (as in friedman2019_risks.R).

cache <- path.expand("~/.cache/irw-comps/carlson")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
tarf <- file.path(cache, "SentimentItReplication.tar")
if (!file.exists(tarf))
    download.file("https://dataverse.harvard.edu/api/access/datafile/3030981", tarf, mode = "wb")
dd <- file.path(cache, "APSRReplication", "DataFiles")
if (!dir.exists(dd))
    untar(tarf, exdir = cache, extras = "--exclude='*Fit*' --exclude='*fit*' --exclude='*.dta'")

ld <- function(f) {
    f <- file.path(dd, f)
    if (grepl("Rdata$", f)) { e <- new.env(); load(f, e); x <- get(ls(e)[1], e) }
    else x <- read.csv(f, stringsAsFactors = FALSE)
    for (v in names(x)) if (is.factor(x[[v]])) x[[v]] <- as.character(x[[v]])
    x[, c("comparison_id", "document_id", "result", "worker_id", "completed_at")]
}

src <- list(
    wiscads          = ld("WiscAds2008/all_batches.Rdata"),
    hrtorture        = ld("HR data/all_batches_with_dups.Rdata"),
    immigration      = ld("ImmigrationSurvey/PooledOutputWNewSys.Rdata"),
    moviereviews     = ld("Movie Reviews/allOutput.csv"),
    treebank         = rbind(cbind(ld("Treebank/CombinedOutput.csv"), experiment = 1),
                             cbind(ld("Treebank/CombinedOutputExperiment2.csv"), experiment = 2)),
    reviews50        = ld("50Reviews/CombinedOutputExperiment2.csv"),
    dennisschwartz50 = ld("50Reviews/DS50.2.csv")
)

## hrtorture: collapse document ids that share a text
e <- new.env(); load(file.path(dd, "HR data", "docs.Rdata"), e)
txt <- trimws(as.character(e$docs$V3))
canon <- tapply(e$docs$ids, txt, min)[txt]
src$hrtorture$document_id <- canon[match(src$hrtorture$document_id, e$docs$ids)]

workers <- sort(unique(unlist(lapply(src, `[[`, "worker_id"))))

for (nm in names(src)) {
    x <- src[[nm]]
    x <- x[!duplicated(x[, setdiff(names(x), "completed_at")]), ]
    x <- split(x, x$comparison_id)
    stopifnot(all(sapply(x, function(d) nrow(d) == 2 && sum(d$result) == 1)))
    df <- data.frame(
        agent_a = sapply(x, function(d) d$document_id[1]),
        agent_b = sapply(x, function(d) d$document_id[2]),
        date = sapply(x, function(d) as.numeric(as.POSIXct(d$completed_at[1], format = "%Y-%m-%d %H:%M:%S", tz = "UTC"))),
        winner = sapply(x, function(d) if (d$result[1] == 1) "agent_a" else "agent_b"),
        rater = sapply(x, function(d) match(d$worker_id[1], workers))
    )
    if ("experiment" %in% names(x[[1]])) df$experiment <- sapply(x, function(d) d$experiment[1])
    stopifnot(!anyNA(df), all(df$agent_a != df$agent_b))
    df <- df[order(df$date), ]
    write.csv(df, paste0("carlson2017_", nm, ".csv"), row.names = FALSE)
}

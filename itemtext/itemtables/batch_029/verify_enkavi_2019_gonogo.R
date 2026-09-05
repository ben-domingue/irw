# verify_enkavi_2019_gonogo.R
#
# This table is BLOCKED and ships no __items.csv, so there is no item_text<->item
# mapping in the corpus to verify. What this script re-runs is the BASIS of the
# block, which is the determinate finding a triager would otherwise rebuild by hand:
#
#   (1) the four IRW `item` codes are STIMULUS CONDITIONS, not verbal items. The
#       expfactory `go_nogo` task presents a single coloured square per trial and
#       the raw `stimulus` column is literally '<div class = centerbox><div id =
#       stimN></div></div>' -- zero characters of item wording, for every trial of
#       every participant, in both waves.
#   (2) the item construction is nonetheless fully determinate and reproducible:
#       re-running data/enkavi_2019_conflict_tasks.py's _prep_gonogo key
#       (condition + stim_id parsed out of `stimulus`) over the two raw SRO files
#       reproduces the live per-item row counts EXACTLY. So the block is "there is
#       no wording to transcribe", not "the mapping could not be established".
#   (3) which colour each id is, is recoverable (style.css: #stim1 background
#       orange, #stim2 background DodgerBlue) and the go/no-go role is
#       counterbalanced across participants (experiment.js line 104 shuffles the
#       [colour, id] pairs). Any `item_text` would therefore be an IRW-authored
#       description of a coloured square, which the standard forbids.
#
# It performs NO Redivis export: the live per-item counts come from
# irw::irw_table_sets(), a server-side aggregate query.
#
# VERDICT: PASS means "the block still reproduces" -- the stimuli still carry no
# text and the item key still reproduces the live counts. VERDICT: FAIL means
# something moved and the table should be re-examined.

RAW <- "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data"
EXP <- "https://raw.githubusercontent.com/expfactory/expfactory-experiments/master/go_nogo"
CACHE <- file.path("..", "..", ".cache", "enkavi_2019_gonogo")
if (!dir.exists(CACHE)) CACHE <- tempdir()

get <- function(url, dest) {
    if (!file.exists(dest) || file.size(dest) < 100)
        utils::download.file(url, dest, quiet = TRUE, mode = "wb")
    dest
}

ok <- TRUE

## ---- (1) the stimuli carry no text -------------------------------------------
samples <- c("1" = "Complete_02-16-2019", "2" = "Retest_02-16-2019")
counts <- integer(0)
stimset <- character(0)
for (w in names(samples)) {
    f <- get(sprintf("%s/%s/Individual_Measures/go_nogo.csv.gz", RAW, samples[[w]]),
             file.path(CACHE, sprintf("go_nogo_%s.csv.gz", samples[[w]])))
    d <- read.csv(gzfile(f), stringsAsFactors = FALSE)
    t <- d[d$exp_stage == "test", ]
    stimset <- union(stimset, unique(t$stimulus))
    r <- suppressWarnings(as.numeric(as.logical(t$correct)))
    keep <- !is.na(r) & r %in% c(0, 1) & !is.na(t$worker_id) & nzchar(t$worker_id)
    t <- t[keep, ]
    stim_id <- sub(".*id\\s*=\\s*(stim[0-9]).*", "\\1", t$stimulus)
    item <- paste0(t$condition, "_", stim_id)
    tb <- table(item)
    for (nm in names(tb)) counts[nm] <- (if (is.na(counts[nm])) 0L else counts[nm]) + as.integer(tb[[nm]])
}
cat("distinct raw `stimulus` strings across both waves:\n")
for (s in sort(stimset)) cat("   ", s, "\n")
# strip all HTML tags: whatever is left is the text a participant could read
txt <- gsub("<[^>]*>", "", stimset)
txt <- gsub("\\s+", "", txt)
cat(sprintf("characters of visible text after stripping HTML tags: %d (expected 0)\n",
            sum(nchar(txt))))
if (sum(nchar(txt)) != 0L) { cat("  ** stimuli now contain text -- re-queue this table **\n"); ok <- FALSE }
if (!all(grepl("id\\s*=\\s*stim[12]", stimset)) || length(stimset) < 2) {
    cat("  ** stimulus grammar changed **\n"); ok <- FALSE
}

## ---- (2) the item key reproduces the live per-item counts --------------------
expected <- c(go_stim1 = 107415L, go_stim2 = 104580L, nogo_stim1 = 11620L, nogo_stim2 = 11935L)
live <- NULL
if (requireNamespace("irw", quietly = TRUE)) {
    s <- try(irw::irw_table_sets("enkavi_2019_gonogo", source = "core", per_item = TRUE), silent = TRUE)
    if (!inherits(s, "try-error") && !is.null(s$per_item)) {
        pi <- as.data.frame(s$per_item)
        live <- setNames(as.integer(pi$n), pi$item)
    }
}
if (is.null(live)) {
    cat("\nirw::irw_table_sets() unavailable -- falling back to the counts recorded at extraction\n")
    live <- expected
}
cat("\nper-item n: rebuilt from the raw SRO files vs live IRW table\n")
cat(sprintf("%-12s %10s %10s %8s\n", "item", "rebuilt", "live", "diff"))
for (nm in sort(union(names(counts), names(live)))) {
    a <- if (is.na(counts[nm])) 0L else counts[nm]
    b <- if (is.null(live[[nm]]) || is.na(live[nm])) 0L else live[nm]
    cat(sprintf("%-12s %10d %10d %8d\n", nm, a, b, a - b))
    if (a != b) ok <- FALSE
}
if (!setequal(names(counts), names(live))) {
    cat("  ** item sets differ **\n"); ok <- FALSE
}

## ---- (3) colour binding fixed, go/no-go role counterbalanced -----------------
css <- paste(readLines(get(paste0(EXP, "/style.css"), file.path(CACHE, "style.css")),
                       warn = FALSE), collapse = " ")
js  <- paste(readLines(get(paste0(EXP, "/experiment.js"), file.path(CACHE, "experiment.js")),
                       warn = FALSE), collapse = " ")
c1 <- grepl("#stim1\\s*\\{[^}]*background:\\s*orange", css)
c2 <- grepl("#stim2\\s*\\{[^}]*background:\\s*DodgerBlue", css)
shuf <- grepl('shuffle\\(\\[\\["orange", *"stim1"\\], *\\["blue", *"stim2"\\]\\]\\)', js)
cat(sprintf("\nstyle.css  #stim1 background: orange      -> %s\n", c1))
cat(sprintf("style.css  #stim2 background: DodgerBlue  -> %s\n", c2))
cat(sprintf("experiment.js shuffles the [colour,id] pairs (go/no-go role is\n"))
cat(sprintf("  counterbalanced across participants, colour<->id binding fixed) -> %s\n", shuf))
if (!(c1 && c2 && shuf)) { cat("  ** task source changed -- re-read it **\n"); ok <- FALSE }

## ---- conclusion ---------------------------------------------------------------
cat("\nConclusion: the item codes are stimulus conditions (colour identity x a\n",
    "counterbalanced go/no-go role) for a task whose stimuli are wordless coloured\n",
    "squares, and `resp` is trial accuracy rather than a chosen response option.\n",
    "Neither join axis has any literal text to transcribe; only the whole-task\n",
    "instructions exist, and those are participant-specific in their operative\n",
    "sentence. The block is determinate, not an access failure.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

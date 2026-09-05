# verify_enkavi_2019_gonogo.R
#
# What is shipped for this table, and therefore what has to be verified:
#   - item_text is BLANK for all 4 items, by the picture-stimulus ruling
#     (itemtext_standard.md, 2026-09-05): the go/no-go stimulus is a wordless
#     coloured square, so there is no wording to map. Nothing to verify there.
#   - correct_response is NOT blank and carries a real per-item claim:
#     go_stim1/go_stim2 -> "spacebar", nogo_stim1/nogo_stim2 -> "no response".
#     THAT is the mapping this script verifies.
#   - option_text is the accuracy label on resp (0=Incorrect, 1=Correct).
#
# The claim would break if the go/no-go roles were swapped across item codes.
# Two independent checks, neither of which exports the IRW table:
#
#  (1) LABEL TIE. The raw SRO go_nogo files carry their own `correct_response`
#      column (the jsPsych key code: 32 = spacebar, -1 = withhold). Cross-tabbed
#      against the rebuilt IRW item code (condition + stim_id, exactly what
#      data/enkavi_2019_conflict_tasks.py::_prep_gonogo builds), it must be 100%
#      32 for the go_* codes and 100% -1 for the nogo_* codes.
#  (2) BEHAVIOUR. Independently of any label: go trials should be near-ceiling
#      accurate and dominated by an actual spacebar press; nogo trials should be
#      markedly less accurate (commission errors) and dominated by withholding.
#      A role swap inverts this.
#
#  (3) The item CODES themselves are pinned by reproducing the live per-item n
#      from the raw files via irw::irw_table_sets() -- a server-side aggregate,
#      no export.
#
# What this does NOT establish: it cannot distinguish go_stim1 from go_stim2 (nor
# nogo_stim1 from nogo_stim2), because every shipped field is identical for the
# two members of each pair -- item_text is blank and correct_response is the same.
# There is consequently nothing that could be swapped between them. The colour
# each stim id denotes (style.css: #stim1 orange, #stim2 DodgerBlue) is checked
# below for the record but is not shipped in any text field.

CACHE <- file.path("..", "..", ".cache", "enkavi_2019_gonogo")
if (!dir.exists(CACHE)) CACHE <- tempdir()
RAW <- "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data"
EXP <- "https://raw.githubusercontent.com/expfactory/expfactory-experiments/master/go_nogo"

get <- function(url, dest) {
    if (!file.exists(dest) || file.size(dest) < 100)
        utils::download.file(url, dest, quiet = TRUE, mode = "wb")
    dest
}

ok <- TRUE
SHIPPED <- c(go_stim1 = "spacebar", go_stim2 = "spacebar",
             nogo_stim1 = "no response", nogo_stim2 = "no response")

samples <- c("Complete_02-16-2019", "Retest_02-16-2019")
d <- do.call(rbind, lapply(samples, function(s) {
    f <- get(sprintf("%s/%s/Individual_Measures/go_nogo.csv.gz", RAW, s),
             file.path(CACHE, sprintf("go_nogo_%s.csv.gz", s)))
    x <- read.csv(gzfile(f), stringsAsFactors = FALSE)
    x[x$exp_stage == "test", c("condition", "stimulus", "correct_response",
                               "key_press", "correct")]
}))
d$stim_id <- sub(".*id\\s*=\\s*(stim[0-9]).*", "\\1", d$stimulus)
d$item <- paste0(d$condition, "_", d$stim_id)

## ---- (1) label tie: raw correct_response keycode by item ---------------------
cat("(1) raw source `correct_response` keycode (32 = spacebar, -1 = withhold)\n")
tb <- table(d$item, d$correct_response)
print(tb)
cat(sprintf("\n%-12s %-14s %-14s %s\n", "item", "shipped", "implied by raw", "share"))
for (it in sort(unique(d$item))) {
    kc <- names(which.max(tb[it, ]))
    share <- max(tb[it, ]) / sum(tb[it, ])
    implied <- if (kc == "32") "spacebar" else if (kc == "-1") "no response" else paste("keycode", kc)
    cat(sprintf("%-12s %-14s %-14s %.4f\n", it, SHIPPED[[it]], implied, share))
    if (implied != SHIPPED[[it]] || share != 1) ok <- FALSE
}

## ---- (2) behaviour: accuracy and actual key press ----------------------------
cat("\n(2) behaviour by item (independent of the label above)\n")
cat(sprintf("%-12s %10s %14s\n", "item", "mean acc", "% spacebar"))
for (it in sort(unique(d$item))) {
    s <- d[d$item == it, ]
    acc <- mean(as.numeric(as.logical(s$correct)), na.rm = TRUE)
    pk <- mean(s$key_press == 32, na.rm = TRUE)
    cat(sprintf("%-12s %10.4f %14.4f\n", it, acc, pk))
    if (grepl("^go_", it) && !(acc > 0.95 && pk > 0.95)) ok <- FALSE
    if (grepl("^nogo_", it) && !(acc < 0.95 && pk < 0.5)) ok <- FALSE
}
cat("go_* items are near-ceiling accurate and >95% spacebar; nogo_* items are\n",
    "markedly less accurate and <50% spacebar. A swapped role inverts this.\n", sep = "")

## ---- (3) item codes pinned by exact per-item n reproduction ------------------
counts <- table(d$item[!is.na(suppressWarnings(as.logical(d$correct)))])
expected <- c(go_stim1 = 107415L, go_stim2 = 104580L, nogo_stim1 = 11620L, nogo_stim2 = 11935L)
live <- NULL
if (requireNamespace("irw", quietly = TRUE)) {
    s <- try(irw::irw_table_sets("enkavi_2019_gonogo", source = "core", per_item = TRUE),
             silent = TRUE)
    if (!inherits(s, "try-error") && !is.null(s$per_item)) {
        pi <- as.data.frame(s$per_item)
        live <- setNames(as.integer(pi$n), pi$item)
    }
}
if (is.null(live)) { cat("\nirw_table_sets() unavailable -- using counts recorded at extraction\n"); live <- expected }
cat("\n(3) per-item n: rebuilt from raw SRO files vs live IRW\n")
cat(sprintf("%-12s %10s %10s %8s\n", "item", "rebuilt", "live", "diff"))
for (nm in sort(union(names(counts), names(live)))) {
    a <- as.integer(counts[[nm]]); b <- as.integer(live[[nm]])
    cat(sprintf("%-12s %10d %10d %8d\n", nm, a, b, a - b))
    if (a != b) ok <- FALSE
}

## ---- (4) colour binding, for the record --------------------------------------
css <- paste(readLines(get(paste0(EXP, "/style.css"), file.path(CACHE, "style.css")), warn = FALSE), collapse = " ")
js  <- paste(readLines(get(paste0(EXP, "/experiment.js"), file.path(CACHE, "experiment.js")), warn = FALSE), collapse = " ")
c1 <- grepl("#stim1\\s*\\{[^}]*background:\\s*orange", css)
c2 <- grepl("#stim2\\s*\\{[^}]*background:\\s*DodgerBlue", css)
shuf <- grepl('shuffle\\(\\[\\["orange", *"stim1"\\], *\\["blue", *"stim2"\\]\\]\\)', js)
cat(sprintf("\n(4) style.css #stim1=orange: %s | #stim2=DodgerBlue: %s | experiment.js shuffles the [colour,id] PAIRS (only the go/no-go role is counterbalanced): %s\n",
            c1, c2, shuf))
cat("    Not shipped in any text field; recorded because it is what a later pass\n",
    "    would need if the ruling on stimulus descriptions ever changes.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

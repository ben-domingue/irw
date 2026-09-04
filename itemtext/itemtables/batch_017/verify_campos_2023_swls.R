# verify_campos_2023_swls.R -- Step 5b mapping check for campos_2023_swls.
#
# CLAIM UNDER TEST (PARTIAL, not VERIFIED):
#   (a) SWLS01..SWLS05 are the deposit's Satisfaction-With-Life block (S1 File
#       "Scores" sheet: columns AM-AQ = "Responses to Satisfaction with Life Scale
#       items", 1=Strongly disagree .. 7=Strongly agree), separate from PIDAQ
#       (cols H-AE, 0-4) and OES (cols AF-AL, 0-10);
#   (b) SWLS05 carries canonical SWLS item 5 ("If I could live my life over, I
#       would change almost nothing") -- the marker item, which in every SWLS
#       validation is the least endorsed, most dispersed and weakest-loading item.
#   NOT under test, and NOT established anywhere: the assignment of items 1-4 to
#   SWLS01..SWLS04. That rests on the deposit's own numbering alone.
#
# Data: the study's S1 File (PLOS 10.1371/journal.pone.0287235.s004), which is the
# file data/campos_2023_aesthetic_dental.py melts into the live table. Live item and
# resp SETS + per-item n come from irw::irw_table_sets() (server-side aggregate) --
# irw_fetch() is deliberately NOT called (200GB/30-day corpus export cap).

suppressMessages({library(readxl); library(lavaan); library(psych)})

TABLE <- "campos_2023_swls"
COLS  <- sprintf("SWLS%02d", 1:5)
URL   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0287235.s004"
CACHE <- file.path(".cache", TABLE, "s004.xlsx")

# Published values, Campos et al. (2023) PLOS ONE, S1 Table (SWLS rows).
PUB_LAMBDA_MIN <- c(Finland = 0.67, Brazil = 0.70)
PUB_LAMBDA_MAX <- c(Finland = 0.92, Brazil = 0.92)
PUB_ALPHA      <- c(Finland = 0.92, Brazil = 0.91)
PUB_N          <- c(Finland = 3614, Brazil = 3979)

ok <- TRUE

## ---- (a) block signature, from the live table ------------------------------
cat("=== (a) block signature vs the deposit codebook ===\n")
ts <- irw::irw_table_sets(TABLE)
live_items <- sort(as.character(ts$item))
live_resp  <- sort(as.numeric(ts$resp))
cat("live items:", paste(live_items, collapse = " "), "\n")
cat("live resp levels:", paste(live_resp, collapse = " "), "\n")
cat("codebook says SWLS = 5 items on 1..7; PIDAQ = 24 items on 0..4; OES = 7 items on 0..10\n")
blk <- identical(live_items, COLS) && identical(live_resp, as.numeric(1:7))
cat("block signature matches SWLS and not PIDAQ/OES:", blk, "\n\n")
ok <- ok && blk

## ---- (b) marker item -------------------------------------------------------
if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    download.file(URL, CACHE, mode = "wb", quiet = TRUE)
}
d <- as.data.frame(read_excel(CACHE, sheet = "DB"))

cat("=== (b) marker item: is SWLS05 the weakest indicator in BOTH samples? ===\n")
cat(sprintf("%-8s %8s %6s %6s %7s %8s\n", "sample", "item", "mean", "sd", "floor%", "lambda"))
for (i in 1:2) {
    lab <- c("Finland", "Brazil")[i]
    s <- d[d$country == i, COLS]; s <- s[complete.cases(s), ]
    stopifnot(nrow(s) == PUB_N[[lab]])
    m  <- sapply(s, mean); sdv <- sapply(s, sd)
    fl <- sapply(s, function(x) 100 * mean(x == 1))
    fit <- cfa(paste("f =~", paste(COLS, collapse = " + ")), data = s,
               ordered = COLS, estimator = "WLSMV")
    l <- standardizedSolution(fit); l <- setNames(l$est.std[l$op == "=~"], l$rhs[l$op == "=~"])
    a <- psych::alpha(psych::polychoric(s)$rho)$total$raw_alpha
    for (cc in COLS)
        cat(sprintf("%-8s %8s %6.2f %6.2f %7.2f %8.2f\n", lab, cc, m[cc], sdv[cc], fl[cc], l[cc]))
    cat(sprintf("  published (S1 Table): n=%d, lambda %.2f-%.2f, ordinal alpha %.2f | observed: n=%d, lambda %.2f-%.2f, alpha %.2f\n",
                PUB_N[[lab]], PUB_LAMBDA_MIN[[lab]], PUB_LAMBDA_MAX[[lab]], PUB_ALPHA[[lab]],
                nrow(s), min(l), max(l), a))
    hit <- names(which.min(m)) == "SWLS05" && names(which.max(sdv)) == "SWLS05" &&
           names(which.max(fl)) == "SWLS05" && names(which.min(l)) == "SWLS05" &&
           abs(min(l) - PUB_LAMBDA_MIN[[lab]]) <= 0.02 && abs(a - PUB_ALPHA[[lab]]) <= 0.01
    cat("  SWLS05 is min-mean, max-sd, max-floor AND min-lambda, and that min reproduces the published lambda: ",
        hit, "\n\n", sep = "")
    ok <- ok && hit
}

cat("What this does NOT establish: nothing here separates SWLS01, SWLS02, SWLS03 and\n",
    "SWLS04 from one another. Their means (4.94/5.16/5.19/5.33 pooled) are close, they\n",
    "share one 1-7 scale, the SWLS is unidimensional and has no reverse-worded items, and\n",
    "neither the paper nor the deposit prints per-item statistics or item wording. Those\n",
    "four assignments rest on the deposit's own SWLSnn numbering following the published\n",
    "order of Diener et al. (1985). Status is PARTIAL for that reason.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

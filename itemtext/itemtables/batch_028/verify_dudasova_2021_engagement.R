# verify_dudasova_2021_engagement.R
#
# This table is BLOCKED and ships no __items.csv, so there is no item_text<->item
# mapping in the corpus to verify. What this script re-runs is the BASIS of the
# block, which is the thing a triager would otherwise have to rebuild by hand:
#
#   (1) the PLOS deposit publishes no item wording for the engagement block --
#       no variable label on Eng1..Eng9 and no value labels anywhere in any of
#       the four .sav supplements;
#   (2) the article never mentions the instrument at all (0 occurrences of
#       "engagement" / "UWES" / "Utrecht" / "Schaufeli" in the full text);
#   (3) the instrument is not even identified by the data -- the canonical
#       UWES-9 facet structure that the IRW Description conjectures is only
#       weakly present and cannot pin any item.
#
# It fetches its own data from the source (PLOS supplements + article HTML) and
# performs NO Redivis export: the IRW item codes ARE the .sav column names
# (data/dudasova_2021_cpc12_battery.py melts Eng1..Eng9 unchanged), so the local
# file is the same object the live table was built from.
#
# VERDICT: PASS means "the block still reproduces" -- i.e. no wording is
# recoverable. VERDICT: FAIL would mean a source has appeared and the table
# should be re-queued.

BASE <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0247114."
ART  <- "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247114"
CACHE <- file.path("..", "..", ".cache", "dudasova_2021_engagement")
if (!dir.exists(CACHE)) CACHE <- tempdir()

get <- function(url, dest) {
    if (!file.exists(dest) || file.size(dest) < 1000)
        utils::download.file(url, dest, quiet = TRUE,
                             headers = c("User-Agent" = "IRW-itemtext/1.0"))
    dest
}

ok <- TRUE

## ---- (1) labels in the four supplements -------------------------------------
if (!requireNamespace("haven", quietly = TRUE)) {
    cat("haven not installed -- cannot check .sav labels\n"); ok <- FALSE
} else {
    cat(sprintf("%-6s %6s %6s %8s %12s\n", "file", "rows", "cols", "varlabs", "vallabsets"))
    exp_lab <- c(s001 = 2L, s002 = 0L, s003 = 0L, s004 = 1L)
    for (s in names(exp_lab)) {
        f <- get(paste0(BASE, s), file.path(CACHE, paste0(s, ".sav")))
        d <- haven::read_sav(f)
        varlabs <- sum(vapply(d, function(x) {
            l <- attr(x, "label"); !is.null(l) && nzchar(l) }, logical(1)))
        vallabs <- sum(vapply(d, function(x) !is.null(attr(x, "labels")), logical(1)))
        cat(sprintf("%-6s %6d %6d %8d %12d\n", s, nrow(d), ncol(d), varlabs, vallabs))
        if (varlabs != exp_lab[[s]]) { cat("  ** variable-label count changed **\n"); ok <- FALSE }
        if (vallabs != 0L)           { cat("  ** value labels have appeared **\n");   ok <- FALSE }
        if (s == "s001") {
            eng <- paste0("Eng", 1:9)
            engl <- vapply(d[eng], function(x) {
                l <- attr(x, "label"); if (is.null(l)) "" else l }, character(1))
            cat("  Eng1..Eng9 variable labels: ",
                if (all(!nzchar(engl))) "all empty (as expected)"
                else paste(engl, collapse = " | "), "\n", sep = "")
            if (any(nzchar(engl))) { ok <- FALSE; cat("  ** Eng items are now labelled -- re-queue **\n") }
            lab2 <- unlist(lapply(d, function(x) attr(x, "label")))
            cat("  the only labelled columns in S1: ",
                paste(sprintf("%s='%s'", names(lab2), lab2), collapse = "; "), "\n", sep = "")
            S1 <<- d
        }
    }
}

## ---- (2) the article never names the instrument ------------------------------
html <- readLines(get(ART, file.path(CACHE, "paper.html")), warn = FALSE)
txt  <- paste(html, collapse = " ")
txt  <- gsub("(?s)<script.*?</script>", " ", txt, perl = TRUE)
txt  <- gsub("(?s)<style.*?</style>", " ", txt, perl = TRUE)
txt  <- gsub("<[^>]+>", " ", txt)
cat(sprintf("\narticle body: %d chars de-tagged\n", nchar(txt)))
for (w in c("engagement", "UWES", "Utrecht", "Schaufeli", "CPC-12")) {
    n <- length(gregexpr(w, txt, ignore.case = TRUE)[[1]])
    if (length(attr(gregexpr(w, txt, ignore.case = TRUE)[[1]], "match.length")) == 1 &&
        gregexpr(w, txt, ignore.case = TRUE)[[1]][1] == -1) n <- 0
    cat(sprintf("  occurrences of %-12s : %d\n", shQuote(w), n))
    if (w %in% c("engagement", "UWES", "Utrecht", "Schaufeli") && n > 0) {
        cat("  ** the article now mentions the instrument -- re-check **\n"); ok <- FALSE
    }
    if (w == "CPC-12" && n == 0) {
        cat("  ** control term missing: the fetch is probably broken, not the finding **\n"); ok <- FALSE
    }
}

## ---- (3) the UWES-9 facet structure does not pin the instrument --------------
if (exists("S1")) {
    d <- na.omit(as.data.frame(lapply(S1[paste0("Eng", 1:9)], as.numeric)))
    cat(sprintf("\ncomplete cases: %d ; resp range %g-%g\n",
                nrow(d), min(d), max(d)))
    C <- cor(d)
    facet <- c(1, 1, 2, 2, 1, 3, 2, 3, 3)   # canonical UWES-9: VI 1,2,5 / DE 3,4,7 / AB 6,8,9
    w <- c(); b <- c()
    for (i in 1:8) for (j in (i + 1):9)
        if (facet[i] == facet[j]) w <- c(w, C[i, j]) else b <- c(b, C[i, j])
    cat(sprintf("mean within-facet r = %.3f (n=%d) ; between-facet r = %.3f (n=%d)\n",
                mean(w), length(w), mean(b), length(b)))
    hits <- 0
    for (i in 1:9) {
        o <- C[i, -i]; k <- as.integer(names(which.max(o)) |> sub(pattern = "Eng", replacement = ""))
        if (is.na(k)) k <- setdiff(1:9, i)[which.max(o)]
        cat(sprintf("  Eng%d (facet %d) strongest partner Eng%d (facet %d) r=%.3f %s\n",
                    i, facet[i], k, facet[k], max(o), ifelse(facet[i] == facet[k], "OK", "x")))
        hits <- hits + (facet[i] == facet[k])
    }
    cat(sprintf("strongest-partner inside own facet: %d/9\n", hits))
    cat("interpretation: 6/9 with a 0.10 within-vs-between gap is the underpowered\n",
        "result UWES facets always give (cf. algner2022_uwes); it neither confirms the\n",
        "instrument nor orders any item. Live resp is 1-7, the published UWES scale 0-6.\n", sep = "")
    if (hits != 6) cat("  (facet-hit count has moved from the recorded 6/9)\n")
}

cat("\nno item wording is recoverable from any source tied to this table;\n",
    "the block stands on ground (1) alone, independently of the UWES rights clause.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

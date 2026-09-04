# verify_short_dark_triad.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: the IRW `item` codes 1..27 are the columns of the Open
# Psychometrics SD3 `data.csv` in file order (M1..M9, N1..N9, P1..P9), because
# data/short_dark_triad.R drops `country`/`source`, pivots the remaining columns
# long in header order, and assigns item = row_number() over unique(item).
# The item_text shipped for code k is the codebook line for column k.
#
# FALSIFIABLE PREDICTION: for every code k and every response level r, the live
# count of (item=k, resp=r) equals the raw count of value r in raw column k --
# after the script's own `replace(., . == 0, NA)`. If any two items' texts were
# swapped, or the range were shifted by one, the 135 cells would not line up.
# The 27 raw count-vectors are pairwise distinct, so the match also identifies
# each item uniquely rather than only as a set.
#
# QUOTA NOTE: this uses a server-side GROUP BY rather than irw::irw_fetch(),
# which would export all 491,184 rows. Same live table, no export.

suppressMessages(library(irw))

TABLE <- "short_dark_triad"
SRC   <- "http://openpsychometrics.org/_rawdata/SD3.zip"

## ---- raw side -------------------------------------------------------------
tmp <- tempfile(fileext = ".zip")
utils::download.file(SRC, tmp, quiet = TRUE, mode = "wb")
dir <- tempfile(); dir.create(dir)
utils::unzip(tmp, exdir = dir)
csv <- list.files(dir, pattern = "^data\\.csv$", recursive = TRUE, full.names = TRUE)[1]
cb  <- list.files(dir, pattern = "^codebook\\.txt$", recursive = TRUE, full.names = TRUE)[1]
raw <- read.delim(csv, check.names = FALSE)
cols <- setdiff(names(raw), c("country", "source"))
cat("raw columns (script order):", paste(cols, collapse = " "), "\n")
cat("n raw respondents:", nrow(raw), "\n\n")

rawcnt <- t(sapply(cols, function(cn) {
    v <- raw[[cn]]; v[v == 0] <- NA
    as.integer(table(factor(v, levels = 1:5)))
}))
rownames(rawcnt) <- cols

## ---- live side (server-side aggregate, no export) --------------------------
ns  <- getNamespace("irw")
tbl <- ns$.fetch_redivis_table(TABLE, source = ns$.irw_resolve_source(source = "core"))
sql <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                     "TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n FROM `%s`",
                     "WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                     "GROUP BY item, resp"), tbl$qualified_reference)
live <- as.data.frame(ns$.irw_query_tibble(sql))
livecnt <- matrix(0L, nrow = 27, ncol = 5, dimnames = list(as.character(1:27), 1:5))
livecnt[cbind(as.character(live$item), as.character(as.integer(live$resp)))] <- as.integer(live$n)

## ---- compare 135 cells -----------------------------------------------------
txt <- iconv(readLines(cb, encoding = "latin1", warn = FALSE), "CP1252", "UTF-8")
stems <- trimws(sub("^[MNP][1-9]\t", "", grep("^[MNP][1-9]\t", txt, value = TRUE)))

cat(sprintf("%-5s %-4s %-38s %28s %28s %s\n",
            "item", "col", "item_text (truncated)", "raw 1..5", "live 1..5", "ok"))
ok <- logical(27)
for (k in 1:27) {
    r <- rawcnt[k, ]; l <- livecnt[k, ]
    ok[k] <- all(r == l)
    cat(sprintf("%-5d %-4s %-38s %28s %28s %s\n", k, cols[k],
                substr(stems[k], 1, 38),
                paste(r, collapse = "/"), paste(l, collapse = "/"),
                if (ok[k]) "ok" else "MISMATCH"))
}

## ---- uniqueness: does each column's profile match only its own item? -------
ambig <- sum(sapply(1:27, function(k)
    sum(apply(livecnt, 1, function(row) all(row == rawcnt[k, ]))) > 1))
cat(sprintf("\ncells matched: %d of 135\n", sum(rawcnt == livecnt)))
cat(sprintf("raw columns whose count-profile matches more than one live item: %d\n", ambig))

cat("Note: this pins every one of the 27 codes to a named source column, so it does\n",
    "establish order and membership outright. It does NOT check the codebook's own\n",
    "wording against the Jones & Paulhus (2014) published SD3, nor the anchor labels\n",
    "for resp 2 and 4, which the source leaves unlabeled and which ship blank.\n", sep = "")

cat(if (all(ok) && ambig == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

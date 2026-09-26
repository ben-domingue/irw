# verify_celik_2026_tipi.R -- Step 5b mapping check (batch_454).
#
# Code derivation: data/celik_2026_motivation_distance_ed.py assigns tipi01..tipi10
# POSITIONALLY, in column order, to the 10 TEZ_412VERI.xlsx columns whose header
# starts "Kendimi", with id = row index. Each header carries the trait pair in
# [brackets] (Google Forms grid export: "Kendimi ... olarak görürüm [<pair>]").
#
# Checks (what would break if two item texts were swapped):
#   1. Re-derive the table from the raw deposit xlsx and compare to the live table
#      cell for cell (id x item).
#   2. No two source columns identical, so the cell match separates every item.
#   3. Header diff: shipped item_text for tipiNN == bracket text of NN-th column.
#   4. INFORMATIONAL ONLY (not gated): correlations of the TIPI reverse-keyed
#      domain pairs. These are weak in this sample (only Extraversion's pair is
#      clearly negative), which is a known TIPI property for A/C/ES/O and says
#      nothing about the mapping, which checks 1-3 settle outright.

suppressMessages({ library(irw); library(readxl); library(jsonlite) })

TABLE <- "celik_2026_tipi"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))),
                 error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))

meta <- fromJSON("https://data.mendeley.com/public-api/datasets/hwp4wsb549")
f <- meta$files
url <- f$content_details$download_url[f$filename == "TEZ_412VERI.xlsx"]
tmp <- tempfile(fileext = ".xlsx")
download.file(url, tmp, mode = "wb", quiet = TRUE)
x <- read_excel(tmp, .name_repair = "minimal")
names(x) <- trimws(names(x))
tcols <- names(x)[startsWith(names(x), "Kendimi")]
cat("source TIPI columns:", length(tcols), "\n")
codes <- sprintf("tipi%02d", seq_along(tcols))
src <- as.data.frame(x[, tcols]); names(src) <- codes
src$id <- seq_len(nrow(src))
long <- reshape(src, direction = "long", varying = codes, v.names = "resp",
                timevar = "item", times = codes, idvar = "id")
long <- long[!is.na(long$resp), c("id", "item", "resp")]

live <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
m <- merge(long, live, by = c("id", "item"), all = TRUE, suffixes = c("_src", "_live"))
n_both <- sum(!is.na(m$resp_src) & !is.na(m$resp_live))
n_mis <- sum(m$resp_src != m$resp_live, na.rm = TRUE) + sum(is.na(m$resp_src) != is.na(m$resp_live))
cat(sprintf("cells: source %d, live %d, matched %d, disagreeing/unpaired %d\n",
            nrow(long), nrow(live), n_both, n_mis))

mat <- as.matrix(src[, codes])
diffs <- c(); dup <- 0
for (i in 1:9) for (j in (i + 1):10) {
  if (identical(mat[, i], mat[, j])) dup <- dup + 1
  diffs <- c(diffs, sum(mat[, i] != mat[, j], na.rm = TRUE))
}
cat(sprintf("identical source column pairs: %d; fewest differing respondents between any two columns: %d\n",
            dup, min(diffs)))

it <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
shipped <- tapply(it$item_text, it$item, function(v) unique(v))
hdr <- sub("^.*\\[(.*)\\]$", "\\1", tcols); names(hdr) <- codes
hd_ok <- sum(shipped[codes] == hdr[codes])
cat(sprintf("header diff: %d/10 shipped item_text identical to header bracket text at that position\n", hd_ok))
for (k in codes) cat(sprintf("  %s  %s\n", k, shipped[[k]]))

w <- reshape(live, direction = "wide", idvar = "id", timevar = "item")
names(w) <- sub("^resp\\.", "", names(w))
pairs <- list(c("tipi01", "tipi06"), c("tipi02", "tipi07"), c("tipi03", "tipi08"),
              c("tipi04", "tipi09"), c("tipi05", "tipi10"))
rs <- sapply(pairs, function(p) cor(w[[p[1]]], w[[p[2]]], use = "pairwise"))
cat("per-item live means:\n"); print(round(tapply(live$resp, live$item, mean)[codes], 3))
cat("TIPI reverse-keyed domain pairs (live data, informational, not gated):\n")
for (k in seq_along(pairs)) cat(sprintf("  r(%s,%s) = %+.3f\n", pairs[[k]][1], pairs[[k]][2], rs[k]))

cat("Does NOT establish: that the study's Google Form displayed Atak's 1-7 anchors; ",
    "the deposit stores bare integers and anchors come from Atak's published form.\n", sep = "")

ok <- n_mis == 0 && n_both == nrow(live) && dup == 0 && hd_ok == 10
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

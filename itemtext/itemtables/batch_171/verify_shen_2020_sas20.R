# verify_shen_2020_sas20.R -- Step 5b mapping check for shen_2020_sas20.
#
# Claim: data/shen_2020_sas20.py assigns item codes POSITIONALLY -- sas_i is the
# i-th of the source columns numbered 11..30 in each of the five PLOS S1-S5 XLS
# files -- and item_text is that column's own header ("11:I feel more nervous or
# anxious than usual" -> sas_1). Each source cell stores "<label>(<score>)", so
# the source ties both item text and option label to the stored number.
#
# Falsifiable prediction: for every item i, the live table's resp distribution
# (server-side GROUP BY, no export) equals the score distribution of source header
# column i, and of NO other column; and each shipped option_text equals the label
# the source pairs with that score for that item (items 5,9,13,17,19 reversed).
# A swap of any two item texts, or a flipped option direction, breaks this.

suppressMessages({ library(irw); library(readxl); library(httr) })

TABLE <- "shen_2020_sas20"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "",
          grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))), error = function(e) ".")
ITEMS_CSV <- file.path(here, paste0(TABLE, "__items.csv"))

# ---- source: the five hospital files ----
tmp <- tempfile(); dir.create(tmp)
src <- list()
for (s in sprintf("s%03d", 1:5)) {
  f <- file.path(tmp, paste0(s, ".xls"))
  u <- sprintf("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.%s", s)
  r <- GET(u, write_disk(f, overwrite = TRUE), user_agent("IRW-itemtext-verify"), timeout(120))
  stop_for_status(r)
  d <- as.data.frame(read_excel(f), check.names = FALSE)
  num <- suppressWarnings(as.integer(sub(":.*$", "", names(d))))
  cols <- names(d)[!is.na(num) & num >= 11 & num <= 30]
  stopifnot(length(cols) == 20)
  src[[s]] <- d[, cols]
}
hdr <- names(src[[1]])
stopifnot(all(sapply(src, function(x) identical(names(x), hdr))))
raw <- do.call(rbind, lapply(src, function(x) { names(x) <- hdr; x }))
cat("source rows:", nrow(raw), "\n")

lab   <- lapply(raw, function(v) trimws(sub("\\((\\d+(\\.\\d+)?)\\)$", "", v)))
score <- lapply(raw, function(v) as.numeric(sub("^.*\\((\\d+(\\.\\d+)?)\\)$", "\\1", v)))
src_counts <- t(sapply(score, function(v) table(factor(v, levels = 1:4))))  # 20 x 4, row = header column

# ---- live: server-side aggregates ----
tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
q <- sprintf("SELECT CAST(item AS STRING) item, CAST(resp AS STRING) resp, COUNT(*) n FROM `%s` WHERE resp IS NOT NULL GROUP BY item, resp", tbl$qualified_reference)
lv <- as.data.frame(irw:::.irw_query_tibble(q))
live_counts <- t(sapply(paste0("sas_", 1:20), function(it)
  sapply(1:4, function(k) { n <- lv$n[lv$item == it & as.numeric(lv$resp) == k]; if (length(n)) n else 0 })))

ok <- TRUE
cat(sprintf("\n%-7s %-52s %-22s %-22s %s\n", "item", "source header", "source n(1..4)", "live n(1..4)", "matching cols"))
for (i in 1:20) {
  m <- which(apply(src_counts, 1, function(r) all(r == live_counts[i, ])))
  cat(sprintf("%-7s %-52s %-22s %-22s %s\n", paste0("sas_", i), substr(hdr[i], 1, 52),
              paste(src_counts[i, ], collapse = "/"), paste(live_counts[i, ], collapse = "/"),
              paste(m, collapse = ",")))
  if (!identical(as.integer(m), i)) ok <- FALSE
}

# ---- shipped CSV: item_text == header at position i; option_text == source label for that score ----
it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
bad_text <- 0; bad_opt <- 0
for (i in 1:20) {
  rows <- it[it$item == paste0("sas_", i), ]
  if (any(rows$item_text != sub("^\\d+:", "", hdr[i]))) bad_text <- bad_text + 1
  for (k in 1:4) {
    srclab <- unique(lab[[i]][score[[i]] == k])
    if (length(srclab) != 1 || rows$option_text[rows$resp == k] != srclab) bad_opt <- bad_opt + 1
  }
}
cat(sprintf("\nitem_text vs source header at position: %d/20 mismatches\n", bad_text))
cat(sprintf("option_text vs source label paired with each score: %d/80 mismatches\n", bad_opt))
if (bad_text > 0 || bad_opt > 0) ok <- FALSE

tot <- Reduce(`+`, score)
cat(sprintf("source raw total: mean %.2f SD %.2f (paper abstract: 30.85 +/- 6.89)\n", mean(tot), sd(tot)))
cat("Count vectors are pairwise distinct across the 20 columns, so each live item matches exactly one header.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

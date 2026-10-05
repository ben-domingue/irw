# verify_matosaslopez_2022_bars_teaching_blended.R -- Step 5b mapping check (batch_735).
#
# Claim, in three links:
#   (a) BARS_k is the deposit column whose Spanish header is item_text(BARS_k).
#       data/matosaslopez_2022_bars_teaching.py renames each column by keyword match on
#       that header (a label-keyed rename), so this is re-run here cell for cell against
#       the Zenodo xlsx (10.5281/zenodo.15160903, CC BY 4.0): live BARS_k must equal that
#       column for every respondent and must NOT equal any other item column.
#   (b) The anchor set shipped for BARS_k is Behav Sci 2022 12:394 Appendix A.k. The link
#       is the category NAME: the appendix headings (PMC XML <title>s, hard-coded below)
#       are word-for-word English renderings of the deposit's Spanish headers, in the same
#       order. Checked here against the shipped file's item_text / item_text_translated.
#   (c) resp r = the anchor the appendix prints at scale point r (1 = least effective).
#       Corroborated against the paper's Table 1: per-item skewness of the live data should
#       rank-agree with the published skewness, and reversing the scale would flip the sign.
#
# What this does NOT establish: (c) is rank corroboration only -- the deposit does not
# reproduce the paper's published statistics numerically (kurtosis, means and the Table 2
# factor split all differ; printed below), so the data cannot independently confirm that
# the deposit's own column headers are correct. The item<->text tie rests on those
# headers (link a) and on the name translation (link b).

suppressMessages({library(irw); library(readxl)})
TABLE <- "matosaslopez_2022_bars_teaching_blended"

## the shipped items CSV, found relative to this script
this <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
here <- if (length(this)) dirname(normalizePath(this)) else getwd()
cand <- c(file.path(here, paste0(TABLE, "__items.csv")),
          file.path("itemtables/batch_735", paste0(TABLE, "__items.csv")))
cand <- cand[file.exists(cand)]
if (!length(cand)) stop("cannot find the shipped items CSV")
it <- read.csv(cand[1], stringsAsFactors = FALSE, encoding = "UTF-8")
ship <- unique(it[, c("item", "item_text", "item_text_translated")])
ship <- ship[match(paste0("BARS_", 1:10), ship$item), ]

## (b) appendix headings, Behav Sci 2022 12:394 Appendix A.1..A.10 (PMC9598132 XML titles)
APPENDIX <- c("Course Introduction", "Evaluation System Description", "Time Management",
              "General Availability", "Organizational Consistency",
              "Evaluation System Implementation", "Dealing with Doubts",
              "Explicative Capacity", "Follow-Up Easiness", "General Satisfaction")

## deposit xlsx: Zenodo API, falling back to the local cache
f <- tempfile(fileext = ".xlsx")
ok <- tryCatch({
  rec <- jsonlite::fromJSON("https://zenodo.org/api/records/15160903")
  u <- rec$files$links$self[grepl("\\.xlsx?$", rec$files$key, ignore.case = TRUE)][1]
  download.file(u, f, mode = "wb", quiet = TRUE); TRUE
}, error = function(e) FALSE)
if (!ok) {
  alt <- c(".cache/matosaslopez_2022_bars_teaching/r15160903_0.xlsx",
           "itemtext/.cache/matosaslopez_2022_bars_teaching/r15160903_0.xlsx",
           file.path(here, "../../.cache/matosaslopez_2022_bars_teaching/r15160903_0.xlsx"))
  alt <- alt[file.exists(alt)]
  if (!length(alt)) stop("cannot fetch the Zenodo xlsx and no cached copy found")
  f <- alt[1]
}
x <- as.data.frame(suppressMessages(read_excel(f)))
x$id <- seq_len(nrow(x))            # the processing script's id = row number
hdr <- names(x)[5:14]

cat("(b) shipped item_text / item_text_translated vs deposit header / appendix heading:\n")
for (k in 1:10) cat(sprintf("  BARS_%-2d item_text=%-40s hdr[%d]=%-40s | translated=%-33s A.%d=%s\n",
    k, ship$item_text[k], k, hdr[k], ship$item_text_translated[k], k, APPENDIX[k]))
b_ok <- all(ship$item_text == hdr) && all(ship$item_text_translated == APPENDIX)
cat(sprintf("  item_text == deposit header at position k: %d/10; item_text_translated == Appendix A.k heading: %d/10\n",
            sum(ship$item_text == hdr), sum(ship$item_text_translated == APPENDIX)))

## (a) live vs deposit, cell for cell
d <- irw::irw_fetch(TABLE)
live <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
                timevar = "item", direction = "wide")
m <- merge(x, live, by = "id")
cat(sprintf("\n(a) respondents: deposit %d, live %d, matched on id %d\n", nrow(x), nrow(live), nrow(m)))
A <- matrix(NA, 10, 10, dimnames = list(paste0("BARS_", 1:10), paste0("col:", substr(hdr, 1, 12))))
for (i in 1:10) for (j in 1:10)
  A[i, j] <- mean(m[[paste0("resp.BARS_", i)]] == m[[ship$item_text[j]]], na.rm = TRUE)
cat("agreement, live BARS_i (rows) vs deposit column headed item_text(BARS_j) (cols):\n")
print(round(A, 3))
off <- A; diag(off) <- NA
a_ok <- all(diag(A) == 1) && max(off, na.rm = TRUE) < 1
cat(sprintf("diagonal all 1: %s; largest off-diagonal: %.3f\n", all(diag(A) == 1), max(off, na.rm = TRUE)))

## (c) direction, against Table 1 skewness (and Table 6 means, printed only)
PUB_SKEW <- c(-0.441, -0.245, -0.062, 0.187, 0.054, -0.145, 0.236, 0.435, 0.161, 0.393)
PUB_MEAN <- c(3.48, 3.39, 3.14, 2.98, 3.55, 3.53, 2.75, 2.79, 3.11, 3.01)
PUB_KURT <- c(-0.424, -0.232, -0.730, -0.433, -0.627, -0.465, -0.594, -0.276, -0.559, -0.571)
sk <- function(v) { v <- v[!is.na(v)]; n <- length(v); z <- (v - mean(v)) / sd(v); n / ((n-1)*(n-2)) * sum(z^3) }
ku <- function(v) { v <- v[!is.na(v)]; n <- length(v); z <- (v - mean(v)) / sd(v)
  n*(n+1)/((n-1)*(n-2)*(n-3)) * sum(z^4) - 3*(n-1)^2/((n-2)*(n-3)) }
L <- lapply(1:10, function(k) m[[paste0("resp.BARS_", k)]])
ls <- sapply(L, sk); lk <- sapply(L, ku); lm <- sapply(L, mean, na.rm = TRUE)
cat("\n(c) item                              skew pub/live    kurt pub/live    mean pub/live\n")
for (k in 1:10) cat(sprintf("  %-34s %6.3f %6.3f   %6.3f %6.3f   %5.2f %5.2f\n",
    APPENDIX[k], PUB_SKEW[k], ls[k], PUB_KURT[k], lk[k], PUB_MEAN[k], lm[k]))
rs <- cor(ls, PUB_SKEW, method = "spearman"); rr <- cor(-ls, PUB_SKEW, method = "spearman")
rm <- cor(lm, PUB_MEAN, method = "spearman")
cat(sprintf("Spearman skew live vs Table 1: %.3f (scale reversed: %.3f); means vs Table 6: %.3f\n", rs, rr, rm))
o1 <- it$option_text[it$resp == 1 & it$item != "BARS_10"]
o5 <- it$option_text[it$resp == 5]
cat(sprintf("resp=1 anchors containing 'does NOT' (items 1-9): %d/9; resp=5 anchors containing 'NOT': %d/10\n",
            sum(grepl("does NOT", o1)), sum(grepl("NOT", o5))))
c_ok <- rs >= 0.7 && rr < 0 && all(grepl("does NOT", o1)) && !any(grepl("NOT", o5))
cat("NOTE: the deposit does not reproduce the paper's statistics numerically (kurtosis\n",
    "-1.2..-1.6 live vs -0.2..-0.7 published; means differ by up to 0.67); only the rank\n",
    "order of skewness is used, as a direction check, not as item identification.\n", sep = "")

cat(sprintf("\nlinks: (a) %s  (b) %s  (c) %s\n", a_ok, b_ok, c_ok))
cat(if (a_ok && b_ok && c_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

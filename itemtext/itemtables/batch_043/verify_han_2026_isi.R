# verify_han_2026_isi.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. The live items ISI01..ISI07 are the seven ISI ratings of
# Han et al. (2026, PeerJ 10.7717/peerj.20868) in the order in which the study's
# own raw survey file holds them:
#   ISI01/02/03 = the 1st/2nd/3rd component of the composite severity field
#                 ("1,1,1"-style) in ISI.xlsx  (= S1 File, peerj-14-20868-s001.xlsx)
#   ISI04 = "How satisfied are you with your sleep?"
#   ISI05 = "How much do your sleep problems affect your daily life? ..."
#   ISI06 = "Are your sleep problems more significant compared to other factors
#            reducing your quality of life?"
#   ISI07 = "Are you anxious or worried about your current sleep problems?"
# ISI04..ISI07 are named in the study's OWN analysis script (S3 File,
# peerj-14-20868-s003.r, lines 91-94) by an exact colnames() match on those header
# strings, so the code->question tie there is by name, not by position.
#
# The falsifiable part is the tie between those source columns and the live IRW
# columns, plus the per-item response coding (the merged file shifted ISI01 and
# ISI07 down by one and left ISI02..ISI06 on the raw 1-5 codes). Both are tested by
# matching the response-level COUNT VECTOR of each source column against each live
# item: a correct mapping puts the minimum distance on the diagonal for every row
# and every column of the 7x7 matrix.
#
# NOT established here: which sleep sub-domain (falling asleep / staying asleep /
# early morning awakening) each of the three severity components is. The deposit
# never labels them; that assignment comes from the paper's ordered item labels
# and canonical ISI order. Hence PARTIAL, not VERIFIED.

suppressMessages({library(irw); library(readxl)})

TABLE <- "han_2026_isi"
ITEMS <- sprintf("ISI0%d", 1:7)
# live items whose codes were shifted down by 1 relative to the raw survey file
SHIFTED <- c("ISI01", "ISI07")

## ---- source: raw survey file from the Europe PMC supplementary zip -------------
zipf <- tempfile(fileext = ".zip"); dst <- tempfile()
utils::download.file(
  "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13048223/supplementaryFiles",
  zipf, quiet = TRUE, mode = "wb")
utils::unzip(zipf, files = "peerj-14-20868-s001.xlsx", exdir = dst)
raw <- readxl::read_excel(file.path(dst, "peerj-14-20868-s001.xlsx"))

sev <- strsplit(gsub("[()]", "", as.character(raw[[2]])), ",")
src <- data.frame(
  S1 = suppressWarnings(as.numeric(trimws(sapply(sev, `[`, 1)))),
  S2 = suppressWarnings(as.numeric(trimws(sapply(sev, `[`, 2)))),
  S3 = suppressWarnings(as.numeric(trimws(sapply(sev, `[`, 3)))),
  S4 = as.numeric(raw[[3]]), S5 = as.numeric(raw[[4]]),
  S6 = as.numeric(raw[[5]]), S7 = as.numeric(raw[[6]]))
src <- src[stats::complete.cases(src), ]
cat(sprintf("raw survey file: %d complete cases\n", nrow(src)))
cat("raw column 2 header (severity, split into three):\n  ", names(raw)[2], "\n")
for (j in 3:6) cat(sprintf("raw column %d header -> ISI0%d:\n   %s\n", j, j + 1, names(raw)[j]))

## ---- live IRW table -----------------------------------------------------------
d <- irw::irw_fetch(TABLE)
LEV <- 0:5
cnt_live <- sapply(ITEMS, function(it) {
  v <- d$resp[d$item == it]
  if (it %in% SHIFTED) v <- v + 1          # put back on the raw 1-5 coding
  as.integer(table(factor(v, levels = LEV)))
})
cnt_src <- sapply(src, function(v) as.integer(table(factor(v, levels = LEV))))

cat("\nresponse-level counts, raw 1-5 coding (rows = level 0..5)\n")
cat(sprintf("%-6s %s | %s\n", "", paste(sprintf("%6s", paste0("src", 1:7)), collapse = ""),
            paste(sprintf("%6s", ITEMS), collapse = "")))
for (i in seq_along(LEV))
  cat(sprintf("lev %d %s | %s\n", LEV[i],
              paste(sprintf("%6d", cnt_src[i, ]), collapse = ""),
              paste(sprintf("%6d", cnt_live[i, ]), collapse = "")))

## ---- 7x7 assignment -----------------------------------------------------------
D <- outer(1:7, 1:7, Vectorize(function(a, b) sum(abs(cnt_src[, a] - cnt_live[, b]))))
cat("\nL1 distance between source column (row) and live item (col):\n")
cat(sprintf("%-6s%s\n", "", paste(sprintf("%7s", ITEMS), collapse = "")))
for (a in 1:7) cat(sprintf("src%-3d%s\n", a, paste(sprintf("%7d", D[a, ]), collapse = "")))

row_ok <- all(apply(D, 1, which.min) == 1:7)
col_ok <- all(apply(D, 2, which.min) == 1:7)
diag_max <- max(diag(D)); offdiag_min <- min(D[row(D) != col(D)])
cat(sprintf("\nworst diagonal distance %d (sample differs by %d rows); best off-diagonal %d\n",
            diag_max, abs(nrow(src) - sum(d$item == ITEMS[1])), offdiag_min))

## ---- coding check: which live items were shifted ------------------------------
mins <- tapply(d$resp, d$item, min)[ITEMS]
maxs <- tapply(d$resp, d$item, max)[ITEMS]
cat("\nlive per-item range: ",
    paste(sprintf("%s=%d-%d", ITEMS, mins, maxs), collapse = "  "), "\n")
shift_ok <- all(maxs[SHIFTED] == 4) && all(maxs[setdiff(ITEMS, SHIFTED)] == 5)

## ---- secondary: paper Table 2 per-item M (SD) ---------------------------------
PUB_M  <- c(0.69, 1.57, 1.57, 1.84, 1.65, 1.61, 0.54)
PUB_SD <- c(0.95, 0.90, 0.91, 1.12, 0.95, 0.90, 0.86)
obs_m  <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd <- tapply(d$resp, d$item, stats::sd)[ITEMS]
cat("\npaper Table 2 per-item M (SD) vs live (paper rows are keyed ISI1..ISI7 in order):\n")
for (i in 1:7) cat(sprintf("  %s  paper %.2f (%.2f)   live %.2f (%.2f)\n",
                           ITEMS[i], PUB_M[i], PUB_SD[i], obs_m[i], obs_sd[i]))
pub_ok <- max(abs(obs_m - PUB_M)) <= 0.01 && max(abs(obs_sd - PUB_SD)) <= 0.01

cat("\nNote: the paper's Table 2 LABELS for ISI5/ISI6/ISI7 (noticeability / distress /\n",
    "interference, i.e. canonical ISI numbering) contradict the study's own analysis\n",
    "script, which maps those same columns to the daily-life-impact, quality-of-life-\n",
    "prominence and worry questions. The shipped text follows the script and the raw\n",
    "file's own column headers. This script does not adjudicate the three severity\n",
    "sub-domain labels on ISI01-03.\n", sep = "")

cat(if (row_ok && col_ok && shift_ok && pub_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

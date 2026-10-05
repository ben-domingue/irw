# verify_clemente_2024_sd4.R -- Step 5b, re-runnable evidence (automated_finding, PMC sweep 2026-10-04).
#
# CLAIM: SD4_k in clemente_2024_sd4 is item k of the SD4 block printed in the
# article's SI questionnaire (mmc1.pdf, Spanish), so item_text for SD4_k is that
# statement. mapping_basis paper_order: the .sav columns carry no labels.
#
# Route: subscale block structure. The deposit ships the four SD4 subscale
# scores. By CONTENT the printed statements group as
#   Machiavellianism  1-7   ("... dejar que la gente conozca tus secretos", "Manipular ...")
#   Narcissism        8-14  ("líder natural", "cualidades excepcionales", "lucirme")
#   Psychopathy       15-21 ("fuera de control", "problemas con la ley", "situaciones peligrosas")
#   Sadism            22-28 ("pelea a puñetazos", "merecen sufrir", "herir ... con palabras")
# (Paulhus et al., 2021 order). For each subscale score, the 7-item contiguous
# windows of SD4_1..SD4_28 whose row means equal it on all respondents are
# printed, plus a greedy check that no item outside the predicted block can be
# swapped in without breaking the equality. A statement assigned to a column in
# another block would break this.
# NOT established: order WITHIN each block of seven (means are symmetric) -- PARTIAL.
#
# Data: staged response CSV (not on Redivis yet) + the figshare .sav. Run from
# the repo root (irw/src) or automated_finding/.

suppressMessages(library(haven))
TABLE <- "clemente_2024_sd4"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
sf <- tempfile(fileext = ".sav")
download.file("https://ndownloader.figshare.com/files/41280237", sf, quiet = TRUE, mode = "wb")
raw <- as.data.frame(zap_labels(read_sav(sf)))
raw$id <- seq_len(nrow(raw))          # data/clemente_2024_divorced_parents.py: row index

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- merge(w, raw[, c("id", "SD4_Machiavellianism", "SD4_Narcissism", "SD4_Psychopathy",
                      "SD4_Sadism")], by = "id")
cat("respondents compared:", nrow(w), "\n\n")
EXPECT <- list(SD4_Machiavellianism = 1:7, SD4_Narcissism = 8:14,
               SD4_Psychopathy = 15:21, SD4_Sadism = 22:28)
eqm <- function(k, s) all(abs(rowMeans(w[, paste0("SD4_", k)]) - w[[s]]) < 1e-6)
ok <- TRUE
for (s in names(EXPECT)) {
  win <- Filter(function(a) eqm(a:(a + 6), s), 1:22)
  # single swaps: replace one predicted item by any outside item
  swaps <- 0
  for (i in EXPECT[[s]]) for (o in setdiff(1:28, EXPECT[[s]]))
    if (eqm(c(setdiff(EXPECT[[s]], i), o), s)) swaps <- swaps + 1
  hit <- identical(win, EXPECT[[s]][1]) && swaps == 0
  ok <- ok && hit
  cat(sprintf("  %-22s expected SD4_%d-%d  matching windows start at: %-6s  single swaps that still match: %d %s\n",
              s, min(EXPECT[[s]]), max(EXPECT[[s]]), paste(win, collapse = ","), swaps,
              if (hit) "" else "<-- MISMATCH"))
}
cat("\nEach content block is pinned to its own seven columns; order within a block is\n",
    "not tested (means are symmetric).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

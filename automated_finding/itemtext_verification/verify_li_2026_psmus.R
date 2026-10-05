# verify_li_2026_psmus.R -- Step 5b, re-runnable evidence (automated_finding, PMC sweep 2026-10-04).
#
# CLAIM: ItemK in li_2026_psmus is the K-th numbered stem of the SI item list
# (peerj-14-21138-s002.docx), so item_text for ItemK is that stem.
# mapping_basis paper_order: the xlsx headers carry the number, not the wording.
#
# Route: subscale block structure. The deposit (s001.xlsx) ships five subscale
# sums alongside the items. By CONTENT, the stems group as
#   aPOSI (preference for online social interaction)  1-3  ("I prefer networking ...")
#   MoodRegulation                                     4-6  ("... make myself feel better ...")
#   cognitivepreoccupation                             7-9  ("... preoccupied ... lost ... obsessively")
#   compulsiveuse                                     10-12 ("difficult to control ...")
#   negativeoutcomes                                  13-15 ("... problems for me in my life")
# For each subscale column, every 3-item subset of Item1..Item15 is tried and the
# subsets whose row sums equal it on all respondents are printed. The claim
# predicts exactly the triple above. A stem assigned to an item in another block
# would break this.
# NOT established: order WITHIN each triple (sums are symmetric) -- PARTIAL.
#
# Data: staged response CSV (not on Redivis yet) + raw s001.xlsx from the Europe
# PMC supplementaryFiles zip. Run from the repo root (irw/src) or automated_finding/.

suppressMessages(library(readxl))
TABLE <- "li_2026_psmus"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)

zf <- tempfile(fileext = ".zip")
download.file("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13175062/supplementaryFiles",
              zf, quiet = TRUE, mode = "wb")
td <- tempfile(); dir.create(td)
unzip(zf, files = "peerj-14-21138-s001.xlsx", exdir = td)
raw <- as.data.frame(read_excel(file.path(td, "peerj-14-21138-s001.xlsx")))
raw$id <- seq_len(nrow(raw))          # data/li_2026_psmus.py: row index before dedup

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- merge(w, raw[, c("id", "aPOSI", "MoodRegulation", "cognitivepreoccupation",
                      "compulsiveuse", "negativeoutcomes")], by = "id")
cat("respondents compared:", nrow(w), "\n\n")

EXPECT <- list(aPOSI = 1:3, MoodRegulation = 4:6, cognitivepreoccupation = 7:9,
               compulsiveuse = 10:12, negativeoutcomes = 13:15)
trip <- combn(15, 3)
ok <- TRUE
for (s in names(EXPECT)) {
  hits <- which(apply(trip, 2, function(k)
    all(rowSums(w[, paste0("Item", k)]) == w[[s]])))
  found <- vapply(hits, function(h) paste(trip[, h], collapse = ","), "")
  hit <- length(hits) == 1 && identical(as.integer(trip[, hits]), EXPECT[[s]])
  ok <- ok && hit
  cat(sprintf("  %-24s expected items %-9s exact-sum triples found: %s %s\n", s,
              paste(EXPECT[[s]], collapse = ","), paste(found, collapse = " | "),
              if (hit) "" else "<-- MISMATCH"))
}
cat("\nEach content block is pinned to exactly its own three item codes; order within\n",
    "a block is not tested (sums are symmetric).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_pcl5_xiong_2025.R -- Step 5b mapping check for pcl5_xiong_2025 (batch_448).
#
# Claim: IRW item pclN carries PCL-5 standard-form item N (canonical NCPTSD numbering).
# The deposit's .sav files carry NO variable/value labels on pcl1..pcl20, so the mapping
# is inferred from the code's numeric suffix. What the deposit DOES carry is the authors'
# own DSM-5 cluster scores R (re-experiencing), A (avoidance), NACM (negative alterations
# in cognition and mood), H (hyperarousal). Under canonical numbering these are
# B = items 1-5, C = 6-7, D = 8-14, E = 15-20.
#
# Checks:
#   1. Live IRW per-item means equal the pooled .sav column means for the same name
#      (ties the IRW code to the deposit column).
#   2. Route 3: stored R/A/NACM/H equal the row sums of the canonical item blocks in
#      every row of all four samples, and dropping ANY single item from its block (or
#      adding any outside item to it) breaks the match -- so each item's cluster
#      membership is pinned individually.
#   3. Route 7 marker: pcl16 ("Taking too many risks...", the reckless-behaviour item)
#      is the least endorsed of the 20.
# Does NOT establish: order WITHIN a cluster (e.g. pcl6 vs pcl7, or pcl1..pcl5 among
# themselves) -- beyond pcl16, the within-cluster assignment rests on the code numbering.

suppressMessages({ library(irw); library(haven) })
TABLE <- "pcl5_xiong_2025"
VO <- "view_only=3b9ee6f978a648deb17d81d244d6c158"
FILES <- c(ado = "https://osf.io/download/cr5e9/",
           col = "https://osf.io/download/pcqjk/",
           com = "https://osf.io/download/jfz9s/",
           pri = "https://osf.io/download/66f3d7e045964aa0dba859b8/")
tmp <- tempfile(); dir.create(tmp)
src <- lapply(names(FILES), function(n) {
  p <- file.path(tmp, paste0(n, ".sav"))
  download.file(paste0(FILES[[n]], "?", VO), p, quiet = TRUE, mode = "wb")
  # Adolescent file has non-UTF-8 bytes in its header; latin1 reads the numerics fine.
  d <- tryCatch(read_sav(p), error = function(e) read_sav(p, encoding = "latin1"))
  as.data.frame(zap_labels(d))
})
names(src) <- names(FILES)
all <- do.call(rbind, lapply(src, function(d) d[, c(paste0("pcl", 1:20), "R", "A", "NACM", "H")]))
cat("deposit rows:", nrow(all), "\n")

ok <- TRUE

# ---- 1. live vs deposit per-item means ----
live <- irw::irw_fetch(TABLE)
lm <- tapply(live$resp, live$item, mean, na.rm = TRUE)
sm <- colMeans(all[, paste0("pcl", 1:20)], na.rm = TRUE)
d1 <- max(abs(lm[names(sm)] - sm))
cat(sprintf("\n[1] live rows %d, ids %d; max |live mean - deposit mean| over 20 items = %.2e\n",
            nrow(live), length(unique(live$id)), d1))
if (d1 > 1e-9) ok <- FALSE

# ---- 2. cluster sums ----
BLOCKS <- list(R = 1:5, A = 6:7, NACM = 8:14, H = 15:20)
cat("\n[2] stored cluster score vs row sum of canonical block (rows matching / total)\n")
for (s in names(BLOCKS)) {
  m <- sum(rowSums(all[, paste0("pcl", BLOCKS[[s]])]) == all[[s]], na.rm = TRUE)
  cat(sprintf("  %-5s items %-6s %d / %d\n", s, paste(range(BLOCKS[[s]]), collapse = "-"), m, nrow(all)))
  if (m != nrow(all)) ok <- FALSE
}
cat("\n  single-item perturbations (max rows still matching after the change):\n")
for (s in names(BLOCKS)) {
  b <- BLOCKS[[s]]
  drop <- sapply(b, function(i) sum(rowSums(all[, paste0("pcl", setdiff(b, i)), drop = FALSE]) == all[[s]]))
  add <- sapply(setdiff(1:20, b), function(i) sum(rowSums(all[, paste0("pcl", c(b, i))]) == all[[s]]))
  cat(sprintf("  %-5s drop-one: max %d / %d   add-one-outside: max %d / %d\n",
              s, max(drop), nrow(all), max(add), nrow(all)))
  if (max(drop) == nrow(all) || max(add) == nrow(all)) ok <- FALSE
}

# ---- 3. marker item ----
ord <- sort(sm)
cat("\n[3] lowest item means (deposit, pooled):\n"); print(round(head(ord, 4), 3))
if (names(ord)[1] != "pcl16") ok <- FALSE

cat("\nNot established: order within a cluster (pcl1-5, pcl6-7, pcl8-14, pcl15-20) beyond the pcl16 marker.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_heekerens2025_phq.R -- Step 5b check for heekerens2025_phq (batch_431).
#
# Claim: live PHQ_n == deposit column phq_n (Zenodo 10.5281/zenodo.14984624,
# dss_2.xlsx), and phq_n is PHQ-8 item n in the standard PHQ-D/PHQ-9 order
# (items 1-8 of the PHQ-9), with resp 1..4 = PHQ score 0..3 + 1
# (1 = "Ueberhaupt nicht" .. 4 = "Beinahe jeden Tag").
#
# What this checks, and what it does not:
#   (a) code -> deposit column: each live item's full 1..4 frequency vector equals
#       exactly one deposit column's, and that column is phq_n for PHQ_n.
#   (b) option direction: PHQ total correlates positively with the DSS and PDS-5
#       symptom totals in the same deposit, so higher resp = more frequent symptoms.
#   (c) PHQ-2 core pair: phq_1/phq_2 are each other's strongest correlate.
#   (d) psychomotor item (8): lowest mean and highest floor of the eight.
#   NOT established: the order among items 3-7, or 1 vs 2 -- the deposit carries
#   no labels and the paper (10.1037/pas0001432, closed access) was not available,
#   so code -> wording within those sets rests on the standard PHQ numbering.

suppressMessages({ library(irw); library(readxl) })
TABLE <- "heekerens2025_phq"
ok <- TRUE

d <- irw::irw_fetch(TABLE)
f <- tempfile(fileext = ".xlsx")
download.file("https://zenodo.org/api/records/14984624/files/dss_2.xlsx/content", f,
              mode = "wb", quiet = TRUE)
x <- as.data.frame(read_excel(f))
dep <- x[, paste0("phq_", 1:8)]

# (a) frequency-vector match, live item x deposit column
freq <- function(v) as.integer(table(factor(v, levels = 1:4)))
live_f <- sapply(paste0("PHQ_", 1:8), function(i) freq(d$resp[d$item == i]))
dep_f  <- sapply(dep, freq)
cat("(a) live item -> deposit columns with identical 1..4 counts\n")
for (i in 1:8) {
  hits <- names(dep)[apply(dep_f, 2, function(col) all(col == live_f[, i]))]
  cat(sprintf("  PHQ_%d counts %s -> %s\n", i, paste(live_f[, i], collapse = "/"),
              paste(hits, collapse = ",")))
  if (!identical(hits, paste0("phq_", i))) ok <- FALSE
}

# (b) direction
tot <- rowSums(dep)
dss <- rowSums(x[, paste0("dss_", 1:20)]); pds <- rowSums(x[, paste0("pds_", 1:7)])
r_dss <- cor(tot, dss, use = "pair"); r_pds <- cor(tot, pds, use = "pair")
cat(sprintf("(b) r(PHQ total, DSS total) = %.3f ; r(PHQ total, PDS-5 total) = %.3f\n", r_dss, r_pds))
cat(sprintf("    PHQ-8 total on 0-3 scoring: M = %.2f, SD = %.2f (n = %d)\n",
            mean(tot - 8), sd(tot), sum(!is.na(tot))))
if (!(r_dss > 0.2 && r_pds > 0.2)) ok <- FALSE

# (c) PHQ-2 pair
R <- cor(dep, use = "pair"); diag(R) <- NA
best1 <- names(which.max(R["phq_1", ])); best2 <- names(which.max(R["phq_2", ]))
cat(sprintf("(c) r(phq_1,phq_2) = %.3f ; strongest partner of phq_1 = %s, of phq_2 = %s\n",
            R["phq_1", "phq_2"], best1, best2))
if (!(best1 == "phq_2" && best2 == "phq_1")) ok <- FALSE

# (d) psychomotor item
mn <- colMeans(dep); fl <- colMeans(dep == 1)
cat("(d) means: ", paste(sprintf("%.2f", mn), collapse = " "), "\n")
cat("    floor%: ", paste(sprintf("%.1f", 100 * fl), collapse = " "), "\n")
if (!(which.min(mn) == 8 && which.max(fl) == 8)) ok <- FALSE

cat("Not established: order among items 3-7 and item 1 vs item 2 (standard PHQ numbering assumed).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

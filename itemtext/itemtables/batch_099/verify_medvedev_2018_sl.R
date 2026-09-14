# Step 5b re-runnable evidence for medvedev_2018_sl (mapping_basis = reconstructed).
#
# THE CLAIM: sl_1..sl_5 are the five Satisfaction With Life Scale statements
# (Diener, Emmons, Larsen & Griffin, 1985) in the instrument's printed order, and
# resp 1..7 runs 1 = "Strongly disagree" .. 7 = "Strongly agree".
#
# WHAT WOULD BREAK IT: nothing in the deposit labels SL1..SL5 (bare headers, no
# cell comments, no SPSS labels) and the article prints no SWLS item. But the paper
# publishes the scale's own descriptives (Table 2: n 178, 5 items, M 4.57, SD 1.196,
# alpha 0.871), and the deposit carries the study's own SLTOTAL composite. Together
# those falsify (a) any item in this table not belonging to the SL scale and (b) the
# reversed anchor reading, which would put the mean at 8 - 4.57 = 3.43.
#
# WHAT THIS DOES NOT ESTABLISH: neither check distinguishes one SWLS statement from
# another. Swapping sl_1 (".. close to my ideal") with sl_2 ("The conditions of my
# life are excellent") leaves the scale mean, SD, alpha and SLTOTAL bit-identical.
# CHECK 3 is a marker/structure diagnostic and is corroboration, not proof. Hence
# the recorded status is PARTIAL.

suppressMessages(library(irw))
TABLE <- "medvedev_2018_sl"

## published, Medvedev (2018) PeerJ 6:e4903, Table 2, row "Satisfaction with life"
PUB_N <- 178; PUB_M <- 4.57; PUB_SD <- 1.196; PUB_A <- 0.871

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar="id", timevar="item",
             direction="wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
m <- as.matrix(w[, paste0("sl_", 1:5)])
m <- m[complete.cases(m), ]
pm <- rowMeans(m)
k <- 5
alpha <- k/(k-1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))

cat("CHECK 1 -- live scale descriptives vs the paper's Table 2\n")
cat(sprintf("  %-22s %10s %10s %8s\n", "", "published", "observed", "diff"))
cat(sprintf("  %-22s %10d %10d %8d\n", "n (complete cases)", PUB_N, nrow(m), nrow(m)-PUB_N))
cat(sprintf("  %-22s %10.3f %10.3f %8.3f\n", "mean of item means", PUB_M, mean(pm), mean(pm)-PUB_M))
cat(sprintf("  %-22s %10.3f %10.3f %8.3f\n", "SD of person score", PUB_SD, sd(pm), sd(pm)-PUB_SD))
cat(sprintf("  %-22s %10.3f %10.3f %8.3f\n", "Cronbach alpha", PUB_A, alpha, alpha-PUB_A))
cat(sprintf("  rival reversed-anchor reading would give mean %.3f (published %.2f)\n",
            8 - mean(pm), PUB_M))
ok1 <- nrow(m) == PUB_N && abs(mean(pm)-PUB_M) < 0.01 && abs(sd(pm)-PUB_SD) < 0.01 &&
       abs(alpha-PUB_A) < 0.01

cat("\nCHECK 2 -- study's own SLTOTAL composite in the source workbook\n")
zip_path <- file.path(tempdir(), "medvedev_sl_supp.zip")
url <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5985772/supplementaryFiles"
ok <- tryCatch({ download.file(url, zip_path, quiet = TRUE, mode = "wb"); TRUE },
               error = function(e) FALSE)
ok2 <- NA
if (!ok) {
  cat("  could not fetch the supplement -- CHECK 2 skipped\n")
} else {
  xl <- grep("s001[.]xlsx$", unzip(zip_path, exdir = tempdir()), value = TRUE)[1]
  src <- as.data.frame(readxl::read_excel(xl))
  s <- rowSums(src[, paste0("SL", 1:5)])
  n  <- sum(!is.na(src$SLTOTAL))
  raw <- sum(abs(s - src$SLTOTAL) < 1e-9, na.rm = TRUE)
  rev <- sum(abs((40 - s) - src$SLTOTAL) < 1e-9, na.rm = TRUE)
  cat(sprintf("  SLTOTAL == SL1+..+SL5 (as stored):        %d / %d\n", raw, n))
  cat(sprintf("  SLTOTAL == 40 - (SL1+..+SL5) (reversed):  %d / %d\n", rev, n))
  ok2 <- raw == n
}

cat("\nCHECK 3 -- marker/structure diagnostics (corroborative, NOT gating)\n")
cat(sprintf("  %-6s %6s %6s %8s %8s\n", "item", "mean", "sd", "floor%", "r_it"))
for (j in 1:5) {
  r <- cor(m[, j], rowSums(m[, -j]))
  cat(sprintf("  sl_%-4d %6.2f %6.2f %8.1f %8.3f\n", j, mean(m[,j]), sd(m[,j]),
              100*mean(m[,j] == 1), r))
}
cat("  Expected of the SWLS: item 5 ('If I could live my life over, I would change\n")
cat("  almost nothing') is the least endorsed and most dispersed item, and the two\n")
cat("  past-oriented items 4 and 5 carry the weakest item-total correlations.\n")
cat("  This orders {1,2,3} against {4,5} and singles out 5; it says nothing about\n")
cat("  the order within either group.\n")

cat("\n", if (isTRUE(ok1) && !isFALSE(ok2)) "VERDICT: PASS\n" else "VERDICT: FAIL\n", sep="")

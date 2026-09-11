# verify_smpi_lorenzoluaces_2020_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: live item codes PHQ_1..PHQ_9 carry the canonical PHQ-9
# wording in the instrument's own numbering (PHQ_1 = "Little interest or
# pleasure in doing things" ... PHQ_9 = "Thoughts that you would be better off
# dead or of hurting yourself in some way"), and resp 0..3 = Not at all ..
# Nearly every day (raw).
#
# Derivation: data/smpi_lorenzoluaces.py keeps the OSF deposit's column names
# PHQ_1..PHQ_9 unchanged. The deposit ("SMPI data.csv", osf.io/69nwe) has bare
# headers and no labels, and the paper never prints a PHQ-9 item, so what PHQ_i
# MEANS rests on the instrument's printed order and is tested against content.
#
# The same 487 respondents answered the SMPI (whose 24 items ARE printed in the
# paper's Table 1, Scale A items 1-12 and Scale B items 1-12) and the SHAPS in
# the same file. Content twins:
#   PHQ_4 tired/little energy   <-> SMPIa_1 "I have very low energy and find it extremely hard to get out of bed..."
#   PHQ_8 moving/speaking slowly <-> SMPIa_6 "In walking and talking, I'm distinctly physically slowed..."
#   PHQ_7 trouble concentrating <-> SMPIa_7 "My concentration is distinctly affected and slowed."
#   PHQ_5 poor appetite/overeating <-> SMPIb_6 "I often get ... food cravings and/or increased appetite when I'm depressed."
#   PHQ_1 little interest/pleasure <-> SMPIa_4 "I completely lose interest in things..." and the SHAPS total
#         (anhedonia; stored here so that HIGHER = more pleasure, hence most NEGATIVE correlation)
# Weaker, non-twin legs:
#   PHQ_9 suicidal ideation: marker item -- least endorsed of the items not already
#         pinned as psychomotor (PHQ_8 is pinned by its twin above)
#   PHQ_3 sleep: of the three items left {PHQ_2, PHQ_3, PHQ_6}, the only one whose
#         strongest within-PHQ partner is the energy item PHQ_4 (sleep-fatigue somatic pair)
# Option axis: PHQ-9 raw total reproduces the paper (M 9.80, SD 6.40; PHQ-9 >= 10
# among completed-SMPI cases n = 216), and correlates with GAD-7 total at the
# paper's r = .73.
#
# WHAT THIS DOES NOT ESTABLISH: PHQ_2 ("Feeling down, depressed, or hopeless")
# and PHQ_6 ("Feeling bad about yourself ...") are NOT distinguished from each
# other -- they are each other's strongest correlate (r = .78) and no content
# twin in the file separates them. The SMPI legs also assume SMPIa_i/SMPIb_i
# follow the paper's Table 1 order (an assumption independent of PHQ order).
# The PHQ_9 and PHQ_3 legs are distributional/structural, not content twins.
# Status PARTIAL.

suppressMessages(library(irw))

TABLE <- "smpi_lorenzoluaces_2020_phq9"
SRC   <- "https://osf.io/download/ygzhj/"   # SMPI data.csv, osf.io/69nwe

p <- paste0("PHQ_", 1:9)

# --- live IRW data (4,377 rows; a deliberately accepted, trivially small export)
d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(w$id), c("id", p)]

# --- the study's deposit ------------------------------------------------------
tf <- tempfile(fileext = ".csv")
utils::download.file(SRC, tf, quiet = TRUE, mode = "wb")
x <- read.csv(tf, check.names = FALSE, fileEncoding = "UTF-8-BOM")
x$id <- seq_len(nrow(x))   # processing script: id = row number
src <- x
names(src)[match(p, names(src))] <- paste0("src_", p)

m <- merge(w, src, by = "id", all.y = TRUE)
cat(sprintf("merged n = %d respondents (live x deposit)\n\n", nrow(m)))

# --- P0: the live table is the deposit's PHQ_i columns ---------------------------
A <- as.matrix(m[, p]); B <- as.matrix(m[, paste0("src_", p)])
mism <- sum(xor(is.na(A), is.na(B))) + sum(A != B, na.rm = TRUE)
cat(sprintf("P0 cells where live PHQ_i != deposit PHQ_i (incl. NA pattern): %d of %d\n\n",
            mism, length(A)))

r <- function(a, b) cor(m[[a]], m[[b]], use = "pairwise.complete.obs")
twin <- function(other, label, expect, fn = which.max) {
    cc <- sapply(p, r, b = other)
    cat(sprintf("corr(PHQ_i, %s)  [%s]\n  %s\n", other, label,
                paste(sprintf("%s=%.3f", p, cc), collapse = " ")))
    top <- names(fn(cc))
    cat(sprintf("  -> selected: %s (predicted %s)\n\n", top, expect))
    top == expect
}

m$SHAPS_total <- m$SHAPS
p1 <- twin("SMPIa_1", "SMPI A1 very low energy", "PHQ_4")
p2 <- twin("SMPIa_6", "SMPI A6 physically slowed", "PHQ_8")
p3 <- twin("SMPIa_7", "SMPI A7 concentration affected", "PHQ_7")
p4 <- twin("SMPIb_6", "SMPI B6 food cravings / increased appetite", "PHQ_5")
p5a <- twin("SMPIa_4", "SMPI A4 completely lose interest", "PHQ_1")
p5b <- twin("SHAPS_total", "SHAPS total, higher = more pleasure; most NEGATIVE", "PHQ_1", which.min)

# --- P6: marker item ------------------------------------------------------------
mu <- sapply(p, function(i) mean(m[[i]], na.rm = TRUE))
z  <- sapply(p, function(i) mean(m[[i]] == 0, na.rm = TRUE))
cat("item mean / % at 0:\n")
for (i in p) cat(sprintf("  %-6s %5.3f  %5.1f%%\n", i, mu[i], 100 * z[i]))
rest <- setdiff(p, "PHQ_8")
low <- names(which.min(mu[rest]))
cat(sprintf("P6 least endorsed item other than psychomotor PHQ_8: %s (predicted PHQ_9); next lowest mean %.3f\n\n",
            low, sort(mu[rest])[2]))
p6 <- low == "PHQ_9"

# --- P7: sleep-fatigue somatic pair ----------------------------------------------
ic <- cor(m[, p], use = "pairwise.complete.obs"); diag(ic) <- NA
for (i in c("PHQ_2", "PHQ_3", "PHQ_6"))
    cat(sprintf("  strongest within-PHQ partner of %s: %s (r=%.2f)\n",
                i, names(which.max(ic[i, ])), max(ic[i, ], na.rm = TRUE)))
part <- sapply(c("PHQ_2", "PHQ_3", "PHQ_6"), function(i) names(which.max(ic[i, ])))
p7 <- part["PHQ_3"] == "PHQ_4" && part["PHQ_2"] != "PHQ_4" && part["PHQ_6"] != "PHQ_4"
cat(sprintf("P7 only PHQ_3 pairs most with energy item PHQ_4: %s\n\n", p7))

# --- P8: option axis -------------------------------------------------------------
tot <- rowSums(m[, p])
smpi_complete <- complete.cases(m[, grep("^SMPI", names(m))])
gsum <- rowSums(m[, paste0("gad", 1:7)])
n10 <- sum(tot >= 10 & smpi_complete, na.rm = TRUE)
rg <- cor(tot, gsum, use = "complete.obs")
cat(sprintf("PHQ-9 total (complete n=%d): mean %.2f SD %.2f  (paper: 9.80, SD 6.40)\n",
            sum(!is.na(tot)), mean(tot, na.rm = TRUE), sd(tot, na.rm = TRUE)))
cat(sprintf("PHQ-9 >= 10 among completed-SMPI cases: %d  (paper: n = 216)\n", n10))
cat(sprintf("corr(PHQ-9 total, GAD-7 total) = %.3f  (paper: r = .73)\n\n", rg))
p8 <- abs(mean(tot, na.rm = TRUE) - 9.80) < 0.01 && abs(sd(tot, na.rm = TRUE) - 6.40) < 0.01 &&
      n10 == 216 && abs(rg - 0.73) < 0.02

cat(sprintf("PHQ_2-PHQ_6 r = %.2f (NOT separated by any route here)\n\n", ic["PHQ_2", "PHQ_6"]))

ok <- c(P0 = mism == 0, P1 = p1, P2 = p2, P3 = p3, P4 = p4, P5 = p5a && p5b,
        P6 = p6, P7 = unname(p7), P8 = p8)
for (k in names(ok)) cat(sprintf("%s: %s\n", k, if (ok[k]) "PASS" else "FAIL"))
cat("\nScope: pins PHQ_1, PHQ_4, PHQ_5, PHQ_7, PHQ_8 (content twins), PHQ_9 (marker),\n",
    "PHQ_3 (somatic pairing) and the option direction. PHQ_2 and PHQ_6 are NOT\n",
    "distinguished from each other -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

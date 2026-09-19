# verify_uti_newlands_2023_phq.R -- Step 5b mapping check (copied from references/verify_template.R).
#
# Claim: IRW items phq_1..phq_9 are PHQ-9 items 1..9 in the canonical form's printed
# order, scored 0 = "Not at all" .. 3 = "Nearly every day". data/uti_newlands_2023.py
# derives item = "phq_" + suffix of the source column phq{wave}_{n}, so phq_n is source
# column phq1_n / phq2_n (number-preserving). The source columns carry NO labels (the
# OSF "Pilot Data Codebook.xlsx" names the PHQ-9 block but lists no PHQ items), so the
# column-number -> PHQ-9-item-number tie is what is tested here.
#
# Data: the study's own OSF file (osf.io/uh8qm), which the IRW table is built from;
# baseline = phq1_* columns (n=240), matching the paper's Online Resource 11 sample.
# The live table is used only for its per-item n (irw_table_sets, no export).

suppressMessages(library(irw))
TABLE <- "uti_newlands_2023_phq"
ok <- TRUE

tf <- tempfile(fileext = ".csv")
download.file("https://osf.io/download/uh8qm/", tf, quiet = TRUE, mode = "wb")
d <- read.csv(tf, na.strings = c(" ", "", "NA", "nan"))
b <- d[, paste0("phq1_", 1:9)]
r2 <- d[, paste0("phq2_", 1:9)]

# 0. raw file -> live table: per-item n must equal baseline + retest non-missing
s <- irw::irw_table_sets(TABLE, per_item = TRUE)
pi <- as.data.frame(s$per_item)
raw_n <- colSums(!is.na(b)) + colSums(!is.na(r2))
live_n <- setNames(pi$n, pi$item)[paste0("phq_", 1:9)]
cat("per-item n raw (base+retest) vs live:\n"); print(rbind(raw = unname(raw_n), live = unname(live_n)))
if (!all(raw_n == live_n)) { cat("FAIL: raw file does not reproduce live per-item n\n"); ok <- FALSE }

# 1. route 3: published PHQ-9 total, Online Resource 11: n=240, M=11.5, SD=7.22, range 0-27
tot <- rowSums(b)
cat(sprintf("\n[route 3] baseline total: n=%d mean=%.3f sd=%.3f range=%d-%d  (published 240 / 11.5 / 7.22 / 0-27)\n",
            sum(!is.na(tot)), mean(tot, na.rm = TRUE), sd(tot, na.rm = TRUE), min(tot, na.rm = TRUE), max(tot, na.rm = TRUE)))
cat(sprintf("          reversed-anchor counterfactual mean=%.3f\n", mean(rowSums(3 - b), na.rm = TRUE)))
if (abs(mean(tot, na.rm = TRUE) - 11.5) > 0.05 || abs(sd(tot, na.rm = TRUE) - 7.22) > 0.05) ok <- FALSE

# 2. convergent content correlations (Spearman) with the study's own RUTIIQ items,
#    whose wording is in the codebook: a2 "low mood or depression", a3 "hopeless about the
#    future", a4 "poor or disrupted sleep"; and GAD-7 item 5 "restless that it is hard to sit still".
cs <- function(v) round(sapply(1:9, function(i) cor(b[[i]], v, use = "pairwise", method = "spearman")), 2)
ca2 <- cs(d$rutiiq1_a2); ca3 <- cs(d$rutiiq1_a3); ca4 <- cs(d$rutiiq1_a4); cg5 <- cs(d$gad1_5)
tab <- rbind(mean = round(colMeans(b, na.rm = TRUE), 3), pct0 = round(colMeans(b == 0, na.rm = TRUE) * 100, 1),
             r_a2_lowmood = ca2, r_a3_hopeless = ca3, r_a4_sleep = ca4, r_gad5_restless = cg5)
colnames(tab) <- paste0("phq_", 1:9); cat("\n"); print(tab)

chk <- function(label, cond) { cat(sprintf("  %-70s %s\n", label, if (cond) "OK" else "FAIL")); if (!cond) ok <<- FALSE }
cat("\nPredictions from canonical PHQ-9 content:\n")
chk("phq_3 (sleep) is the PHQ item most correlated with RUTIIQ a4 (sleep)", which.max(ca4) == 3)
chk("phq_2 (down/depressed/hopeless) is the item most correlated with a2 (low mood)", which.max(ca2) == 2)
chk("phq_2 is the item most correlated with a3 (hopeless)", which.max(ca3) == 2)
chk("phq_4 (tired/little energy) has the highest item mean", which.max(tab["mean", ]) == 4)
chk("phq_8 and phq_9 are the two least-endorsed items", all(sort(order(tab["mean", ])[1:2]) == c(8, 9)))
chk("phq_9 (thoughts of death) > phq_8 on r with a3 hopeless", ca3[9] > ca3[8])
chk("phq_8 (psychomotor/restless) > phq_9 on r with GAD-7 item 5 restless", cg5[8] > cg5[9])

cat("\nNot established: the order among phq_1, phq_5, phq_6, phq_7 (no item-specific external\n",
    "criterion or per-item published statistic separates them); phq_1 vs phq_2 rests on a\n",
    "0.06 margin in r with a2 and 0.07 with a3. Status is therefore PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

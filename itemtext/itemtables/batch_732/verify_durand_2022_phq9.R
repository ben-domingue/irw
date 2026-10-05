# verify_durand_2022_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes PHQ_1..PHQ_9 carry the canonical PHQ-9
# wording in the form's printed numbering (PHQ_1 = "Little interest or pleasure
# in doing things" ... PHQ_9 = "Thoughts that you would be better off dead or of
# hurting yourself in some way"), and resp 0/1/2/3 = Not at all / Several days /
# More than half the days / Nearly every day, ascending.
#
# Neither the paper (Durand & Arbone 2022, PeerJ 10.7717/peerj.12836) nor its
# SPSS deposit (peerj-10-12836-s001.sav) ties the columns to text: PHQ_1..PHQ_9
# carry no variable labels and no value labels. The paper cites Kroenke et al.
# 2001 and states the 0 = not at all .. 3 = nearly every day scale. So the tie
# rests on the column numbering matching the form's printed numbering, and is
# tested here against content.
#
# The live table is built by melting the deposit's PHQ_1..PHQ_9 columns by name
# (data/durand_2022_phq9_stai6.py), so the deposit's own ASRS/total columns can
# be used as external criteria once P0 shows the live codes and the deposit
# columns are the same variables.
#
# Predictions:
#   P0  LINK. For every code, the live 0/1/2/3 counts equal the deposit column's
#       counts cell for cell, and the nine count vectors are pairwise distinct
#       (so no two codes could be swapped undetected by this check).
#   P1  MARKER ITEM (route 7). Item 9 (suicidal ideation) has the highest share
#       of zero responses of the nine. (Its MEAN ties item 8's, 0.629 vs 0.631,
#       so the mean alone does not pin it -- %zero is the tie-breaker.)
#   P2  Item 4 (tired / little energy) has the highest mean.
#   P3  Item 7 (trouble concentrating) correlates most, of the nine, with the
#       deposit's ASRS inattention subscale total -- a cross-instrument anchor.
#   P4  Item 8 (slowed or fidgety/restless) correlates most, of the nine, with
#       the deposit's ASRS hyperactivity-impulsivity subscale total.
#   P5  Items 1 and 2 (anhedonia, depressed mood -- the PHQ-2 core) are the
#       most strongly intercorrelated pair of all 36.
#   P6  Two-factor blocks (route 5): mean within-block r exceeds cross-block r
#       for somatic {3,4,5} and cognitive/affective {2,6,7,8,9}.
#   P7  RESPONSE AXIS. Row-sum totals by ADHD diagnosis reproduce the paper's
#       Table 1 (ADHD 12.18 (6.28), n=201; no ADHD 11.09 (6.83), n=206) and the
#       deposit's PHQ_Diagnosis equals total >= 15 (paper: 63+74 = 137 high).
#       A reversed 0..3 axis would put the means near 27 - 11.6 = 15.4.
#
# NOT ESTABLISHED: PHQ_1 vs PHQ_2 (pinned as a pair, not individually), PHQ_3
# vs PHQ_5 (pinned as somatic, not separated from each other), PHQ_6 vs PHQ_2
# beyond block membership. Individually pinned: PHQ_4, PHQ_7, PHQ_8, PHQ_9.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "durand_2022_phq9"
IT <- paste0("PHQ_", 1:9)
ZIP <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8784014/supplementaryFiles"

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w)); w <- w[, IT]
cat(sprintf("live table: %d respondents x %d items\n\n", nrow(w), ncol(w)))

tz <- tempfile(fileext = ".zip"); utils::download.file(ZIP, tz, quiet = TRUE, mode = "wb")
td <- tempfile(); utils::unzip(tz, files = "peerj-10-12836-s001.sav", exdir = td)
sav <- as.data.frame(haven::read_sav(file.path(td, "peerj-10-12836-s001.sav")))
P <- sapply(IT, function(i) as.numeric(sav[[i]]))

# P0
cnt_live <- t(sapply(IT, function(i) table(factor(w[[i]], 0:3))))
cnt_dep  <- t(sapply(IT, function(i) table(factor(P[, i], 0:3))))
cat("per-code counts of resp 0/1/2/3 (live | deposit)\n")
for (i in IT) cat(sprintf("  %-6s %s | %s\n", i, paste(cnt_live[i, ], collapse = "/"),
                          paste(cnt_dep[i, ], collapse = "/")))
p0 <- identical(unname(cnt_live), unname(cnt_dep)) &&
      !any(duplicated(apply(cnt_live, 1, paste, collapse = "/")))

mu <- colMeans(w); pz <- 100 * colMeans(w == 0)
cat("\nper-item mean and %zero (live)\n")
for (i in IT) cat(sprintf("  %-6s mean %.3f  %%zero %4.1f\n", i, mu[i], pz[i]))
p1 <- names(which.max(pz)) == "PHQ_9"
p2 <- names(which.max(mu)) == "PHQ_4"
cat(sprintf("  -> highest %%zero %s (pred PHQ_9); highest mean %s (pred PHQ_4)\n\n",
            names(which.max(pz)), names(which.max(mu))))

ri <- cor(P, as.numeric(sav$ASRS_inattention))[, 1]
rh <- cor(P, as.numeric(sav$ASRS_hyperimpuls))[, 1]
cat("r with deposit ASRS subscale totals (inattention | hyperactivity-impulsivity)\n")
for (i in IT) cat(sprintf("  %-6s %.3f | %.3f\n", i, ri[i], rh[i]))
p3 <- names(which.max(ri)) == "PHQ_7"; p4 <- names(which.max(rh)) == "PHQ_8"
cat(sprintf("  -> max inattention %s (pred PHQ_7); max hyperactivity %s (pred PHQ_8)\n\n",
            names(which.max(ri)), names(which.max(rh))))

R <- cor(w); R2 <- R; R2[lower.tri(R2, diag = TRUE)] <- NA
top <- which(R2 == max(R2, na.rm = TRUE), arr.ind = TRUE)
pair <- sort(c(rownames(R)[top[1, 1]], colnames(R)[top[1, 2]]))
cat(sprintf("highest inter-item r: %s-%s = %.3f (pred PHQ_1-PHQ_2)\n",
            pair[1], pair[2], max(R2, na.rm = TRUE)))
p5 <- identical(pair, c("PHQ_1", "PHQ_2"))

SOM <- paste0("PHQ_", 3:5); COG <- paste0("PHQ_", c(2, 6, 7, 8, 9))
wi <- function(g) mean(R[g, g][upper.tri(R[g, g])])
ws <- wi(SOM); wc <- wi(COG); cr <- mean(R[SOM, COG])
cat(sprintf("blocks: within somatic %.3f, within cognitive %.3f, across %.3f\n\n", ws, wc, cr))
p6 <- ws > cr && wc > cr

tot <- rowSums(P); g <- as.numeric(sav$ADHDdiagnosis)  # 1 = yes, 2 = no
m1 <- mean(tot[g == 1]); s1 <- sd(tot[g == 1]); m2 <- mean(tot[g == 2]); s2 <- sd(tot[g == 2])
cat(sprintf("total, ADHD dx:    %.2f (%.2f) n=%d   paper 12.18 (6.28) n=201\n", m1, s1, sum(g == 1)))
cat(sprintf("total, no ADHD dx: %.2f (%.2f) n=%d   paper 11.09 (6.83) n=206\n", m2, s2, sum(g == 2)))
dx <- as.numeric(sav$PHQ_Diagnosis)
cat(sprintf("PHQ_Diagnosis == (total >= 15) on %d/%d rows; high n = %d (paper 137)\n\n",
            sum(dx == (tot >= 15)), length(tot), sum(dx == 1)))
p7 <- abs(m1 - 12.18) < 0.01 && abs(s1 - 6.28) < 0.01 && abs(m2 - 11.09) < 0.01 &&
      abs(s2 - 6.83) < 0.01 && all(dx == (tot >= 15)) && sum(dx == 1) == 137

ok <- c(P0 = p0, P1 = p1, P2 = p2, P3 = p3, P4 = p4, P5 = p5, P6 = p6, P7 = p7)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins PHQ_4, PHQ_7, PHQ_8, PHQ_9 individually, {PHQ_1,PHQ_2} as a pair,\n",
    "{PHQ_3,PHQ_5} as somatic and PHQ_6 as cognitive; does NOT separate PHQ_1 from\n",
    "PHQ_2 or PHQ_3 from PHQ_5 -- PARTIAL.\n", sep = "")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_qin_2025_behavioral_intention.R
#
# CLAIM: BI1/BI2/BI3 in the live IRW table carry the three behavioural-intention
# item texts that S1 Table of PLOS ONE 10.1371/journal.pone.0336220 prints against
# exactly those codes.
#
# Two independent links are checked, neither of which is a count check:
#
#  (A) code -> column. The live table is joined to the study's own S1 Data CSV
#      (10.1371/journal.pone.0336220.s002) on id == "No.", and each live item's
#      responses are compared to the source column of the same name, respondent by
#      respondent. If the processing script had permuted the three codes this is
#      where it breaks. The cross-code comparisons are printed too, so the reader
#      can see the wrong pairings do NOT match.
#
#  (B) column -> paper code. The paper's Table 7 cross-loading matrix gives, for
#      each of BI1/BI2/BI3, its loading on the CI, PCD, RCTE and SA constructs.
#      Those 12 cells are recomputed from the source CSV as correlations of the
#      raw item with each construct's mean, and compared to the published values.
#      This is what ties the paper's OWN codes (hence its S1 Table item texts) to
#      the columns of the deposited data. The BI2/BI3 swap is scored explicitly.

suppressMessages(library(irw))

TABLE <- "qin_2025_behavioral_intention"
SRC   <- "https://doi.org/10.1371/journal.pone.0336220.s002"

# Paper Table 7 (Discriminant Validity, Cross-Loading Analysis), BI rows.
#                     CI     PCD    RCTE     SA
PUB <- rbind(BI1 = c(0.728, 0.258, 0.764, 0.821),
             BI2 = c(0.680, 0.242, 0.687, 0.765),
             BI3 = c(0.688, 0.235, 0.703, 0.781))
colnames(PUB) <- c("CI", "PCD", "RCTE", "SA")

d <- irw::irw_fetch(TABLE)
s <- read.csv(SRC, check.names = FALSE)

## ---- (A) live item code vs source column, per respondent ------------------
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
m <- merge(w, s, by.x = "id", by.y = "No.")
cat(sprintf("joined respondents: %d (live ids x S1 Data 'No.')\n\n", nrow(m)))

cat("(A) per-respondent agreement, live item x source column (% of 547):\n")
cat(sprintf("%-6s %8s %8s %8s\n", "live", "BI1", "BI2", "BI3"))
agree <- matrix(NA_real_, 3, 3, dimnames = list(paste0("BI", 1:3), paste0("BI", 1:3)))
for (i in paste0("BI", 1:3)) {
    for (j in paste0("BI", 1:3))
        agree[i, j] <- 100 * mean(m[[paste0(i, ".x")]] == m[[paste0(j, ".y")]])
    cat(sprintf("%-6s %7.1f%% %7.1f%% %7.1f%%\n", i, agree[i, 1], agree[i, 2], agree[i, 3]))
}
diag_ok <- all(abs(diag(agree) - 100) < 1e-9)
offdiag_max <- max(agree[row(agree) != col(agree)])
cat(sprintf("\ndiagonal all 100%%: %s ; largest off-diagonal: %.1f%%\n\n",
            diag_ok, offdiag_max))

## ---- (B) recomputed cross-loadings vs paper Table 7 ------------------------
cons <- list(CI = paste0("CI", 1:3), PCD = paste0("PCD", 1:3),
             RCTE = paste0("RCTE", 1:5), SA = paste0("SA", 1:3))
comp <- sapply(cons, function(cc) rowMeans(s[, cc]))
obs <- t(sapply(paste0("BI", 1:3), function(i)
    sapply(colnames(PUB), function(k) cor(s[[i]], comp[, k]))))

cat("(B) paper Table 7 cross-loadings vs correlations recomputed from S1 Data:\n")
cat(sprintf("%-5s %-6s %10s %10s %8s\n", "item", "constr", "published", "observed", "diff"))
for (i in rownames(PUB)) for (k in colnames(PUB))
    cat(sprintf("%-5s %-6s %10.3f %10.3f %8.3f\n", i, k, PUB[i, k], obs[i, k],
                obs[i, k] - PUB[i, k]))
resid <- max(abs(obs - PUB))
cat(sprintf("\nlargest residual as mapped: %.4f\n", resid))

# Would swapping BI2 and BI3 fit as well? (BI1 is separated by wide margins.)
sw <- obs[c("BI1", "BI3", "BI2"), ]; rownames(sw) <- rownames(obs)
cat(sprintf("largest residual if BI2/BI3 were swapped: %.4f (%.1fx worse)\n",
            max(abs(sw - PUB)), max(abs(sw - PUB)) / resid))
cat(sprintf("BI2-vs-BI3 published gaps: CI %.3f, PCD %.3f, RCTE %.3f, SA %.3f -- ",
            PUB["BI3","CI"]-PUB["BI2","CI"], PUB["BI3","PCD"]-PUB["BI2","PCD"],
            PUB["BI3","RCTE"]-PUB["BI2","RCTE"], PUB["BI3","SA"]-PUB["BI2","SA"]))
cat(sprintf("all 4 signs reproduced: %s\n",
            all(sign(obs["BI3",] - obs["BI2",]) == sign(PUB["BI3",] - PUB["BI2",]))))

cat("\nWhat this does NOT establish: nothing here reads the item WORDING -- it ties\n",
    "each live code to a source column and to the paper's own code. The wording comes\n",
    "from S1 Table, which prints 'BI1'..'BI3' beside the three sentences; the check\n",
    "above is what rules out the codes having been permuted between paper and deposit.\n",
    "The BI2/BI3 separation rests on gaps of 0.008-0.016, small in absolute terms\n",
    "though several times the residual.\n", sep = "")

ok <- diag_ok && offdiag_max < 100 && resid <= 0.01 &&
      all(sign(obs["BI3", ] - obs["BI2", ]) == sign(PUB["BI3", ] - PUB["BI2", ]))
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

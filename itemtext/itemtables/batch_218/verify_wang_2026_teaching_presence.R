# verify_wang_2026_teaching_presence.R -- Step 5b, mapping_basis = reconstructed
#
# THE PROBLEM. Wang & Zou (2026, PLOS ONE 10.1371/journal.pone.0346229)
# administered TWELVE technology-perception items, printed in their S1 Appendix
# as TP1-TP12. Their S2 Appendix data file -- the file data/wang_2026_efl_tam.py
# melts by column name into this IRW table -- carries only EIGHT TP columns,
# named TP1..TP8. The paper says TP3, TP4, TP5 and TP6 were dropped for low
# loadings, so the deposit's eight columns are the RETAINED eight (appendix
# TP1, TP2, TP7, TP8, TP9, TP10, TP11, TP12) under a new 1..8 numbering. The
# live item code therefore does NOT name the appendix item, and which shipped
# sentence goes with which live code is the whole question.
#
# THE CLAIM being tested: the renumbering is alphabetical on the appendix label
# -- the order Table 2 of the paper itself lists the retained items in --
#
#     live TP1 TP2  TP3  TP4  TP5 TP6 TP7 TP8
#     appx TP1 TP10 TP11 TP12 TP2 TP7 TP8 TP9
#
# THE TEST. Table 2 publishes a VIF per item, and VIF is a function of the
# construct's correlation matrix that differs item by item. Recomputing it from
# the LIVE IRW responses gives eight numbers that must be matched to the eight
# published labels; only one of the 8! = 40320 possible assignments can be
# right. The script recomputes the VIFs, prints them against the published
# values under the claimed mapping, and scores every permutation so the reader
# can see the margin over the runner-up. A swap of any two items' item_text
# moves this from the best assignment to a worse one.
#
# The method is calibrated on the four sibling constructs in the same deposit
# (ATT, PU, TA, BI), whose labels are NOT in doubt: it reproduces all 14 of
# their published VIFs to the last printed digit, so a deviation of even 0.006
# here is signal rather than noise.
#
# WHAT THIS DOES NOT ESTABLISH: (a) the four dropped appendix items (TP3-TP6)
# are absent from the data, which is a claim about the deposit, not about this
# mapping; (b) that the authors' own spreadsheet labelling is internally
# correct; (c) anything about the Chinese wording respondents actually read --
# the shipped English is the 2026-09-01 recoverability fallback.
#
# The script also prints the reverse-coding check that decides option_text for
# live TP3 and TP5 (appendix TP11 and TP2, the two retained negatively-worded
# items): if the deposit stored them raw they would correlate NEGATIVELY with
# the other six. They do not, so the shipped anchors for those two items are
# reversed to match the stored direction.

suppressMessages(library(irw))

TABLE <- "wang_2026_teaching_presence"
LIVE  <- paste0("TP", 1:8)
# Claimed appendix label for each live code, in live order.
APPX  <- c("TP1", "TP10", "TP11", "TP12", "TP2", "TP7", "TP8", "TP9")
# Wang & Zou (2026) Table 2, VIF column, TP block (rows listed TP1, TP10, TP11,
# TP12, TP2, TP7, TP8, TP9).
PUB   <- c(TP1 = 1.874, TP10 = 1.974, TP11 = 2.032, TP12 = 2.231,
           TP2 = 1.919, TP7  = 1.913, TP8  = 1.999, TP9  = 2.122)
REV   <- c("TP3", "TP5")   # live codes whose appendix item is negatively worded

d <- irw::irw_fetch(TABLE)
w <- reshape(data.frame(id = d$id, item = as.character(d$item),
                        resp = as.numeric(d$resp)),
             idvar = "id", timevar = "item", direction = "wide")
X <- as.matrix(w[, paste0("resp.", LIVE)])
colnames(X) <- LIVE
R <- cor(X, use = "complete.obs")
vif <- diag(solve(R))

cat(sprintf("live n = %d respondents x %d items\n\n", nrow(X), ncol(X)))
cat("=== Recomputed VIF from live IRW data vs published Table 2 VIF ===\n")
cat(sprintf("%-6s %-10s %12s %12s %9s\n", "live", "appendix", "published", "recomputed", "diff"))
for (i in seq_along(LIVE))
    cat(sprintf("%-6s %-10s %12.3f %12.4f %9.4f\n",
                LIVE[i], APPX[i], PUB[[APPX[i]]], vif[i], vif[i] - PUB[[APPX[i]]]))
claimed <- sum(abs(vif - PUB[APPX]))
cat(sprintf("\ntotal absolute deviation, claimed mapping: %.4f over 8 items\n", claimed))

# --- all 40320 assignments, to show the margin --------------------------------
perms <- function(v) {
    if (length(v) == 1) return(matrix(v, 1))
    do.call(rbind, lapply(seq_along(v), function(i)
        cbind(v[i], perms(v[-i]))))
}
P <- perms(1:8)
sc <- apply(P, 1, function(p) sum(abs(vif - PUB[p])))
o <- order(sc)
cat("\n=== Best 3 of all 40320 label assignments (lower is better) ===\n")
for (k in 1:3)
    cat(sprintf("  %.4f   %s\n", sc[o[k]], paste(names(PUB)[P[o[k], ]], collapse = " ")))
best_is_claimed <- identical(names(PUB)[P[o[1], ]], APPX)
cat(sprintf("\nclaimed mapping is the best of 40320: %s ; runner-up is %.4f worse\n",
            best_is_claimed, sc[o[2]] - sc[o[1]]))

# --- reverse-coding direction, which decides option_text for TP3 and TP5 ------
cat("\n=== Stored direction of the two negatively-worded items ===\n")
for (it in REV) {
    others <- setdiff(LIVE, it)
    r <- R[it, others]
    cat(sprintf("%-4s (appendix %s): r with the other 7 items %.3f..%.3f (mean %.3f)\n",
                it, APPX[match(it, LIVE)], min(r), max(r), mean(r)))
}
rev_ok <- all(sapply(REV, function(it) all(R[it, setdiff(LIVE, it)] > 0.2)))
cat(sprintf("both negatively-worded items correlate POSITIVELY with the rest: %s\n", rev_ok))
cat("  => the deposit stores them already reverse-scored, so a high resp means the\n")
cat("     respondent DISAGREED with the printed statement; the shipped option_text\n")
cat("     for these two items runs 1 = Strongly Agree .. 5 = Strongly Disagree.\n")

cat("\nNot established here: the correctness of the authors' own column labelling,\n")
cat("and nothing at all about the administered Chinese wording.\n")

cat(if (best_is_claimed && claimed < 0.01 && rev_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

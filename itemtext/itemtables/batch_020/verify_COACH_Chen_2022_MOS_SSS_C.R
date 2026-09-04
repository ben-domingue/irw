# verify_COACH_Chen_2022_MOS_SSS_C.R -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST. The shipped item_text assigns ra_mos_sss_c_qN the text that
# Sherbourne & Stewart (1991, Soc Sci Med 32:705-714) APPENDIX prints at
# questionnaire number N (N = 2..20; question 1 is the structural "how many close
# friends" item and is not in this table).
#
# This DELIBERATELY CONTRADICTS the study's own codebook. The deposit's
# 'COACH_Code Book_Final_version.xlsx' labels RA_MOS_SSS_C_Q2..Q20 with the same
# 19 sentences but in RAND's subscale-GROUPED web ordering (8 emotional/
# informational, then 4 tangible, then 3 affectionate, then 4 positive social
# interaction), i.e. contiguous blocks. The canonical questionnaire interleaves
# them. The two hypotheses are therefore a permutation of each other and the data
# can choose between them:
#
#   canonical (shipped) : TANG = q2,q5,q12,q15  AFF = q6,q10,q20
#                         PSI  = q7,q11,q14,q18 EI = q3,q4,q8,q9,q13,q16,q17,q19
#   codebook order      : EI = q2..q9  TANG = q10..q13  AFF = q14..q16  PSI = q17..q20
#
# Two independent predictions are checked, both on wave 1 (n = 2363):
#   (A) within-minus-between mean correlation gap is larger under the shipped
#       grouping than under the codebook grouping, and larger than a random
#       4-block partition of the same sizes;
#   (B) the four highest-mean items are exactly the four TANGIBLE items -- the
#       illness-contingent instrumental items (bed / doctor / meals / chores),
#       which are the most-available kind of support in this rural Chinese
#       older-adult sample.
#
# WHAT THIS DOES NOT ESTABLISH: it pins each item's SUBSCALE, not its position
# within its subscale. Which of q2/q5/q12/q15 is "confined to bed" vs "doctor"
# vs "meals" vs "chores" rests on the 1991 appendix numbering alone. Hence
# status PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "COACH_Chen_2022_MOS_SSS_C"
ITEMS <- paste0("ra_mos_sss_c_q", 2:20)

SHIPPED  <- c(q2="TANG", q3="EI", q4="EI", q5="TANG", q6="AFF", q7="PSI",
              q8="EI", q9="EI", q10="AFF", q11="PSI", q12="TANG", q13="EI",
              q14="PSI", q15="TANG", q16="EI", q17="EI", q18="PSI", q19="EI",
              q20="AFF")
CODEBOOK <- c(rep("EI", 8), rep("TANG", 4), rep("AFF", 3), rep("PSI", 4))
names(CODEBOOK) <- names(SHIPPED)
TANG <- paste0("ra_mos_sss_c_", names(SHIPPED)[SHIPPED == "TANG"])

d <- irw::irw_fetch(TABLE)
d <- d[d$wave == 1, ]
ids <- sort(unique(d$id))
m <- matrix(NA_real_, length(ids), length(ITEMS), dimnames = list(ids, ITEMS))
m[cbind(match(d$id, ids), match(d$item, ITEMS))] <- as.numeric(d$resp)
cat(sprintf("wave-1 respondents: %d\n\n", nrow(m)))

mu <- colMeans(m, na.rm = TRUE)
cat("per-item means (wave 1), shipped subscale in brackets:\n")
for (it in ITEMS)
    cat(sprintf("  %-18s %.3f  [%s]\n", it, mu[it], SHIPPED[sub("^ra_mos_sss_c_", "", it)]))

top4 <- names(sort(mu, decreasing = TRUE))[1:4]
okB  <- setequal(top4, TANG)
cat(sprintf("\n(B) four highest-mean items: %s\n", paste(sort(top4), collapse = ", ")))
cat(sprintf("    shipped TANGIBLE block  : %s  -> %s\n",
            paste(sort(TANG), collapse = ", "), if (okB) "MATCH" else "MISMATCH"))

cm <- cor(m, use = "pairwise.complete.obs")
gap <- function(g) {
    win <- bet <- numeric(0)
    for (i in 1:(length(ITEMS) - 1)) for (j in (i + 1):length(ITEMS))
        if (g[i] == g[j]) win <- c(win, cm[i, j]) else bet <- c(bet, cm[i, j])
    c(within = mean(win), between = mean(bet), gap = mean(win) - mean(bet))
}
gs <- gap(SHIPPED); gc_ <- gap(CODEBOOK)
set.seed(1)
null <- replicate(2000, {
    p <- sample(2:20); g <- character(19); names(g) <- names(SHIPPED)
    k <- 1
    for (z in seq_along(c(8, 4, 3, 4))) {
        n <- c(8, 4, 3, 4)[z]
        g[paste0("q", p[k:(k + n - 1)])] <- c("EI", "TANG", "AFF", "PSI")[z]; k <- k + n
    }
    gap(g[names(SHIPPED)])["gap"]
})

cat(sprintf("\n(A) within/between mean correlation, wave 1\n"))
cat(sprintf("    shipped (canonical 1991 numbering): within %.4f  between %.4f  gap %.4f\n",
            gs[1], gs[2], gs[3]))
cat(sprintf("    codebook (subscale-grouped)       : within %.4f  between %.4f  gap %.4f\n",
            gc_[1], gc_[2], gc_[3]))
cat(sprintf("    random 4-block partitions (2000)  : mean %.4f  sd %.4f  max %.4f\n",
            mean(null), sd(null), max(null)))
okA <- gs[3] > gc_[3] && gs[3] > max(null)

cat("\nNOT established by either route: the order of items WITHIN a subscale.\n")
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

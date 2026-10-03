# verify_meco_l1_comprehension.R -- Step 5b check for meco_l1_comprehension (batch_737).
#
# CLAIM UNDER TEST. Item codes are {version}_text{t}_q{q} / text{t}_q{q}, where t and q
# are the release's trialid/number and QUESTIONNUM (data/meco_l1_comprehension.py). The
# wording and yes/no key were taken from the study's comp-questions.xlsx, whose sheets
# are keyed by the same text number (column `number`) and question column q1..q4. So the
# mapping rests on QUESTIONNUM k == sheet column qk. What would break if it were wrong:
#   (1) QUESTIONNUM must index the same translated question in every wave-1 site: per-
#       question accuracy on the 20 shared matched-text items should correlate strongly
#       across the 13 sites, far above a within-text shuffle of q.
#   (2) [tried and dropped -- see below]
#   (3) Marker: the Norwegian sheet's text-6 q4 is a duplicate of q3 with a different key
#       and the readme says Norwegian wave 1 had 47 questions; the data must lack exactly
#       QUESTIONNUM 4 of text 6 for wave-1 Norwegian readers.
#   (4) Marker: the Spanish sheet's text-3 q3 repeats q4's wording; Spanish accuracy on
#       sp_text3_q3 should sit with Spanish text3_q4, not with text3_q3 elsewhere.
# WHAT THIS DOES NOT ESTABLISH: it does not pin each item's wording individually from
# data (a permutation of q common to every sheet would pass (1); markers (3) and (4) pin
# only two cells);
# it says nothing about the 317 wave-2-only items, which ship with no item_text; and it
# cannot test the processing script's assumption that wave-2 sites reusing a wave-1
# text (no, tr, en_uk, German text 8) also reused its questions.

suppressMessages(library(irw))
TABLE <- "meco_l1_comprehension"
here <- {
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grep("^--file=", a)])
    if (length(f)) dirname(normalizePath(f[1])) else "."
}
it <- read.csv(file.path(here, "meco_l1_comprehension__items.csv"), stringsAsFactors = FALSE)
d <- irw::irw_fetch(TABLE)
ok <- TRUE
set.seed(737)

# (1) cross-site consistency on shared matched-text items, wave 1
w1 <- d[d$cov_sample == 1 & grepl("^text", d$item), ]
P <- tapply(w1$resp, list(w1$item, w1$cov_site), mean)
txt <- sub("_q\\d$", "", rownames(P))
loo <- function(P) sapply(colnames(P), function(s) {
    o <- rowMeans(P[, colnames(P) != s, drop = FALSE], na.rm = TRUE)
    x <- P[, s]; k <- !is.na(x); cor(x[k], o[k]) })
r_obs <- loo(P)
null <- replicate(300, {
    Q <- P
    for (s in colnames(Q)) Q[, s] <- ave(Q[, s], txt, FUN = function(v) v[sample.int(length(v))])
    median(loo(Q)) })
cat("(1) leave-one-site-out r, 20 shared items, wave-1 sites:\n")
print(round(r_obs, 3))
cat(sprintf("    median r = %.3f; within-text shuffle null: mean %.3f, max %.3f (300 draws)\n",
            median(r_obs), mean(null), max(null)))
if (!(median(r_obs) > 0.6 && median(r_obs) > max(null))) ok <- FALSE

# (2) dropped: a yes-key vs no-key accuracy test was tried and is uninformative at the
#     item level (diff 0.018 vs within-section shuffle null mean 0.019, p = 0.53), so it
#     is not used as evidence either way.

# (3) Norwegian text 6 q4 marker
no1 <- d[d$cov_sample == 1 & d$cov_site == "no" & grepl("^no_text6_", d$item), ]
n_by_q <- table(factor(no1$item, levels = paste0("no_text6_q", 1:4)))
cat("\n(3) wave-1 Norwegian respondents per text-6 question:\n"); print(n_by_q)
t6q4_text <- unique(it$item_text[it$item == "no_text6_q4"])
cat(sprintf("    shipped item_text for no_text6_q4: %s\n", paste(t6q4_text, collapse = "|")))
if (!(n_by_q[["no_text6_q4"]] == 0 && all(n_by_q[1:3] > 0) && all(is.na(t6q4_text) | t6q4_text == ""))) ok <- FALSE

# (4) Spanish text 3 q3 duplicate marker
sp <- d[d$cov_site == "sp", ]
a_sp_q3 <- mean(sp$resp[sp$item == "sp_text3_q3"]); a_sp_q4 <- mean(sp$resp[sp$item == "text3_q4"])
oth <- d[d$cov_sample == 1 & d$cov_site != "sp" & d$item == "text3_q3", ]
a_oth_q3 <- mean(oth$resp)
cat(sprintf("\n(4) Spanish sp_text3_q3 acc %.3f vs Spanish text3_q4 %.3f; other wave-1 sites text3_q3 %.3f\n",
            a_sp_q3, a_sp_q4, a_oth_q3))
cat(sprintf("    shipped sp_text3_q3 text: %s\n", unique(it$item_text[it$item == "sp_text3_q3"])))
if (!(abs(a_sp_q3 - a_sp_q4) < 0.15 && a_oth_q3 - a_sp_q3 > 0.25)) ok <- FALSE

cat("\nScope: corroborates the sheet-column == QUESTIONNUM tie overall and at two marker\n",
    "cells; does not pin each item's wording individually (PARTIAL).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

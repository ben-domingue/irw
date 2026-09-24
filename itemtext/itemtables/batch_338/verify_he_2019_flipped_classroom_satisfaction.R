# verify_he_2019_flipped_classroom_satisfaction.R -- Step 5b mapping check.
#
# Claim: satisfaction_k carries Table 7 item No. k of He et al. (2019) PLOS ONE
# 10.1371/journal.pone.0214624. The processing script prefixes the S8 File's bare
# column headers 1..8 ("satisfaction_" + header), so the claim is that the paper's
# item numbering 1..8 is the S8 column numbering 1..8.
#
# Falsifiable prediction: Table 7 publishes per-item mean (and SE) for BOTH arms.
# Two quirks, both handled explicitly below rather than tuned away:
#   (a) The live cov_group labels are REVERSED relative to the paper: the paper's FC
#       arm has n = 81 (Table 1), but the live rows labelled "flipped_classroom" hold
#       56 ids. So arms are matched by size (81 = FC, 56 = LBL), not by label.
#   (b) Table 7's LBL means for items 1, 5, 6 were computed with the source's "9"
#       code averaged in as if it were a score; IRW (correctly) drops those three
#       cells. The script adds a single 9 back to exactly the LBL items that have
#       55 of 56 ids, which reproduces the published figures.
suppressMessages(library(irw))
TABLE <- "he_2019_flipped_classroom_satisfaction"

PUB_FC  <- c(4.36, 3.65, 3.83, 4.54, 4.48, 4.36, 4.43, 4.41)
PUB_LBL <- c(3.05, 3.59, 2.88, 4.36, 3.20, 3.41, 4.41, 3.29)
TOL <- 0.006  # published to 2 dp

d <- irw::irw_fetch(TABLE)
items <- paste0("satisfaction_", 1:8)
nid <- tapply(d$id, d$cov_group, function(x) length(unique(x)))
cat("ids per live cov_group label:\n"); print(nid)
fc_lab  <- names(nid)[nid == 81]; lbl_lab <- names(nid)[nid == 56]
cat(sprintf("paper FC arm (n=81) = live label '%s'; paper LBL arm (n=56) = live label '%s'\n\n", fc_lab, lbl_lab))

fc  <- d[d$cov_group == fc_lab, ];  lbl <- d[d$cov_group == lbl_lab, ]
obs_fc <- sapply(items, function(i) mean(fc$resp[fc$item == i]))
obs_lbl <- sapply(items, function(i) {
  x <- lbl$resp[lbl$item == i]
  if (length(x) == 55) mean(c(x, 9)) else mean(x)     # quirk (b)
})
n_lbl <- sapply(items, function(i) sum(lbl$item == i))

cat(sprintf("%-15s %7s %7s | %7s %7s %5s\n", "item", "pubFC", "obsFC", "pubLBL", "obsLBL", "nLBL"))
for (k in 1:8) cat(sprintf("%-15s %7.2f %7.3f | %7.2f %7.3f %5d\n", items[k],
                           PUB_FC[k], obs_fc[k], PUB_LBL[k], obs_lbl[k], n_lbl[k]))

dev <- max(abs(c(obs_fc - PUB_FC, obs_lbl - PUB_LBL)))
cat(sprintf("\nlargest deviation over 16 cells: %.4f (tolerance %.3f)\n", dev, TOL))

# Uniqueness: for each live item, how many published rows match it on BOTH arms?
hits <- sapply(1:8, function(k) sum(abs(PUB_FC - obs_fc[k]) <= TOL & abs(PUB_LBL - obs_lbl[k]) <= TOL))
cat("published rows matching each live item on both arms:", hits, "\n")
cat("Note: FC means alone tie items 1 and 6 at 4.36; the LBL arm (3.05 vs 3.41) separates them.\n",
    "Does NOT establish: the administered (presumably Chinese) wording -- only which English\n",
    "Table 7 row belongs to which code.\n", sep = "")

cat(if (dev <= TOL && all(hits == 1)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

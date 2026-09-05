# verify_duboz_2021_pss10.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST (two parts, both falsifiable):
#   (a) item codes Stress1..Stress10 carry the CANONICAL PSS-10 item numbers, so the
#       four positively-worded self-efficacy items (4,5,7,8) and the six negatively-worded
#       helplessness items (1,2,3,6,9,10) sit exactly where the shipped item_text puts them.
#       Duboz et al. (2021) state this split for their own data:
#       "Six out of the ten items of PSS-10 are considered negative (1, 2, 3, 6, 9, 10)
#        and the remaining four as positive (4, 5, 7, 8)".
#       If any item_text were moved across that boundary, the correlation signs break.
#   (b) the shipped option_text runs 1 = Never .. 5 = Very Often (ASCENDING frequency),
#       not the reverse. The source .doc numbers these anchors 0-4 while the IRW table
#       stores 1-5, so the direction is an inference and has to be tested. Anchor: the
#       paper's own substantive finding that life satisfaction FALLS as stress RISES.
#       Scored under the shipped direction, PSS total must correlate NEGATIVELY with the
#       same respondents' Satisfaction With Life Scale total (duboz_2021_swls, same
#       source file, same ids). Under the flipped reading the sign flips.
#
# NOT established here: the order of items WITHIN each polarity class. Nothing in this
# study publishes per-item statistics, so e.g. Stress1 and Stress2 cannot be told apart.

suppressMessages(library(irw))

NEG <- c(1, 2, 3, 6, 9, 10)   # helplessness, negatively worded
POS <- c(4, 5, 7, 8)          # self-efficacy, positively worded

d <- as.data.frame(irw::irw_fetch("duboz_2021_pss10"))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", paste0("Stress", 1:10))]
cm <- cor(w[, -1], use = "pairwise.complete.obs")

cat("--- (a) keying polarity: mean r of each item with each polarity class ---\n")
cat(sprintf("%-9s %14s %14s  %s\n", "item", "r_with_neg6", "r_with_pos4", "expected"))
ok_a <- TRUE
for (i in 1:10) {
    it <- paste0("Stress", i)
    rn <- mean(cm[it, paste0("Stress", setdiff(NEG, i))])
    rp <- mean(cm[it, paste0("Stress", setdiff(POS, i))])
    own <- if (i %in% NEG) rn else rp
    riv <- if (i %in% NEG) rp else rn
    good <- own > 0 && riv < 0
    ok_a <- ok_a && good
    cat(sprintf("%-9s %+14.3f %+14.3f  %s %s\n", it, rn, rp,
                if (i %in% NEG) "helplessness" else "self-efficacy",
                if (good) "ok" else "*** WRONG SIDE ***"))
}
cat(sprintf("all 10 items on the predicted side of the split: %s\n\n", ok_a))

cat("--- (b) response-anchor direction, against the paper's stress<->life-satisfaction finding ---\n")
s <- as.data.frame(irw::irw_fetch("duboz_2021_swls"))
sw <- reshape(s[, c("id", "item", "resp")], idvar = "id", timevar = "item",
              direction = "wide")
names(sw) <- sub("^resp\\.", "", names(sw))
swls <- rowSums(sw[, setdiff(names(sw), "id")])
names(swls) <- sw$id

# PSS total on the shipped 1..5 Never..Very Often coding (positives reversed as 6 - x)
pss <- rowSums(w[, paste0("Stress", NEG)]) + rowSums(6 - w[, paste0("Stress", POS)])
names(pss) <- w$id
common <- intersect(names(pss), names(swls))
r_shipped <- cor(pss[common], swls[common])

cat(sprintf("n matched respondents: %d\n", length(common)))
cat(sprintf("PSS-10 total (shipped direction, 10-50): mean %.2f  sd %.2f  range %d-%d\n",
            mean(pss[common]), sd(pss[common]), min(pss[common]), max(pss[common])))
cat(sprintf("corr(PSS total, SWLS total)  shipped direction : %+.4f\n", r_shipped))
cat(sprintf("corr(PSS total, SWLS total)  flipped anchors   : %+.4f\n", -r_shipped))
cat("paper: \"stress is associated with life satisfaction ... life satisfaction decreases\n")
cat("       ... when stress increases\" -- requires a NEGATIVE correlation.\n")
ok_b <- r_shipped < 0
cat(sprintf("shipped direction reproduces the paper's sign: %s\n\n", ok_b))

cat("Note: this pins each item's POLARITY CLASS and the anchor direction. It does NOT\n")
cat("      order items within a polarity class; that assignment rests on the source\n")
cat("      column numbering (Stress1..Stress10) matching canonical PSS-10 numbering.\n")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

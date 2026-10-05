# verify_VEI_Brazillian_Shiramizu_2018_EI.R -- Step 5b for batch_542.
#
# Mapping claim: live codes Empathy_Item_n / Behavioral_Contagion_Item_n are the OSF
# deposit's own column names (data/VEI_Brazillian_Shiramizu_2018.R pivots them with no
# rename), and n is the "Item" number of Table 1 of Shiramizu & Yamamoto (2018,
# PsyArXiv 10.31234/osf.io/zwu26), under the matching subscale heading.
#
# The paper publishes NO per-item statistics (only subscale alphas and composite
# factor loadings), so no route here can distinguish every item from every other.
# Two checks, both PARTIAL-grade:
#   (A) subscale block structure (route 5): same-subscale items should intercorrelate
#       more than cross-subscale items. The code prefix already names the subscale, so
#       this mostly corroborates that the prefix and Table 1's column agree.
#   (B) semantic coherence of item means (route 8): content predictions about which
#       items should be most/least endorsed. CAVEAT: these predictions were written
#       after item_stats.R had been viewed, so this is a coherence check, not a blind
#       test. It rules out gross permutations, not adjacent swaps among mid-ranked items.
suppressMessages(library(irw))
TABLE <- "VEI_Brazillian_Shiramizu_2018_EI"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
E <- paste0("Empathy_Item_", 1:7); B <- paste0("Behavioral_Contagion_Item_", 1:7)
R <- cor(w[, c(E, B)], use = "pairwise.complete.obs")
ut <- function(m) m[upper.tri(m)]
wE <- mean(ut(R[E, E])); wB <- mean(ut(R[B, B])); x <- mean(R[E, B])
cat(sprintf("(A) mean r within Empathy = %.3f, within Behavioral Contagion = %.3f, cross = %.3f\n", wE, wB, x))
okA <- wE > x && wB > x

m <- tapply(d$resp, d$item, mean, na.rm = TRUE)
cat("\n(B) item means (live, pooled Study 1 + Study 2):\n")
for (i in c(E, B)) cat(sprintf("  %-28s %.2f\n", i, m[i]))
mb <- m[B]; me <- m[E]
top2B <- names(sort(mb, decreasing = TRUE))[1:2]
bot3B <- names(sort(mb))[1:3]
p1 <- setequal(top2B, B[c(1, 4)])        # yawn, baby smiling: common, overt contagion
p2 <- setequal(bot3B, B[c(3, 6, 7)])     # crossing arms, balance-beam lean, nose scratch: subtle mimicry
p3 <- names(which.min(me)) == E[3]       # feel pain in own leg watching a film: rarest
p4 <- names(which.max(me)) == E[1]       # feel excited when someone is excited: most common
cat(sprintf("  BC top-2 = {%s} expected {BC1 yawn, BC4 baby smile}: %s\n", paste(top2B, collapse = ","), p1))
cat(sprintf("  BC bottom-3 = {%s} expected {BC3 arms, BC6 beam, BC7 nose}: %s\n", paste(bot3B, collapse = ","), p2))
cat(sprintf("  EMP min = %s (%.2f) expected Empathy_Item_3 leg pain: %s\n", names(which.min(me)), min(me), p3))
cat(sprintf("  EMP max = %s (%.2f) expected Empathy_Item_1 excited: %s\n", names(which.max(me)), max(me), p4))
cat("\nNOT established: order among the mid-ranked items (EMP 2/4/5/6/7, BC 2/5) --\n",
    "an adjacent swap there would pass. Status PARTIAL.\n", sep = "")
cat(if (okA && p1 && p2 && p3 && p4) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

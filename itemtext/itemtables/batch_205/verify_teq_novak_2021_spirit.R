# Verification for teq_novak_2021_spirit (#1945, batch_205).  STATUS: PARTIAL.
#
# SOURCE. Novak et al. (2021), 'Psychometric Analysis of the Czech Version of the
# Toronto Empathy Questionnaire', IJERPH 18:5343, CC BY; OSF deposit osf.io/z85cv.
# This table is the study's DSES (Daily Spiritual Experience Scale) block, used
# there for convergent validity. The paper states the scale and the anchors; it
# does NOT print the items, and neither does the deposit.
#
# THE CZECH RENUMBERING IS PUBLISHED, which is what makes all 15 assignable.
# The Czech 15-item DSES is Underwood's 16 items minus item 5 ("I find comfort in
# my religion or spirituality", dropped for r=.92 with item 4) -- Malinakova et
# al. 2018, Ceskoslovenska psychologie 62 Suppl.1. So Czech position n maps to
# Underwood 1-4, 6-16 in order. IRW already relied on that renumbering once, for
# CV_OASIS_ODSIS_PPE_Novak_2020_DSES in batch_024, from the same research group.
#
# THREE INDEPENDENT PINS AGREE WITH IT, which is why it is not taken on trust:
#   SPIRIT_12_ALTR and SPIRIT_13_PRIJ name their construct in the code suffix
#     (altruism, prijeti = acceptance) and the renumbering puts Underwood's
#     "selfless caring" and "accept others" at exactly 12 and 13.
#   SPIRIT_15 carries four response levels where every other item carries six,
#     and the renumbering puts Underwood's closeness question at 15.
#
# Route 1: the level-count signature.
# Route 2: the God/non-God split predicted by the mapping, tested on the data.
# Route 3: scale DIRECTION, which three sources disagree about, settled by data.
# Route 4: the paper's reported reliability reproduced.
suppressWarnings(suppressMessages({library(dplyr); library(tidyr)}))
alpha <- function(m) { m <- m[complete.cases(m), , drop = FALSE]; k <- ncol(m)
    (k / (k - 1)) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
sp <- as.data.frame(irw::irw_fetch("teq_novak_2021_spirit"))
sc <- as.data.frame(irw::irw_fetch("teq_novak_2021_scbs"))
if (!nrow(sp)) stop("irw_fetch returned no rows -- nothing was checked")
sp$item <- as.character(sp$item)
wide <- function(x) x %>% select(id, item, resp) %>% distinct(id, item, .keep_all = TRUE) %>%
                         pivot_wider(names_from = item, values_from = resp)
w <- wide(sp)

cat("=== Route 1: the level-count signature identifies the closeness item ===\n")
lv <- sapply(setdiff(names(w), "id"), function(i) length(unique(na.omit(w[[i]]))))
for (i in names(sort(lv))) cat(sprintf("  %-16s %d levels\n", i, lv[i]))
r1 <- lv[["SPIRIT_15"]] == 4 && all(lv[setdiff(names(lv), "SPIRIT_15")] == 6)
cat(sprintf("  -> exactly one item has 4 levels and it is SPIRIT_15: %s\n", r1))
cat("  Underwood's scale is 15 frequency items on 6 points plus one closeness\n")
cat("  question on 4. Two papers from this group describe the Czech 15-item form\n")
cat("  the same way: 14 six-point items and a final four-point item.\n")

cat("\n=== Route 2: the mapping predicts which items mention God, and the data agrees ===\n")
# Under the Czech renumbering, six of the fourteen frequency items do NOT refer to
# God: SPIRIT_2 (connection to all of life), SPIRIT_5 (inner peace), SPIRIT_10
# (beauty of creation), SPIRIT_11 (thankful for blessings), SPIRIT_12_ALTR
# (selfless caring) and SPIRIT_13_PRIJ (accept others). If the mapping is right
# those six should be the weakest correlates of "how close do you feel to God";
# if it is shifted, the boundary lands somewhere else.
NONGOD <- c("SPIRIT_2", "SPIRIT_5", "SPIRIT_10", "SPIRIT_11",
            "SPIRIT_12_ALTR", "SPIRIT_13_PRIJ")
r <- sapply(setdiff(names(w), c("id", "SPIRIT_15")),
            function(i) cor(w[[i]], w$SPIRIT_15, use = "complete.obs"))
for (i in names(sort(r)))
    cat(sprintf("  %-16s r with closeness item %+.3f   %s\n", i, r[i],
                if (i %in% NONGOD) "<- predicted non-God" else ""))
lowest6 <- names(sort(r))[1:6]
r2 <- setequal(lowest6, NONGOD)
cat(sprintf("  six weakest correlates: %s\n", paste(sort(lowest6), collapse = ", ")))
cat(sprintf("  -> exactly the six the mapping predicts: %s\n", r2))
cat("  This tests all fifteen positions at once rather than the four that carry\n")
cat("  their own evidence. A renumbering shifted by even one item moves a God item\n")
cat("  into the low group or a non-God item out of it, and the split breaks.\n\n")
cat("\n=== Route 3: scale direction, which the sources contradict each other on ===\n")
f14 <- setdiff(names(w), c("id", "SPIRIT_15"))
w$sp14 <- rowMeans(w[, f14], na.rm = TRUE)
sct <- sc %>% group_by(id) %>% summarise(scbs = mean(resp, na.rm = TRUE), .groups = "drop")
m <- inner_join(w[, c("id", "sp14", "SPIRIT_15")], sct, by = "id")
r_cs <- cor(m$scbs, m$sp14, use = "complete.obs")
r_1514 <- cor(m$SPIRIT_15, m$sp14, use = "complete.obs")
cat(sprintf("  SPIRIT_15 vs the 14 frequency items:      r = %+.3f (same direction)\n", r_1514))
cat(sprintf("  SCBCS compassion mean vs the 14 items:    r = %+.3f\n", r_cs))
cat("  The SCBCS direction is unambiguous -- the paper states 1 'Not at all true of\n")
cat("  me' to 7 'Very true of me', higher = more compassion -- and the same paper\n")
cat("  reports a POSITIVE association between compassion and spirituality. That\n")
cat("  only holds if a higher DSES value means LESS spiritual experience, i.e.\n")
cat("  1 = 'Many times a day' through 6 = 'Never or almost never'.\n")
r3 <- r_cs < 0 && r_1514 > 0
cat(sprintf("  -> anchors ship in that direction: %s\n", r3))
cat("  NOTE the source paper contradicts itself: it states those anchors and then\n")
cat("  says 'a higher score indicates a higher degree of spirituality'. The anchors\n")
cat("  are right, that clause is not. Two other papers from the same group state\n")
cat("  the anchors in the opposite order. The data settles it.\n")
cat("  SPIRIT_15 runs the same way, so its four labels are reversed relative to\n")
cat("  Underwood's printed order -- 1 is the closest, 4 the least close.\n")

cat("\n=== Route 4: the paper's reported reliability reproduced ===\n")
a <- alpha(as.matrix(w[, setdiff(names(w), c("id", "sp14"))]))
cat(sprintf("  Cronbach's alpha from the live data: %.3f; the paper reports 0.96\n", a))
r4 <- abs(a - 0.96) < 0.01
cat(sprintf("  -> agrees to the printed precision: %s\n", r4))
cat("  This confirms the item SET and the scoring, not the wording.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which item is which WITHIN the God block or within the non-God block.\n")
cat("  Route 2 separates two classes of six and eight, not fifteen individuals, so\n")
cat("  SPIRIT_1 and SPIRIT_7 are interchangeable as far as any test here goes.\n")
cat("  The full ordering rests on the published Czech renumbering rather than on\n")
cat("  anything in this data, which is why mapping_basis is reconstructed and the\n")
cat("  status is PARTIAL. Nor does any route check the Czech wording itself: the\n")
cat("  administered Czech is not published, so item_text is Underwood's English.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r4) "PASS" else "FAIL", "\n")

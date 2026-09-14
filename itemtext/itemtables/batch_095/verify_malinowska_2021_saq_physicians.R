# Step 5b verification for malinowska_2021_saq_physicians.
#
# CLAIM UNDER TEST: bezp_<n> is SAQ-SF PL question <n> (n = 1..36), and
# kier_24a..kier_28a are the ward-manager ("kier. oddzialu") rating of questions
# 24-28 while bezp_24..bezp_28 are the hospital-director ("dyr. szpitala") rating
# of the same five stems.
#
# Three independent, falsifiable predictions follow from that mapping:
#   (A) Route 3 -- published subscale means. Malinowska-Lipien et al. (2021),
#       PLOS ONE 16(12):e0260926, Table 2, physicians row, reports the six SAQ
#       subscale scores on the 0-100 conversion (1=0, 2=25, 3=50, 4=75, 5=100;
#       items 2, 11, 36 reversed; "Nie dotyczy" = resp 6 excluded). The paper
#       assigns TC=1-6, SC=7-13, JS=15-19, SR=20-23, PM=24-28, WC=29-32.
#       Recomputing those subscales from the items this table claims they are
#       must reproduce the published numbers. PM is the decisive one: it is only
#       reproduced when BOTH management referents (bezp_24-28 AND kier_24a-28a)
#       are averaged, which is what shows the kier_* columns are the second
#       referent of questions 24-28 rather than five unrelated items.
#   (B) Route 6 -- keying polarity. The paper states questions 2, 11 and 36 are
#       reverse scored. Under the claimed mapping exactly bezp_2, bezp_11 and
#       bezp_36 -- and no others -- must show a negative raw item-total
#       correlation.
#   (C) Route 7 -- marker item. Question 35 asks about collaboration with
#       pharmacists, the one item a hospital physician can plausibly mark
#       "Nie dotyczy". bezp_35 must therefore carry the most resp==6 responses
#       of any item, by a wide margin.
#
# The IRW table has 738 respondents against the paper's N = 527 physicians, so
# (A) is checked at a tolerance of 3 points, not to the decimal (largest observed
# deviation is teamwork climate at 2.45; work conditions and perception of
# management land within 0.25).

suppressMessages(library(irw))

TABLE <- "malinowska_2021_saq_physicians"

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
rownames(w) <- w$id; w$id <- NULL

conv <- function(x, reverse = FALSE) {
    v <- ifelse(is.na(x) | x == 6, NA, (x - 1) * 25)
    if (reverse) v <- 100 - v
    v
}
S <- as.data.frame(lapply(names(w), function(cn) {
    n <- suppressWarnings(as.integer(sub("^bezp_", "", cn)))
    conv(w[[cn]], reverse = (!is.na(n) && n %in% c(2, 11, 36)))
}))
names(S) <- names(w)

# ---- (A) published subscale means -------------------------------------------
PUB <- c(TC = 66.76, SC = 66.06, JS = 68.50, SR = 80.86, PM = 59.47, WC = 52.09)
SUB <- list(TC = paste0("bezp_", 1:6),
            SC = paste0("bezp_", 7:13),
            JS = paste0("bezp_", 15:19),
            SR = paste0("bezp_", 20:23),
            PM = c(paste0("bezp_", 24:28), paste0("kier_", 24:28, "a")),
            WC = paste0("bezp_", 29:32))
TOL <- 3.0  # observed max is TC at 2.45; N differs from the paper by 211 respondents

cat("(A) Route 3 -- published subscale means, physicians (paper Table 2, N=527)\n")
cat("    vs. recomputed from this table's item assignment (N=738)\n\n")
cat(sprintf("%-4s %10s %10s %8s\n", "sub", "published", "observed", "diff"))
obs <- numeric(0)
for (k in names(SUB)) {
    m <- rowMeans(S[, SUB[[k]], drop = FALSE], na.rm = TRUE)
    obs[k] <- mean(m, na.rm = TRUE)
    cat(sprintf("%-4s %10.2f %10.2f %8.2f\n", k, PUB[k], obs[k], obs[k] - PUB[k]))
}
worstA <- max(abs(obs[names(PUB)] - PUB))
cat(sprintf("\n    largest deviation: %.2f (tolerance %.2f)\n", worstA, TOL))

# the PM discriminator: single-referent readings must FAIL
pm_b <- mean(rowMeans(S[, paste0("bezp_", 24:28), drop = FALSE], na.rm = TRUE), na.rm = TRUE)
pm_k <- mean(rowMeans(S[, paste0("kier_", 24:28, "a"), drop = FALSE], na.rm = TRUE), na.rm = TRUE)
cat(sprintf("    PM discriminator: bezp_24-28 alone = %.2f, kier_24a-28a alone = %.2f,\n", pm_b, pm_k))
cat(sprintf("      both averaged = %.2f, published = %.2f -- only the pooled reading fits.\n",
            obs["PM"], PUB["PM"]))
okA <- worstA <= TOL && abs(pm_b - PUB["PM"]) > 5 && abs(pm_k - PUB["PM"]) > 5

# ---- (B) keying polarity ----------------------------------------------------
core <- paste0("bezp_", 1:36)
lik <- as.data.frame(lapply(w[, core], function(x) ifelse(x == 6, NA, x)))
tot <- rowMeans(lik, na.rm = TRUE)
r <- sapply(core, function(cn) cor(lik[[cn]], tot, use = "pairwise.complete.obs"))
neg <- names(sort(r))[r[order(r)] < 0]
cat("\n(B) Route 6 -- raw item-total correlations; paper says questions 2, 11, 36\n    are reverse scored.\n")
cat(sprintf("    negative-r items: %s\n", paste(sprintf("%s (%.3f)", neg, r[neg]), collapse = ", ")))
cat(sprintf("    lowest positive:  %s\n",
            paste(sprintf("%s (%.3f)", names(sort(r))[length(neg) + 1:2],
                          sort(r)[length(neg) + 1:2]), collapse = ", ")))
okB <- setequal(neg, c("bezp_2", "bezp_11", "bezp_36"))

# ---- (C) marker item --------------------------------------------------------
n6 <- sort(sapply(names(w), function(cn) sum(w[[cn]] == 6, na.rm = TRUE)), decreasing = TRUE)
cat("\n(C) Route 7 -- 'Nie dotyczy' (resp = 6) counts; question 35 is the pharmacist\n    collaboration item, the only one a physician can plausibly mark N/A.\n")
cat(sprintf("    top 4: %s\n", paste(sprintf("%s=%d", names(n6)[1:4], n6[1:4]), collapse = ", ")))
okC <- names(n6)[1] == "bezp_35" && n6[1] > 3 * n6[2]

cat("\nWhat this does NOT establish: none of the three routes separates items WITHIN\n",
    "a subscale. bezp_2, bezp_11, bezp_35 and bezp_36 are pinned individually; the\n",
    "remaining positions are pinned only to their published subscale block\n",
    "({1,3,4,5,6}, {7,8,9,10,12,13}, {15..19}, {20..23}, the five management pairs,\n",
    "{29..32}, and {14, 33, 34} by exclusion). Nor does any route decide WHICH member\n",
    "of each management pair is the ward manager and which the hospital director:\n",
    "that rests on the source column name (KIER 24A vs bezp_24) matching the printed\n",
    "label 'kier. oddzialu', which the questionnaire prints first, and is only\n",
    "corroborated -- not proved -- by the 27-point gap above (73.08 vs 45.97) running\n",
    "in the direction SAQ studies always report, local management rated above\n",
    "hospital management. Status is therefore PARTIAL.\n", sep = "")

cat(sprintf("\nA=%s B=%s C=%s\n", okA, okB, okC))
cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

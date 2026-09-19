# verify_latifi_2026_insect_fear.R
#
# What is being verified
# ----------------------
# ITEM AXIS (item <-> item_text) is a code-label match, not an inference: the
# study's S1 Table prints every item with its own code ("Q1. I can easily
# identify insects and spiders."), the SPSS deposit's columns are named Q1..Q32,
# and data/latifi_2026_insect_fear.py melts those columns by name
# (item_cols = [f"Q{i}" for i in range(1, 33)], no rename). Nothing statistical
# can add to that, so this script does not try to.
#
# RESP AXIS (resp <-> option_text) is what carried a decision, and it is what is
# checked here. The deposit's value labels say Q1-Q23 run 1 = "completly
# disagree" .. 5 = "completly agree"; the paper's Methods says the OTHER block
# is the reversed one ("Pesticide use and personal anxiety: 1 = Always to 5 =
# Never"). Both cannot be right, and the shipped table takes neither at face
# value: it ships Q1-Q23 as 1 = Strongly agree .. 5 = Strongly disagree and
# Q24-Q32 as 1 = Never .. 5 = Always. The three tests below are what forced that.

suppressMessages(library(irw))

TABLE <- "latifi_2026_insect_fear"
d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
d$item <- as.character(d$item)

wide <- reshape(d[, c("id", "item", "resp")], idvar = "id",
                timevar = "item", direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
cov <- unique(d[, c("id", "cov_age", "cov_gender")])
wide <- merge(wide, cov, by = "id")

blk <- function(v) rowMeans(wide[, paste0("Q", v)], na.rm = TRUE)
# Shipped orientation: the agreement block runs agree -> disagree, so the
# construct score is 6 - mean; the frequency block runs Never -> Always as is.
know <- 6 - blk(1:4)
ento <- 6 - blk(5:23)
anx  <- blk(28:32)

ok <- rep(TRUE, 3)

# ---- Test 1. Reproduce the paper's own age correlations -------------------
# Latifi et al. (2026), "Age- and gender-related analyses": age correlates
# r = 0.10 (p < 0.001) with knowledge, r = 0.077 (p = 0.004) with anxiety, and
# r = 0.035 (p = 0.199, ns) with insectophobia. Under the deposit's labelled
# direction the two agreement-block constructs come out at -0.10 and -0.034:
# right magnitude, wrong sign. The shipped orientation reproduces all three.
age <- as.numeric(wide$cov_age)
pub <- c(knowledge = 0.100, insectophobia = 0.035, anxiety = 0.077)
obs <- c(knowledge = cor(age, know, use = "pairwise"),
         insectophobia = cor(age, ento, use = "pairwise"),
         anxiety = cor(age, anx, use = "pairwise"))
cat("Test 1 -- age correlations, shipped orientation vs Latifi et al. (2026)\n")
cat(sprintf("%-15s %10s %10s %8s\n", "construct", "published", "observed", "diff"))
for (i in seq_along(pub))
    cat(sprintf("%-15s %+10.3f %+10.3f %8.3f\n",
                names(pub)[i], pub[i], obs[i], obs[i] - pub[i]))
t1 <- max(abs(obs - pub)) <= 0.01 && all(sign(obs) == 1)
cat(sprintf("  max deviation %.4f (tol 0.010), all signs positive: %s\n\n",
            max(abs(obs - pub)), t1))
ok[1] <- t1

# ---- Test 2. Frequency-block direction, from two floor items --------------
# Q26 "I use insecticides at school" and Q27 "I have insecticide with me" are
# behaviours schoolchildren overwhelmingly do NOT do. The shipped anchors put
# "Never" at resp = 1, so both must pile up at 1; the reversed reading would
# claim most children ALWAYS carry insecticide at school.
cat("Test 2 -- floor share at resp = 1 for the two insecticide-possession items\n")
p26 <- mean(wide$Q26 == 1, na.rm = TRUE); p27 <- mean(wide$Q27 == 1, na.rm = TRUE)
cat(sprintf("  Q26 'I use insecticides at school'  %%(resp=1) = %.1f%%\n", 100 * p26))
cat(sprintf("  Q27 'I have insecticide with me'    %%(resp=1) = %.1f%%\n", 100 * p27))
t2 <- p26 > 0.6 && p27 > 0.6
cat(sprintf("  both > 60%%, so resp 1 = 'Never' not 'Always': %s\n\n", t2))
ok[2] <- t2

# ---- Test 3. Anxiety must correlate POSITIVELY with insect fear -----------
# General anxiety-proneness and a specific animal fear cannot be negatively
# related. Under the deposit's labelled direction for Q1-Q23 they correlate
# about -0.35; under the shipped orientation, +0.35. The same flip puts girls
# above boys on insectophobia, which is the direction the paper reports
# ("females scoring slightly higher") and the direction its own introduction
# cites (4:1 to 6:1 female:male phobia ratios).
r_ax <- cor(anx, ento, use = "pairwise")
g <- as.numeric(wide$cov_gender)   # 1 = Girl, 2 = Boy
cat("Test 3 -- construct relations under the shipped orientation\n")
cat(sprintf("  cor(personal anxiety, insectophobia) = %+.3f (labelled direction would give %+.3f)\n",
            r_ax, -r_ax))
cat(sprintf("  insectophobia mean: girls %.3f vs boys %.3f (diff %+.3f)\n",
            mean(ento[g == 1], na.rm = TRUE), mean(ento[g == 2], na.rm = TRUE),
            mean(ento[g == 1], na.rm = TRUE) - mean(ento[g == 2], na.rm = TRUE)))
t3 <- r_ax > 0.2 && mean(ento[g == 1], na.rm = TRUE) > mean(ento[g == 2], na.rm = TRUE)
cat(sprintf("  positive anxiety-fear link and girls > boys: %s\n\n", t3))
ok[3] <- t3

cat("What this does NOT establish: nothing here separates one item from another\n",
    "WITHIN a block -- the order of Q5..Q23 rests entirely on the S1 Table's own\n",
    "Q-numbering matching the deposit's column names, which is a label match and\n",
    "needs no statistical support. Tests 1-3 verify the two blocks' option_text\n",
    "direction and their block membership only.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

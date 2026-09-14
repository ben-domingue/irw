# Step 5b mapping check for nomt_hooper_2024_study1.
#
# Two claims are shipped, and both are falsifiable against the data:
#
#  (a) SECTION -> OBJECT CATEGORY. The item blocks 1xx / 2xx / 3xx are labelled
#      Greebles / Sheinbugs / Ziggerins. This is NOT presentation order -- the
#      paper says participants did "Ziggerins, then Greebles, then Sheinbugs" --
#      so the labelling is a real, breakable claim. Hooper, Tomarken & Gauthier
#      (2024) Table 1 publishes M and SD per task per instruction group; pooled
#      over the 63 English + 56 Spanish participants those means are far apart
#      (.59 / .56 / .68), so they identify the assignment uniquely.
#
#  (b) PHASE -> item_text. Within each block, items x01-x18 carry
#      "Which object did you just view?" (learning phase, 3AFC over the object
#      just studied) and x19-x72 carry "Which object is one of the 6 target
#      objects?" (test phase). The paper states the split -- "The learning phase
#      (trials 1-18) ... In the following 54 test phase trials (block 2: trials
#      19-48; block 3: trials 48-72)" -- which predicts that the single largest
#      drop in accuracy between adjacent items inside each block falls exactly at
#      the 18 -> 19 boundary. If the split were anywhere else, this fails.
#
# The shipped text takes six distinct (section_id, item_text) combinations and
# this script pins all six group boundaries; inside a group every item carries
# byte-identical text, so the mapping is fully determined by (a) and (b).

suppressMessages(library(irw))
TABLE <- "nomt_hooper_2024_study1"

# Hooper et al. (2024), Behav Res Methods 57:36, Table 1. n = 56 Spanish, 63 English.
PUB <- list(greebles  = c(sp = .593, en = .588),
            ziggerins = c(sp = .686, en = .676),
            sheinbugs = c(sp = .560, en = .561))
pooled <- sapply(PUB, function(x) (56 * x["sp"] + 63 * x["en"]) / 119)
names(pooled) <- names(PUB)

d <- irw::irw_fetch(TABLE)
d$item <- as.integer(as.character(d$item))
d$blk  <- d$item %/% 100

cat(sprintf("live: %d rows, %d persons, %d items\n\n",
            nrow(d), length(unique(d$id)), length(unique(d$item))))

# ---- (a) block -> category -------------------------------------------------
SHIPPED <- c("1" = "greebles", "2" = "sheinbugs", "3" = "ziggerins")
per_person <- tapply(d$resp, list(d$id, d$blk), mean)
obs_m  <- colMeans(per_person, na.rm = TRUE)
obs_sd <- apply(per_person, 2, sd, na.rm = TRUE)

cat("(a) block mean accuracy vs published pooled M (SD), per shipped label\n")
cat(sprintf("%-6s %-10s %14s %14s %8s\n", "block", "shipped", "observed M(SD)", "published M", "diff"))
worst_a <- 0
for (b in names(obs_m)) {
    lab <- SHIPPED[[b]]
    diff <- obs_m[[b]] - pooled[[lab]]
    worst_a <- max(worst_a, abs(diff))
    cat(sprintf("%-6s %-10s %6.3f (%.3f) %14.3f %8.3f\n",
                b, lab, obs_m[[b]], obs_sd[[b]], pooled[[lab]], diff))
}
cat(sprintf("largest deviation under the shipped labelling: %.3f (tolerance 0.02)\n", worst_a))

# the rival hypothesis: label the blocks in the order the tasks were presented
RIVAL <- c("1" = "ziggerins", "2" = "greebles", "3" = "sheinbugs")
worst_r <- max(abs(sapply(names(obs_m), function(b) obs_m[[b]] - pooled[[RIVAL[[b]]]])))
cat(sprintf("largest deviation under presentation-order labelling (rival): %.3f -- rejected\n\n", worst_r))

# ---- (b) learning/test boundary -------------------------------------------
# Changepoint: for every candidate split k, mean(items 1..k) - mean(items k+1..72).
# If the shipped split is right, this is maximised at k = 18 in every block.
cat("(b) best accuracy changepoint inside each block (predicted at k = 18)\n")
ok_b <- TRUE
for (b in sort(unique(d$blk))) {
    sub <- d[d$blk == b, ]
    m <- tapply(sub$resp, sub$item, mean)
    m <- as.numeric(m[order(as.integer(names(m)))])
    ks <- 5:67
    gap <- sapply(ks, function(k) mean(m[1:k]) - mean(m[(k + 1):72]))
    best <- ks[which.max(gap)]
    cat(sprintf("block %d: learning mean(x01-x18) = %.3f, test mean(x19-x72) = %.3f, gap %.3f; best k = %d (gap %.3f), gap at k=18 = %.3f\n",
                b, mean(m[1:18]), mean(m[19:72]), mean(m[1:18]) - mean(m[19:72]),
                best, max(gap), gap[ks == 18]))
    ok_b <- ok_b && best == 18
}
cat("\n")

pass <- worst_a <= 0.02 && worst_r > 0.02 && ok_b
cat(if (pass) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")

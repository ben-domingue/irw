# verify_emobank_buechel_2017.R
#
# WHAT IS BEING VERIFIED
# ----------------------
# The live table's six item codes are `<dimension>-<perspective>` where dimension
# in {valence, arousal, dominance} and perspective in {writer, reader}. The shipped
# item_text is the corresponding SAM panel paragraph from the CrowdFlower task
# instructions reproduced in the appendix of arXiv:2205.01996 (= Buechel & Hahn,
# EACL 2017), one paragraph per dimension per perspective. The shipped option_text
# puts the Pleasure/Arousal/Control LEFT pole at resp=1 and the RIGHT pole at resp=5.
#
# Two claims, verified separately:
#
#   (A) ITEM AXIS. Each live item is exactly one column of one file of the EmoBank
#       deposit (github.com/JULIELab/EmoBank, corpus/individual_{writer,reader}_ratings.csv,
#       columns V / A / D). data/emobank_buechel_2017.R builds the table by a
#       number-free rename (V->valence, A->arousal, D->dominance) plus the file's
#       perspective. The falsifiable prediction is that the live per-item response
#       distribution equals that deposit column's distribution, CELL FOR CELL --
#       and because all six deposit marginals are mutually distinct, a match pins
#       every item to exactly one column. If arousal-writer and dominance-writer
#       were swapped this breaks immediately.
#       Corroborated independently of the deposit's column names by reproducing the
#       ordering of the twelve published IAA values in EACL 2017 Table 2 (r and MAE
#       per dimension per perspective).
#
#   (B) RESP AXIS. resp=1 is the left (Unhappy / Calm / Submissive) pole, not the
#       right one. Checked against content: the paper's own Hint that "Capitalization,
#       exclamation marks and swearing may often hint at high Arousal", and a
#       positive- vs negative-word contrast on Valence.
#
# NOTE ON COST: irw_fetch() exports the whole table. This one is 318,519 rows of
# (id, item, resp) -- a few MB -- so the export is deliberate and cheap. The item
# and resp SETS were gated separately with validate_items.R --table-sets.

suppressMessages(library(irw))

TABLE <- "emobank_buechel_2017"
GH <- "https://raw.githubusercontent.com/JULIELab/EmoBank/master/corpus/"
ITEMS <- c("valence-writer","arousal-writer","dominance-writer",
           "valence-reader","arousal-reader","dominance-reader")

ok <- TRUE

## ---------- deposit ----------
dep <- list(writer = read.csv(paste0(GH, "individual_writer_ratings.csv"),
                              stringsAsFactors = FALSE),
            reader = read.csv(paste0(GH, "individual_reader_ratings.csv"),
                              stringsAsFactors = FALSE))
raw <- read.csv(paste0(GH, "raw.csv"), stringsAsFactors = FALSE)

dep_counts <- matrix(0L, nrow = length(ITEMS), ncol = 5,
                     dimnames = list(ITEMS, 1:5))
map <- c(V = "valence", A = "arousal", D = "dominance")
for (p in c("writer", "reader"))
    for (cl in names(map))
        dep_counts[paste0(map[[cl]], "-", p), ] <-
            as.integer(table(factor(dep[[p]][[cl]], levels = 1:5)))

## ---------- (A) live vs deposit, 30 cells ----------
d <- irw::irw_fetch(TABLE)
live_counts <- matrix(0L, nrow = length(ITEMS), ncol = 5,
                      dimnames = list(ITEMS, 1:5))
tb <- table(factor(d$item, levels = ITEMS), factor(d$resp, levels = 1:5))
live_counts[] <- as.integer(tb)

cat("=== (A) per-item response distribution: live IRW vs EmoBank deposit ===\n")
cat(sprintf("%-18s %26s %26s  %s\n", "item", "live (1..5)", "deposit (1..5)", "match"))
for (it in ITEMS) {
    m <- identical(live_counts[it, ], dep_counts[it, ])
    if (!m) ok <- FALSE
    cat(sprintf("%-18s %26s %26s  %s\n", it,
                paste(live_counts[it, ], collapse = " "),
                paste(dep_counts[it, ], collapse = " "),
                if (m) "YES" else "NO"))
}
distinct <- nrow(unique(dep_counts)) == length(ITEMS)
cat(sprintf("all six deposit marginals mutually distinct: %s (%d unique of %d)\n",
            if (distinct) "YES" else "NO", nrow(unique(dep_counts)), length(ITEMS)))
if (!distinct) ok <- FALSE

## ---------- (A2) published IAA, EACL 2017 Table 2 ----------
PUB_R   <- c(`valence-writer` = .698, `arousal-writer` = .578, `dominance-writer` = .540,
             `valence-reader` = .738, `arousal-reader` = .595, `dominance-reader` = .570)
PUB_MAE <- c(`valence-writer` = .300, `arousal-writer` = .388, `dominance-writer` = .316,
             `valence-reader` = .349, `arousal-reader` = .441, `dominance-reader` = .367)
obs_r <- obs_mae <- setNames(rep(NA_real_, 6), ITEMS)
for (p in c("writer", "reader")) {
    dd <- dep[[p]]
    dd <- dd[!(dd$V == 1 & dd$A == 1 & dd$D == 1), ]   # paper removed the (1,1,1) block
    for (cl in names(map)) {
        it <- paste0(map[[cl]], "-", p)
        x  <- dd[[cl]]
        mu <- ave(x, dd$id, FUN = mean)
        n  <- ave(x, dd$id, FUN = length)
        k  <- n >= 2                                    # paper aggregates n>=2 only
        obs_r[it]   <- cor(x[k], mu[k])
        obs_mae[it] <- mean(abs(x[k] - mu[k]))
    }
}
cat("\n=== (A2) IAA vs EACL 2017 Table 2 (per dimension x perspective) ===\n")
cat("  (absolute level differs by ~.05: the paper averages r/MAE over annotators,\n",
    "   and annotator identity is not in the deposit -- the ORDERING is the signal)\n", sep = "")
cat(sprintf("%-18s %9s %9s %9s %9s\n", "item", "pub r", "obs r", "pub MAE", "obs MAE"))
for (it in ITEMS)
    cat(sprintf("%-18s %9.3f %9.3f %9.3f %9.3f\n",
                it, PUB_R[it], obs_r[it], PUB_MAE[it], obs_mae[it]))
prs <- combn(ITEMS, 2, simplify = FALSE)
agree_r   <- sum(vapply(prs, function(q) sign(PUB_R[q[1]]   - PUB_R[q[2]])   ==
                                         sign(obs_r[q[1]]   - obs_r[q[2]]),   logical(1)))
agree_mae <- sum(vapply(prs, function(q) sign(PUB_MAE[q[1]] - PUB_MAE[q[2]]) ==
                                         sign(obs_mae[q[1]] - obs_mae[q[2]]), logical(1)))
either    <- sum(vapply(prs, function(q)
    (sign(PUB_R[q[1]] - PUB_R[q[2]]) == sign(obs_r[q[1]] - obs_r[q[2]])) ||
    (sign(PUB_MAE[q[1]] - PUB_MAE[q[2]]) == sign(obs_mae[q[1]] - obs_mae[q[2]])), logical(1)))
cat(sprintf("pairwise orderings reproduced: r %d/15, MAE %d/15, at least one metric %d/15\n",
            agree_r, agree_mae, either))
if (either < 15) ok <- FALSE

## ---------- (B) resp direction ----------
cat("\n=== (B) direction of the 1..5 coding (option_text poles) ===\n")
for (p in c("writer", "reader")) {
    dd <- dep[[p]]
    agg <- aggregate(cbind(V, A, D) ~ id, data = dd, FUN = mean)
    txt <- raw$text[match(agg$id, raw$id)]
    txt[is.na(txt)] <- ""
    bang <- grepl("!", txt, fixed = TRUE)
    pos  <- grepl("\\b(wonderful|great|love|happy|beautiful|thanks|thank you|excellent)\\b",
                  txt, ignore.case = TRUE)
    neg  <- grepl("\\b(hate|awful|terrible|horrible|sad|fuck|worst|stupid)\\b",
                  txt, ignore.case = TRUE)
    a1 <- mean(agg$A[bang]); a0 <- mean(agg$A[!bang])
    v1 <- mean(agg$V[pos]);  v0 <- mean(agg$V[neg])
    cat(sprintf("%-7s arousal:  with '!' (n=%4d) %.3f   vs without (n=%5d) %.3f  -> %s\n",
                p, sum(bang), a1, sum(!bang), a0,
                if (a1 > a0) "5 = Excited (as shipped)" else "SHIPPED POLES WRONG"))
    cat(sprintf("%-7s valence:  positive words (n=%4d) %.3f vs negative words (n=%4d) %.3f -> %s\n",
                p, sum(pos), v1, sum(neg), v0,
                if (v1 > v0) "5 = Happy (as shipped)" else "SHIPPED POLES WRONG"))
    if (!(a1 > a0 && v1 > v0)) ok <- FALSE
}
cat("Dominance has no comparable lexical marker here; its direction rests on the deposit's\n",
    "own documented extremes (corpus/README.md: min D 1.78 'I shivered as I walked past the\n",
    "pale man's blank eyes...', max D 4.2 '“NO”' -- a command, which the task's own Hints\n",
    "call 'a reliable indicator for high Control') plus the fact that all three SAM rows share\n",
    "one left-to-right layout, verified above for Valence and Arousal.\n", sep = "")

cat("\nWHAT THIS DOES NOT ESTABLISH: nothing about the sentence being rated. In this table\n",
    "`id` is the EmoBank sentence, not a person, and the stimulus text lives in the deposit's\n",
    "raw.csv, not in the itemtext table. Also, positions 2-4 of the SAM scale carry no printed\n",
    "label in the source, so option_text is deliberately blank there.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

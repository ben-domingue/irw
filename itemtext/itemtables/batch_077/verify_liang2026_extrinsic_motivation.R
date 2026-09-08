# Step 5b re-runnable evidence for liang2026_extrinsic_motivation.
#
# THE CLAIM UNDER TEST. This table's item codes are em_1..em_5. They are a
# lower-cased rename of the deposit CSV's own EM1_num..EM5_num columns
# (S2 Data, doi:10.1371/journal.pone.0345759.s002), but that file carries NO
# item wording -- its headers are bare codes. The words come from the paper's
# Table 1, which numbers the ten items 1-10 and groups 6-10 under "Extrinsic
# Motivation" WITHOUT printing any item code. The shipped mapping is therefore
# an ORDER inference: em_1=item6, em_2=item7, em_3=item8, em_4=item9,
# em_5=item10 (mapping_basis=paper_order).
#
# Three things are tested here:
#  A (decisive, code identity): live em_i equals source EM{i}_num for all 45
#    respondents, and does so for exactly one source column each -- so the
#    integer-to-code half carries no inference.
#  B (decisive, option axis): the deposit ships each item twice, as a label
#    string (EMi) and an integer (EMi_num). The per-item crosstab must be
#    one-to-one with zero off-diagonal cells and must match the shipped
#    option_text/resp pairs (2=disagree, 3=ordinary, 4=agree, 5=strongly agree).
#  C (partial, item axis): the paper states items 6-8 were adapted from Asad et
#    al. [16], item 9 from Eom & Ashill [17] (grade-oriented) and item 10 from
#    Tsai et al. [18] (social recognition). Under the shipped mapping that
#    predicts a 3+1+1 structure in the live correlations.
#
# C does NOT establish the order WITHIN {em_1,em_2,em_3}; see the note at the
# end. Status recorded as PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "liang2026_extrinsic_motivation"
CACHE <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
SRC <- file.path(CACHE, "s002.csv")
if (!file.exists(SRC))
    download.file("https://doi.org/10.1371/journal.pone.0345759.s002", SRC, quiet = TRUE)
src <- read.csv(SRC, stringsAsFactors = FALSE)
src <- src[order(src$participant_id), ]

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(as.integer(w$id)), ]
items <- paste0("em_", 1:5)
cat("N respondents:", nrow(w), " (source rows:", nrow(src), ")\n")
cat("ids identical to source participant_id:",
    identical(as.integer(w$id), as.integer(src$participant_id)), "\n\n")

## --- A: code identity, live vs source columns -------------------------------
cat("A. exact column identity, live em_i vs source EM{j}_num (45 respondents):\n")
hit <- matrix(FALSE, 5, 5, dimnames = list(items, paste0("EM", 1:5, "_num")))
for (i in 1:5) for (j in 1:5)
    hit[i, j] <- identical(as.integer(w[[items[i]]]),
                           as.integer(src[[paste0("EM", j, "_num")]]))
print(hit)
A <- all(diag(hit)) && sum(hit) == 5
cat("A diagonal exact and unique:", A, "\n\n")

## --- B: option axis, label vs integer crosstab ------------------------------
shipped <- c("2" = "disagree", "3" = "ordinary", "4" = "agree", "5" = "strongly agree")
cat("B. per-item label x integer crosstab in the deposit (off-diagonal must be 0):\n")
B <- TRUE
for (i in 1:5) {
    tt <- table(src[[paste0("EM", i)]], src[[paste0("EM", i, "_num")]])
    cat("\n-- EM", i, " --\n", sep = "")
    print(tt)
    for (lv in colnames(tt)) {
        lab <- rownames(tt)[tt[, lv] > 0]
        if (length(lab) != 1 || !identical(lab, unname(shipped[lv]))) B <- FALSE
        if (sum(tt[, lv] > 0) != 1) B <- FALSE
    }
}
cat("\nB one-to-one and matching the shipped option_text/resp pairs:", B, "\n\n")

## --- C: 3+1+1 subscale-provenance structure ---------------------------------
R <- cor(w[, items])
cat("C. live inter-item correlations:\n"); print(round(R, 3))
rest <- sapply(items, function(v)
    cor(w[[v]], rowMeans(w[, setdiff(items, v), drop = FALSE])))
cat("\nitem-rest correlations:\n"); print(round(rest, 3))
block <- c(R["em_1","em_2"], R["em_1","em_3"], R["em_2","em_3"])
e4 <- c(R["em_4","em_1"], R["em_4","em_2"], R["em_4","em_3"])
e5 <- c(R["em_5","em_1"], R["em_5","em_2"], R["em_5","em_3"])
cat(sprintf("\nwithin {em_1,em_2,em_3}: min %.3f (%s)\n", min(block),
            paste(sprintf("%.2f", block), collapse = ", ")))
cat(sprintf("em_4 (item 9, Eom & Ashill) to that block: max %.3f, mean %.3f\n",
            max(e4), mean(e4)))
cat(sprintf("em_5 (item 10, Tsai)        to that block: max %.3f, mean %.3f\n",
            max(e5), mean(e5)))
p1 <- min(block) > max(e4) && min(block) > max(e5)
p2 <- which.min(rest) == 5
p3 <- mean(e4) > mean(e5)
cat(sprintf("C1 Asad block tighter than either outside item: %s\n", p1))
cat(sprintf("C2 em_5 lowest item-rest (%.3f vs next %.3f): %s\n",
            min(rest), sort(rest)[2], p2))
cat(sprintf("C3 em_4 closer to the block than em_5 (%.3f vs %.3f): %s\n",
            mean(e4), mean(e5), p3))

cat("\nNOTE -- what this does NOT establish: C separates the three Asad-sourced\n",
    "items from item 9 and item 10 and distinguishes those two from each other,\n",
    "but it cannot order em_1/em_2/em_3 among themselves -- all three come from\n",
    "one source scale and their pairwise r (0.77-0.83) are within noise at N=45.\n",
    "A permutation inside that triple would not be detected. The paper's own EFA\n",
    "(S1 Table) is not a stronger route: it does not reproduce on the deposited\n",
    "data. Hence PARTIAL.\n", sep = "")

cat(if (A && B && p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

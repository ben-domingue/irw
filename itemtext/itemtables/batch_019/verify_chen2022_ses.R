# verify_chen2022_ses.R -- re-runnable form of the Step 5b evidence for chen2022_ses.
#
# CLAIM UNDER TEST: the IRW item codes A25..A34 are the ten Rosenberg Self-Esteem
# Scale items in the instrument's canonical published order (A25 = RSES item 1,
# ... A34 = RSES item 10).
#
# The source file (Frontiers Data_Sheet_1, figshare 21515877) has bare column
# headers A1..A48 and no variable labels, and the paper reproduces no item
# wording, so the mapping is RECONSTRUCTED from the questionnaire's own
# numbering. What is testable is whether that numbering is canonical
# instrument order at all. It is, and the Children's Loneliness Scale block
# immediately before the RSES block proves it:
#
#   Asher et al. (1984) Loneliness and Social Dissatisfaction Questionnaire is
#   24 items, of which 8 are hobby/interest FILLERS at fixed positions
#   2, 5, 7, 11, 13, 15, 19, 23. The deposited file carries only 16 of A1..A24,
#   and the 8 it omits must be exactly that filler set if -- and only if -- the
#   A-numbers are canonical instrument positions. Chance probability of hitting
#   the right 8 of 24: 1 / choose(24,8) = 1/735471.
#
# It also checks the block boundaries the whole extraction rests on (A1-A24 on
# the CLS's 1-5 scale, A25-A34 on the RSES's 1-4, A35-A48 on the SASC's 1-3),
# and reports the scoring-direction finding that is why this table ships blank
# option_text.
#
# WHAT THIS DOES NOT ESTABLISH: nothing here distinguishes A27 from A28, or any
# other RSES item from any other. Canonical order for the block is an inference
# from the neighbouring block; per-item identity is unverified. Status PARTIAL.

suppressMessages(library(irw))

TABLE <- "chen2022_ses"
SRC   <- "https://ndownloader.figshare.com/files/38137143"  # Frontiers Data_Sheet_1
LSDQ_FILLERS <- c(2, 5, 7, 11, 13, 15, 19, 23)              # Asher et al. (1984)

raw <- read.csv(url(SRC), check.names = FALSE)
acols <- grep("^A[0-9]+$", names(raw), value = TRUE)
anum  <- as.integer(sub("^A", "", acols))

# --- 1. live item set (server-side aggregate, no export) -------------------
live <- irw::irw_table_sets(TABLE)
live_items <- sort(live$items)
cat("live item set:", paste(live_items, collapse = " "), "\n")
ok_live <- identical(sort(live_items), sort(paste0("A", 25:34)))
cat("  matches A25..A34 in the source file:", ok_live, "\n\n")

# --- 2. the filler-position test -------------------------------------------
cls_present <- sort(anum[anum <= 24])
cls_missing <- setdiff(1:24, cls_present)
cat("A-numbers 1-24 present in source file (", length(cls_present), "):",
    paste(cls_present, collapse = " "), "\n")
cat("A-numbers 1-24 ABSENT   (", length(cls_missing), "):",
    paste(cls_missing, collapse = " "), "\n")
cat("Asher (1984) LSDQ filler positions      :",
    paste(LSDQ_FILLERS, collapse = " "), "\n")
ok_fill <- identical(as.integer(cls_missing), as.integer(LSDQ_FILLERS))
cat("  identical:", ok_fill,
    sprintf("  (chance of this by accident: 1/%d)\n\n", choose(24, 8)))

# --- 3. block boundaries by response range ---------------------------------
blocks <- list(CLS = 1:24, SES = 25:34, SASC = 35:48)
expected_max <- c(CLS = 5, SES = 4, SASC = 3)
ok_blocks <- TRUE
cat(sprintf("%-6s %-9s %8s %8s %8s\n", "block", "A-range", "n_cols", "min", "max"))
for (b in names(blocks)) {
    cc <- acols[anum %in% blocks[[b]]]
    v  <- unlist(raw[cc], use.names = FALSE)
    cat(sprintf("%-6s %-9s %8d %8d %8d\n", b,
                paste0("A", min(blocks[[b]]), "-A", max(blocks[[b]])),
                length(cc), min(v, na.rm = TRUE), max(v, na.rm = TRUE)))
    if (max(v, na.rm = TRUE) != expected_max[[b]]) ok_blocks <- FALSE
}
cat("  each block's max equals its instrument's top scale point (5/4/3):",
    ok_blocks, "\n\n")

# --- 4. scoring direction inside the RSES block -----------------------------
ses <- raw[paste0("A", 25:34)]
cm  <- cor(ses, use = "pairwise.complete.obs")
off <- cm[upper.tri(cm)]
cat(sprintf("RSES block: %d of %d inter-item correlations positive (range %.2f to %.2f)\n",
            sum(off > 0), length(off), min(off), max(off)))
itemrest <- sapply(names(ses), function(v)
    cor(ses[[v]], rowSums(ses[setdiff(names(ses), v)]), use = "complete.obs"))
cat("item-rest correlations:\n")
print(round(itemrest, 3))
cat("A raw 5-positive/5-negative RSES cannot intercorrelate this way, so the\n",
    "deposited values are already keyed toward high self-esteem -- which means\n",
    "the paper's '1 = very conformity ... 4 = very inconformity' anchors do not\n",
    "apply uniformly across items. That is why option_text ships blank.\n",
    sprintf("A34 is the lone exception (item-rest r = %.3f); flagged, not resolved.\n\n",
            itemrest[["A34"]]), sep = "")

cat("Not established by any check above: which RSES item each of A25..A34 is,\n",
    "individually. The evidence pins the block and the numbering convention only.\n", sep = "")

cat(if (ok_live && ok_fill && ok_blocks) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

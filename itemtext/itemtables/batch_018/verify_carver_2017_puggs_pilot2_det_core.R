# verify_carver_2017_puggs_pilot2_det_core.R
#
# CLAIM UNDER TEST
#   Item codes Q1..Q9 in carver_2017_puggs_pilot2_det_core carry the Section 3
#   ("Knowledge about gene-environment interaction") statements of the PUGGS
#   questionnaire AS ADMINISTERED IN THE SECOND PILOT (PLOS ONE
#   10.1371/journal.pone.0169808, S1 Table questionnaire + S2 Text code book),
#   not the first pilot's Section 2 Part 2 wording (S3 Table, 13 items on a
#   4-point agreement scale), and resp = 1 marks the code book's keyed-correct
#   True/False choice for that item.
#
# Falsifiable predictions that validate_items.R cannot make:
#   A. PILOT boundary. Pilot-2 raw file (.s006) has 45 Q and 17 TT columns;
#      pilot-1 (.s005) has 51 and 20. The questionnaire we transcribed (S1
#      Table) numbers 45 items with 17 traits, so it is the pilot-2 form.
#   B. SCORING re-run. Re-running the IRW script's rule -- keep raw in {1,2},
#      resp = (raw == key) -- over source columns Q1..Q9 with the S2 Text code
#      book key must reproduce the live per-item n AND the live per-item number
#      correct, for all 9 items. Because no item sits at 50% correct, flipping
#      any single item's key changes that item's k, so this pins each item's
#      keyed truth value from the data.
#   C. TRUTH-VALUE consistency. Every stem shipped must be scientifically
#      consistent with the truth value the data-confirmed key encodes, and must
#      match the truth value S2 Table (the core-ideas document) independently
#      prints beside that same item number. Two documents, one numbering.
#   D. SEMANTIC COMPLEMENTS. The two items that share the referent "A person's
#      height" (Q4 one gene only / Q9 many different genes) and the two that
#      share "Most traits and diseases are caused by ..." (Q2 a single gene /
#      Q8 both genes and environmental factors) must be the mutually most
#      negatively correlated pairs in the raw True/False matrix.
#
# NOT ESTABLISHED by the statistics: within the False-keyed class, nothing here
# separates Q1, Q6 and Q7 from one another beyond difficulty plausibility.
# Their identity rests on the printed numbering -- which is a label match in
# three separate source documents (S1 Table prints "1".."9" in its own "Q."
# column beside each stem; S2 Table lists "corresponding items (and item
# number)"; S2 Text keys "Question 1 (Q1)"..."Q9") and on the fact that the raw
# file's columns are literally named Q1..Q9 and the processing script melts
# them unrenamed -- not on an order inference.

suppressMessages({library(irw); library(readxl)})

TABLE <- "carver_2017_puggs_pilot2_det_core"
ITEMS <- paste0("Q", 1:9)
KEY   <- c(Q1=2, Q2=2, Q3=1, Q4=2, Q5=1, Q6=2, Q7=2, Q8=1, Q9=1)  # S2 Text, Section 3
S2TAB <- c(Q1=2, Q2=2, Q3=1, Q4=2, Q5=1, Q6=2, Q7=2, Q8=1, Q9=1)  # S2 Table (core ideas)
STEM_IS_TRUE <- c(Q1=FALSE, Q2=FALSE, Q3=TRUE, Q4=FALSE, Q5=TRUE,
                  Q6=FALSE, Q7=FALSE, Q8=TRUE, Q9=TRUE)            # science of the shipped stem

cache <- file.path("..", "..", ".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)
get_supp <- function(id, dest) {
    if (!file.exists(dest))
        download.file(sprintf(paste0("https://journals.plos.org/plosone/article/file",
                                     "?type=supplementary&id=10.1371/journal.pone.0169808.s%s"), id),
                      dest, quiet = TRUE, mode = "wb")
    dest
}
p1 <- read_excel(get_supp("005", file.path(cache, "s005.xlsx")), sheet = "Sheet1")
p2 <- read_excel(get_supp("006", file.path(cache, "s006.xlsx")), sheet = "Sheet1")

## ---- A. pilot boundary -------------------------------------------------
nq1 <- sum(grepl("^Q[0-9]+$", names(p1))); nt1 <- sum(grepl("^TT[0-9]+", names(p1)))
nq2 <- sum(grepl("^Q[0-9]+$", names(p2))); nt2 <- sum(grepl("^TT[0-9]+", names(p2)))
cat("A. PILOT boundary\n")
cat(sprintf("   pilot-1 raw (.s005): %d Q columns, %d TT columns\n", nq1, nt1))
cat(sprintf("   pilot-2 raw (.s006): %d Q columns, %d TT columns\n", nq2, nt2))
cat("   S1 Table questionnaire (wording shipped): 45 items, 17 traits -> pilot 2\n")
cat("   S3 Table questionnaire (first pilot form): 51 items, 20 traits\n")
okA <- (nq1 == 51 && nt1 == 20 && nq2 == 45 && nt2 == 17)
cat(sprintf("   => shipped form is pilot 2's: %s\n\n", okA))

## ---- B. scoring re-run against live n and k ----------------------------
d <- irw::irw_fetch(TABLE)          # 583 rows; a few tens of kB, not a bulk export
cat("B. re-run of the IRW scoring rule over source columns Q1..Q9\n")
cat(sprintf("   %-4s %-6s %13s %13s %8s\n", "item", "key", "n src/live", "k src/live", "p"))
okB <- TRUE; okNo50 <- TRUE
for (it in ITEMS) {
    v <- suppressWarnings(as.numeric(p2[[it]])); v <- v[!is.na(v) & v %in% c(1, 2)]
    n_src <- length(v); k_src <- sum(v == KEY[[it]])
    lv <- d$resp[d$item == it]
    n_lv <- length(lv); k_lv <- sum(lv == 1)
    m <- (n_src == n_lv && k_src == k_lv)
    okB <- okB && m
    okNo50 <- okNo50 && (k_src != n_src - k_src)     # a flipped key would be detectable
    cat(sprintf("   %-4s %-6s %5d /%5d %5d /%5d %8.3f %s\n", it,
                ifelse(KEY[[it]] == 1, "True", "False"),
                n_src, n_lv, k_src, k_lv, k_lv / n_lv, ifelse(m, "", " <-- MISMATCH")))
}
cat(sprintf("   => all 9 items reproduce n and k exactly: %s\n", okB))
cat(sprintf("   => no item sits at 50%% correct, so a flipped key would show: %s\n\n", okNo50))

## ---- C. truth-value consistency across two documents and the science ---
cat("C. keyed truth value vs the shipped stem and vs S2 Table (core ideas)\n")
okC <- TRUE
for (it in ITEMS) {
    keyed_true <- (KEY[[it]] == 1)
    agree_doc  <- (KEY[[it]] == S2TAB[[it]])
    agree_sci  <- (keyed_true == STEM_IS_TRUE[[it]])
    okC <- okC && agree_doc && agree_sci
    cat(sprintf("   %-4s codebook=%-5s S2Table=%-5s shipped stem is scientifically %-5s  %s\n",
                it, ifelse(keyed_true, "True", "False"),
                ifelse(S2TAB[[it]] == 1, "True", "False"),
                ifelse(STEM_IS_TRUE[[it]], "True", "False"),
                ifelse(agree_doc && agree_sci, "ok", "<-- MISMATCH")))
}
cat(sprintf("   => 9/9 agree, so no permutation across truth classes is possible: %s\n\n", okC))

## ---- D. semantic complement pairs --------------------------------------
raw <- suppressWarnings(sapply(p2[ITEMS], as.numeric))
raw[!(raw %in% c(1, 2))] <- NA
C <- cor(raw, use = "pairwise.complete.obs")
argmin <- function(it) { r <- C[it, ]; r[it] <- NA; names(which.min(r)) }
cat("D. semantic complements (raw True/False codes)\n")
cat(sprintf("   r(Q4 'height ... one gene only', Q9 'height ... many genes')      = %+.3f\n", C["Q4","Q9"]))
cat(sprintf("   r(Q2 'most ... single gene',     Q8 'most ... genes and environ') = %+.3f\n", C["Q2","Q8"]))
cat(sprintf("   Q4 most-negative partner: %s ; Q9: %s\n", argmin("Q4"), argmin("Q9")))
cat(sprintf("   Q2 most-negative partner: %s ; Q8: %s\n", argmin("Q2"), argmin("Q8")))
okD <- (argmin("Q4") == "Q9" && argmin("Q9") == "Q4" &&
        argmin("Q2") == "Q8" && argmin("Q8") == "Q2")
cat(sprintf("   => both referent-sharing pairs are mutually most negative: %s\n", okD))
cat("   Difficulty also coheres: the two polygenicity items are the hardest\n")
cat(sprintf("     (Q9 p=%.2f, Q5 p=%.2f) and the gene-and-environment items the easiest\n",
            mean(d$resp[d$item=="Q9"]), mean(d$resp[d$item=="Q5"])))
cat(sprintf("     (Q2 p=%.2f, Q6 p=%.2f, Q8 p=%.2f); swapping Q5 and Q8 would invert that.\n\n",
            mean(d$resp[d$item=="Q2"]), mean(d$resp[d$item=="Q6"]), mean(d$resp[d$item=="Q8"])))

cat("Pins: the pilot version, the construct block (Section 3 = Q1..Q9), the\n")
cat("code<->source-column identity, each item's keyed truth value, and the two\n")
cat("referent-sharing complement pairs. Does NOT pin, on statistics alone, the\n")
cat("order among Q1/Q6/Q7 within the False-keyed class -- that rests on the\n")
cat("printed item numbers, which three source documents and the data column\n")
cat("names all carry.\n\n")

cat(if (okA && okB && okNo50 && okC && okD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

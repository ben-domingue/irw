# verify_mekheimer_2026_cai.R -- Step 5b, route 5 (subscale block structure).
#
# CLAIM UNDER TEST: the shipped item_text assigns CAI_1..CAI_9 to the CAI Scale's
# "Part A: Global Identity Alignment" block and CAI_10..CAI_18 to "Part B: Local
# Identity Alignment", following the item numbering 1-18 printed in the study's own
# questionnaire appendix (Additional file 4, 40862_2025_378_MOESM4_ESM.docx, tables
# "Part A" = items 1-9 and "Part B" = items 10-18).
#
# The falsifiable prediction: Part A items should cohere with each other and behave
# oppositely to Part B items (the two parts are worded as competing global vs local
# orientations). Any mapping that moved an item across the 9/10 boundary -- e.g. a
# shifted or concatenated-in-the-wrong-order transcription -- breaks it immediately.
#
# What this does NOT establish: the order WITHIN each block. The source publishes no
# per-item statistics for this 160-respondent deposit (its SPSS output files analyse a
# different, N=496 sample and report composites), so nothing separates CAI_3 from
# CAI_5. Hence the recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "mekheimer_2026_cai"
A <- paste0("CAI_", 1:9)    # Part A: Global Identity Alignment
B <- paste0("CAI_", 10:18)  # Part B: Local Identity Alignment

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
m <- cor(w[, c(A, B)], use = "pairwise.complete.obs")

wi <- function(g) { x <- m[g, g]; range(x[upper.tri(x)]) }
cr <- range(m[A, B])

cat(sprintf("n respondents: %d\n", nrow(w)))
cat(sprintf("within Part A (CAI_1..CAI_9)   r range: %+.2f to %+.2f\n", wi(A)[1], wi(A)[2]))
cat(sprintf("within Part B (CAI_10..CAI_18) r range: %+.2f to %+.2f\n", wi(B)[1], wi(B)[2]))
cat(sprintf("across Part A x Part B         r range: %+.2f to %+.2f\n", cr[1], cr[2]))

# Per-item: does each item correlate more strongly with its own block than the other?
bad <- character(0)
cat(sprintf("\n%-8s %6s %8s %8s %6s\n", "item", "block", "mean|r|own", "mean|r|oth", "ok"))
for (it in c(A, B)) {
    own <- if (it %in% A) setdiff(A, it) else setdiff(B, it)
    oth <- if (it %in% A) B else A
    ro <- mean(m[it, own]); rt <- mean(m[it, oth])
    ok <- ro > 0 && rt < 0
    if (!ok) bad <- c(bad, it)
    cat(sprintf("%-8s %6s %+8.2f %+8.2f %6s\n",
                it, if (it %in% A) "A" else "B", ro, rt, if (ok) "ok" else "FAIL"))
}

cat(sprintf("\nitems whose own-block mean r is positive AND cross-block mean r negative: %d/18\n",
            18 - length(bad)))
cat("Does NOT establish: within-block item order (no per-item published statistics exist\n",
    "for this 160-respondent deposit). Status recorded as PARTIAL.\n", sep = "")

cat(if (length(bad) == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

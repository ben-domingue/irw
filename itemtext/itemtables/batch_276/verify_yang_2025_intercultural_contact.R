# verify_yang_2025_intercultural_contact.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST: each live item code (FSM1..FSM3, FICA1..FICA6) carries the
# wording of the correspondingly numbered line of Part III of the study's own
# questionnaire (S1 File), and the 1..5 integers are the source workbook's own
# codes with Never..Always attached in ascending order.
#
# WHAT THIS SCRIPT CAN TEST: the tie between each live item code and its column
# in the source workbook (S2 File). data/yang_2025_intercultural.py melts named
# columns, so a permutation there would be the failure mode; all nine columns
# have distinct response-frequency vectors, so any swap between any two items
# breaks the match. Also that the integers were not recoded, and that the
# workbook's own "Final Score of FSM"/"FICA" composites confirm which columns
# form which block.
#
# WHAT IT CANNOT TEST: that questionnaire line FSM(1) is the column named FSM1
# rather than FSM2/FSM3 (and likewise within FICA). The paper publishes no
# per-item statistics, and the per-item means span only 2.88-3.22 with
# near-uniform distributions, so no statistical route separates the texts
# within a block. That step rests on the questionnaire printing the block code
# ("Foreign Social Media (FSM)") above a numbered list. Hence PARTIAL, not
# VERIFIED.

suppressMessages(library(irw))

TABLE <- "yang_2025_intercultural_contact"
ITEMS <- c("FSM1","FSM2","FSM3","FICA1","FICA2","FICA3","FICA4","FICA5","FICA6")
S2 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0316937.s002")

# --- source workbook (S2 File, "Intercultural Contact" sheet) ---
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(S2, tmp, quiet = TRUE, mode = "wb")
src <- as.data.frame(readxl::read_excel(tmp, sheet = "Intercultural Contact"))
names(src) <- trimws(names(src))

# --- live IRW table (1,170 rows; a negligible export) ---
d <- irw::irw_fetch(TABLE)

cat("Route 9 -- per item x response-level counts, source workbook vs live table\n")
cat(sprintf("%-6s %-22s %-22s %s\n", "item", "source 1/2/3/4/5", "live 1/2/3/4/5", "match"))
ok <- TRUE
src_mat <- matrix(NA_integer_, length(ITEMS), 5, dimnames = list(ITEMS, 1:5))
for (it in ITEMS) {
    s <- as.integer(table(factor(as.numeric(src[[it]]), levels = 1:5)))
    l <- as.integer(table(factor(d$resp[d$item == it],        levels = 1:5)))
    src_mat[it, ] <- s
    agree <- identical(s, l)
    ok <- ok && agree
    cat(sprintf("%-6s %-22s %-22s %s\n", it,
                paste(s, collapse = "/"), paste(l, collapse = "/"),
                if (agree) "yes" else "NO"))
}

# The counts only discriminate if no two items share a frequency vector.
dupes <- sum(duplicated(apply(src_mat, 1, paste, collapse = "/")))
cat(sprintf("\nDistinct frequency vectors among the 9 items: %d duplicated (0 means any\n",
            dupes))
cat("  swap between any two items would have shown up above).\n")

# --- Route 3: the workbook's own composite columns fix block membership ---
fsm_col  <- which(names(src) == "FSM")[1]
fica_col <- which(names(src) == "FICA")[1]
fsm_obs  <- rowMeans(sapply(c("FSM1","FSM2","FSM3"), function(i) as.numeric(src[[i]])))
fica_obs <- rowMeans(sapply(paste0("FICA", 1:6),     function(i) as.numeric(src[[i]])))
fsm_dev  <- max(abs(as.numeric(src[[fsm_col]])  - fsm_obs))
fica_dev <- max(abs(as.numeric(src[[fica_col]]) - fica_obs))
cat(sprintf("\nRoute 3 -- workbook composites vs recomputed block means (n=%d rows)\n", nrow(src)))
cat(sprintf("  'FSM'  column  vs mean(FSM1..FSM3):  max |dev| = %.4f\n", fsm_dev))
cat(sprintf("  'FICA' column  vs mean(FICA1..FICA6): max |dev| = %.4f\n", fica_dev))
blocks_ok <- fsm_dev < 0.005 && fica_dev < 0.005

# --- Weak, not relied on: per-item means in the live table ---
cat("\nRoute 8 (weak, reported not relied on) -- live per-item means:\n")
m <- tapply(d$resp, d$item, mean)[ITEMS]
cat(paste(sprintf("  %-6s %.3f", names(m), m), collapse = "\n"), "\n")
cat("  FSM text 3.200 > voice 3.038 > video 2.877 is the ordering the modalities\n")
cat("  predict, but the spread is 0.32 on a near-uniform distribution and the six\n")
cat("  FICA means span 3.031-3.223; this separates nothing.\n")

cat("\nNOT ESTABLISHED: which questionnaire line within a block goes with which\n")
cat("index (FSM1 vs FSM2 vs FSM3; the six FICA lines). No published per-item\n")
cat("statistic exists for this scale, so that rests on the questionnaire's own\n")
cat("printed numbering under the block heading, not on the data. PARTIAL.\n")

cat(if (ok && blocks_ok && dupes == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

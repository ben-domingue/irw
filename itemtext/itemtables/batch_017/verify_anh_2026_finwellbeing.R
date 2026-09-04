# verify_anh_2026_finwellbeing.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: live item code FWk carries the wording printed on row FWk of
# PLOS ONE 10.1371/journal.pone.0340002 Table 3 ("Financial well-being (FW) [39]"
# block, seven rows FW1-FW7, bounded above by the FB9 row and below by the
# "Financial literacy (FL) [40]" header).
#
# The chain has two links:
#   (a) paper row FWk  <-> S1 File column FWk   -- a literal code-label match in
#       the paper's own "Variable code" column; not numeric, stated not proved here.
#   (b) S1 File column FWk <-> live item FWk    -- THIS is what the script tests.
#       data/anh_2026_finwellbeing.py melts the S1 CSV with var_name="item", so a
#       shuffled or shifted column->code assignment is the failure mode that would
#       put one item's wording on another's responses. If FW3's and FW5's columns
#       had been swapped anywhere in that path, the per-item response
#       distributions below would swap with them.
#
# Method: full 7 x 5 response-frequency cross-tab, source file vs live table,
# cell for cell (Step 5b route 9). Live counts come from a server-side GROUP BY,
# never irw_fetch() -- the corpus is under an export quota.

suppressMessages(library(irw))

TABLE <- "anh_2026_finwellbeing"
ITEMS <- paste0("FW", 1:7)
S1_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0340002.s001")

# Counts read from S1 File (306 respondents) on 2026-09-03; rows = FW1..FW7,
# columns = resp 1..5. Hard-coded so this script stays checkable offline, and
# re-derived from the live download when the network is available.
S1 <- matrix(c(
    21,  81, 108,  79, 17,
    18,  82, 113,  72, 21,
    24,  68, 117,  79, 18,
    14,  83, 115,  69, 25,
    18,  73, 123,  72, 20,
    20,  79, 109,  82, 16,
    20,  73, 129,  67, 17), nrow = 7, byrow = TRUE,
    dimnames = list(ITEMS, 1:5))

# --- re-derive S1 from the deposit if reachable -------------------------------
s1_live <- try({
    raw <- read.csv(S1_URL)
    m <- t(sapply(ITEMS, function(it) as.integer(table(factor(raw[[it]], levels = 1:5)))))
    dimnames(m) <- dimnames(S1); m
}, silent = TRUE)
if (inherits(s1_live, "try-error")) {
    cat("NOTE: S1 File not reachable; using the hard-coded 2026-09-03 counts.\n\n")
} else {
    cat("S1 File re-downloaded; matches hard-coded counts: ",
        all(s1_live == S1), "\n\n", sep = "")
    if (!all(s1_live == S1)) S1 <- s1_live
}

# --- live counts, server-side -------------------------------------------------
sets <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
qfun <- utils::getFromNamespace(".irw_query_tibble", "irw")
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                   "CAST(resp AS STRING) AS resp, COUNT(*) AS n",
                   "FROM `%s` WHERE resp IS NOT NULL GROUP BY item, resp"),
             sets$table)
d <- as.data.frame(qfun(q))
LIVE <- matrix(0L, 7, 5, dimnames = dimnames(S1))
for (i in seq_len(nrow(d))) LIVE[as.character(d$item[i]), as.character(d$resp[i])] <- as.integer(d$n[i])

cat("response-frequency cross-tab (S1 File deposit -> live IRW table)\n")
cat(sprintf("%-5s %25s %25s  %s\n", "item", "S1 (1,2,3,4,5)", "live (1,2,3,4,5)", "match"))
ok_cells <- TRUE
for (it in ITEMS) {
    same <- all(S1[it, ] == LIVE[it, ])
    ok_cells <- ok_cells && same
    cat(sprintf("%-5s %25s %25s  %s\n", it,
                paste(S1[it, ], collapse = ","),
                paste(LIVE[it, ], collapse = ","),
                if (same) "OK" else "MISMATCH"))
}

# --- the cross-tab is only evidence if it separates the items -----------------
# A permutation of the seven codes is detectable only where no two items share a
# frequency vector. Check every pair, and report the closest one.
pairs_equal <- 0L
min_l1 <- Inf; closest <- ""
for (a in 1:6) for (b in (a + 1):7) {
    l1 <- sum(abs(S1[a, ] - S1[b, ]))
    if (l1 == 0) pairs_equal <- pairs_equal + 1L
    if (l1 < min_l1) { min_l1 <- l1; closest <- paste(ITEMS[a], "vs", ITEMS[b]) }
}
cat(sprintf("\nidentical frequency vectors among the 21 item pairs: %d\n", pairs_equal))
cat(sprintf("closest pair: %s, L1 distance %d (a swap of these two would move %d cells)\n",
            closest, min_l1, min_l1))

ok <- ok_cells && pairs_equal == 0L
cat(sprintf("\n35 of 35 cells match: %s; every item separated from every other: %s\n",
            ok_cells, pairs_equal == 0L))
cat("Does NOT establish: link (a), paper row FWk <-> S1 column FWk. That rests on\n",
    "the paper printing the code 'FW1'..'FW7' in its own Variable code column\n",
    "against the same names the S1 CSV header uses -- a label match, which no\n",
    "statistic here can add to. Nor does it check the transcribed wording itself,\n",
    "which was OCR'd from the Table 3 image.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

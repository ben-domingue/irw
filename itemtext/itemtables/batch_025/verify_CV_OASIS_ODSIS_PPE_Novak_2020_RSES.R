# verify_CV_OASIS_ODSIS_PPE_Novak_2020_RSES.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes RSES_1 .. RSES_10 are the source spreadsheets' own column
# names (data/CV_OASIS_ODSIS_PPE_Novak_2020.R melts `starts_with("RSES")` out of
# ex.dataset.csv / pa.dataset.csv with no rename), and those ten columns are the
# Rosenberg Self-Esteem Scale in the WIDELY CIRCULATED (Morris Rosenberg
# Foundation / UMD) item order, i.e.
#   RSES_1  "On the whole, I am satisfied with myself."                       (+)
#   RSES_2  "At times, I think I am no good at all."                          (-)
#   RSES_3  "I feel that I have a number of good qualities."                  (+)
#   RSES_4  "I am able to do things as well as most other people."            (+)
#   RSES_5  "I feel I do not have much to be proud of."                       (-)
#   RSES_6  "I certainly feel useless at times."                              (-)
#   RSES_7  "I feel that I'm a person of worth ..."                           (+)
#   RSES_8  "I wish I could have more respect for myself."                    (-)
#   RSES_9  "All in all, I am inclined to feel that I am a failure."          (-)
#   RSES_10 "I take a positive attitude toward myself."                       (+)
# and that the live table stores RAW responses coded 1 = "Strongly agree" ...
# 4 = "Strongly disagree".
#
# THREE FALSIFIABLE PREDICTIONS.
#
# (1) ROUTE 6, keying polarity. That version is reverse-keyed at positions
#     2, 5, 6, 8, 9 and nowhere else -- 1 of C(10,5) = 252 possible 5-subsets.
#     The study's own analysis script (OSF osf.io/k5bvs, CZ_short_OASIS_ODSIS.Rmd
#     lines 220-224 and 286-290) independently reverses exactly RSES_2, RSES_5,
#     RSES_6, RSES_8, RSES_9. So in the raw live table those five and only those
#     five must correlate NEGATIVELY with RSES_1.
#
# (2) RESPONSE DIRECTION. The .Rmd applies TWO recodes: it reverses
#     {2,5,6,8,9}, then reverses ALL ten "to indicate that higher RSES score
#     refers to higher self-esteem". Net: {1,3,4,7,10} flipped, {2,5,6,8,9}
#     unchanged. That chain is only self-consistent if the raw coding runs
#     1 = strongly agree ... 4 = strongly disagree AND {1,3,4,7,10} are the
#     positively worded items -- which is what this file ships. The test:
#     define score_i = resp for i in {2,5,6,8,9} and 5 - resp otherwise, and
#     require every one of the ten scored means to exceed 2.0 (i.e. this
#     community sample has above-midpoint self-esteem on every item). Under the
#     opposite direction every scored mean would fall below 2.0.
#
# (3) ROUTE 7, marker item. In the scored metric the least-endorsed RSES item in
#     general samples is "I wish I could have more respect for myself" -- the
#     item this file places at RSES_8 -- and the two best-endorsed are the
#     competence/qualities pair, placed at RSES_3 and RSES_4. Require RSES_8 to
#     be the strict minimum by a clear margin and {RSES_3, RSES_4} to be the top
#     two.
#
# WHAT THIS DOES NOT ESTABLISH: it pins the reverse-keyed CLASS {2,5,6,8,9},
# the response direction, the position of RSES_8, and the {RSES_3, RSES_4} pair
# as a pair. It CANNOT separate RSES_3 from RSES_4, RSES_1 from RSES_10, or
# RSES_2 / RSES_5 / RSES_6 / RSES_9 from one another -- no per-item statistics
# for the Czech RSES are published anywhere in the deposit or the paper.
# Hence PARTIAL, not VERIFIED.
#
# Everything below is a server-side aggregate query (no table export).

suppressMessages(library(redivis))

TBL <- "`datapages.item_response_warehouse:as2e:v47_0.cv_oasis_odsis_ppe_novak_2020_rses:8jkr`"

REVERSE   <- c(2, 5, 6, 8, 9)   # study .Rmd rescoring list AND the circulated RSES keying
ITEM_TEXT <- c("On the whole, I am satisfied with myself.",
               "At times, I think I am no good at all.",
               "I feel that I have a number of good qualities.",
               "I am able to do things as well as most other people.",
               "I feel I do not have much to be proud of.",
               "I certainly feel useless at times.",
               "I feel that I'm a person of worth ...",
               "I wish I could have more respect for myself.",
               "All in all, I am inclined to feel that I am a failure.",
               "I take a positive attitude toward myself.")

piv <- paste0("WITH w AS (SELECT id, ",
              paste(sprintf('MAX(IF(item="RSES_%d", resp, NULL)) AS i%d', 1:10, 1:10),
                    collapse = ", "),
              " FROM ", TBL, " GROUP BY id)")
sel <- paste(c(sprintf("CORR(i1,i%d) AS c1_%d", 2:10, 2:10),
               sprintf("AVG(i%d) AS m%d", 1:10, 1:10)), collapse = ", ")

r <- as.data.frame(redivis::query(paste0(piv, " SELECT ", sel, " FROM w"))$to_data_frame())

cor1  <- c(NA, as.numeric(r[1, sprintf("c1_%d", 2:10)]))
raw_m <- as.numeric(r[1, sprintf("m%d", 1:10)])
scored <- ifelse(seq_len(10) %in% REVERSE, raw_m, 5 - raw_m)

cat(sprintf("%-8s %-56s %10s %8s %8s %s\n",
            "item", "shipped item_text", "cor w/ i1", "raw m", "scored m", "keyed"))
for (i in 1:10)
    cat(sprintf("%-8s %-56s %10s %8.2f %8.2f %s\n",
                paste0("RSES_", i), ITEM_TEXT[i],
                if (i == 1) "  (self)" else sprintf("%+.3f", cor1[i]),
                raw_m[i], scored[i], if (i %in% REVERSE) "reverse" else "forward"))

obs_rev <- which(cor1 < 0)
cat(sprintf("\n(1) negatively correlated with RSES_1: {%s}\n",
            paste(obs_rev, collapse = ", ")))
cat(sprintf("    study .Rmd rescoring list + circulated RSES reverse positions: {%s}\n",
            paste(REVERSE, collapse = ", ")))
ok_polarity <- setequal(obs_rev, REVERSE)
cat(sprintf("    polarity classes agree (1 of 252 subsets): %s\n", ok_polarity))

ok_dir <- all(scored > 2.0)
cat(sprintf("\n(2) all ten scored means above the 2.0 midpoint: %s (min %.2f, max %.2f)\n",
            ok_dir, min(scored), max(scored)))
cat("    => raw 1 = 'Strongly agree' ... 4 = 'Strongly disagree', as shipped.\n")

lo <- order(scored)[1]
top2 <- sort(order(scored, decreasing = TRUE)[1:2])
margin <- sort(scored)[2] - sort(scored)[1]
cat(sprintf("\n(3) lowest scored item: RSES_%d (%.2f), margin to next %.2f\n",
            lo, scored[lo], margin))
cat(sprintf("    top two scored items: {%s}\n",
            paste(sprintf("RSES_%d", top2), collapse = ", ")))
ok_marker <- lo == 8L && margin > 0.2 && setequal(top2, c(3L, 4L))
cat(sprintf("    marker prediction (min = RSES_8 by >0.2, top two = {3,4}): %s\n", ok_marker))

cat("\nDoes NOT establish: RSES_3 vs RSES_4, RSES_1 vs RSES_10, or the order\n")
cat("within {RSES_2, RSES_5, RSES_6, RSES_9}.\n")
cat(if (ok_polarity && ok_dir && ok_marker) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

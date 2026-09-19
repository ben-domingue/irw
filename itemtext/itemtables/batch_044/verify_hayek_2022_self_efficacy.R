# verify_hayek_2022_self_efficacy.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST: the IRW item codes se1..se5 are the deposited SPSS columns
# S_eff_1..S_eff_5 of the study's S1 Dataset, in that order -- which is what
# data/hayek_2022_attitude.py asserts positionally and what the shipped item_text
# (S1 File questionnaire items 1.9-1.13, in order) depends on.
#
# The falsifiable prediction: for every item, the live table's count of each of
# the five resp levels must equal that .sav column's count, cell for cell. The
# five columns' distributions are mutually distinct, so any permutation of the
# codes breaks the match.
#
# WHAT THIS DOES NOT ESTABLISH: which questionnaire wording belongs to which
# S_eff_n column. The .sav's variable labels are bare ("self-efficacy_1".."_5"),
# so that half of the mapping rests on the S1 File's printed block order and is
# recorded as PARTIAL in verification_hayek_2022_self_efficacy.csv.

suppressMessages(library(irw))

TABLE <- "hayek_2022_self_efficacy"
LEVELS <- c(-2, -1, 0, 1, 2)

# Counts read from journal.pone.0265595.s001 (S1 Dataset .sav), columns
# S_eff_1..S_eff_5, via pyreadstat. Hard-coded so this runs without the .sav.
SAV <- rbind(
  S_eff_1 = c(23, 80, 128,  92, 22),
  S_eff_2 = c(11, 53, 123, 128, 30),
  S_eff_3 = c(13, 27, 103, 175, 27),
  S_eff_4 = c(33, 69, 112, 120, 11),
  S_eff_5 = c(40, 87, 102, 103, 13)
)
colnames(SAV) <- as.character(LEVELS)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
items <- paste0("se", 1:5)

obs <- t(sapply(items, function(it)
  as.integer(table(factor(d$resp[d$item == it], levels = LEVELS)))))
colnames(obs) <- as.character(LEVELS)

cat("live table counts (item x resp):\n"); print(obs)
cat("\nS1 Dataset .sav counts (S_eff_n x value):\n"); print(SAV)

diffs <- obs - SAV
cat("\ncell-by-cell differences (live - sav):\n"); print(diffs)
ok_cells <- all(diffs == 0)
cat(sprintf("\n%d of %d cells match exactly\n", sum(diffs == 0), length(diffs)))

# Uniqueness: no OTHER assignment of the five .sav columns to the five codes works.
perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i)
    lapply(perms(v[-i]), function(p) c(v[i], p))))
n_ok <- sum(sapply(perms(1:5), function(p) all(obs == SAV[p, , drop = FALSE])))
cat(sprintf("permutations of the 5 .sav columns reproducing the live counts: %d (of 120)\n", n_ok))

cat("\nNOTE: this pins se_n <-> S_eff_n for every item. It does NOT pin which\n",
    "questionnaire wording is which -- the .sav labels are bare, so the text-to-\n",
    "number tie rests on S1 File order (items 1.9-1.13). Status is PARTIAL.\n", sep = "")

cat(if (ok_cells && n_ok == 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

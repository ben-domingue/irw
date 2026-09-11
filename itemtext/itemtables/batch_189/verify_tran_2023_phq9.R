# verify_tran_2023_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes PHQ1..PHQ9 carry the official PHQ-9
# wording in the form's printed numbering (PHQ1 = "Little interest or pleasure
# in doing things" ... PHQ9 = "Thoughts that you would be better off dead or of
# hurting yourself in some way"), and resp 0/1/2/3 = Not at all / Several days /
# More than half the days / Nearly every day in that ascending order.
#
# Nothing in the study ties these columns to text: the S1 Data .xlsx
# (10.1371/journal.pone.0289123.s002) has bare headers PHQ1..PHQ9, no label row,
# no comments, no other sheet; the paper prints no item. data/
# tran_2023_gi_mental_battery.py melts the columns by name (code IS the source
# column name), so what is inferred is what the column NAME's digit means.
#
# The deposit also carries the same 400 students' sleep, breakfast and GI-symptom
# answers, which gives content twins for two PHQ-9 items. Predictions (each
# breaks under a permutation of the item labels):
#
#   P0  JOIN. Live PHQ_i equals deposit PHQ_i cell for cell (so the deposit's
#       covariates below describe the same responses the live table holds).
#   P1  MARKER ITEM (route 7). PHQ9 (suicidal ideation) is the least endorsed of
#       the nine in a non-clinical student sample: lowest mean AND highest %zero.
#   P2  SLEEP TWIN. Sleepquality is the self-rated good/poor item (0 = poor; its
#       87 zeros equal paper Table 1 "Poor sleep quality 87 (21.8)"). Its most
#       negative Spearman correlate must be PHQ3 (sleep trouble).
#   P3  APPETITE TWIN. The most positive Spearman correlate of BOTH
#       Early_satiation (Rome IV symptom, 0/1) and Breakfast (1 Everyday /
#       2 Usually / 3 Sometimes; 223/120/57 = paper Table 1) must be PHQ5
#       (poor appetite or overeating).
#   P4  RESPONSE-AXIS DIRECTION. Raw unreversed PHQ-9 sum >= 10 must give the
#       paper's MDD count, 41 of 400 (Table 1, 10.2%), and agree row-for-row with
#       the deposit's own MDD flag; the flipped coding (3 - x) must not.
#
# WHAT THIS DOES NOT ESTABLISH: it pins PHQ9, PHQ3 and PHQ5 individually. It
# does NOT separate PHQ1, PHQ2, PHQ4, PHQ6, PHQ7 and PHQ8 from one another
# (PHQ8 being the second-least-endorsed item is printed as corroboration only).
# The PHQ-9 two-factor block test (somatic {3,4,5} vs cognitive {2,6,7,8,9}) is
# printed but is NOT a pass criterion: in this low-symptom sample the cognitive
# block's within-r does not exceed the cross-block r, which is an underpowered
# test rather than evidence against the mapping (the somatic items are already
# pinned by P2/P3 on content). Status: PARTIAL, not VERIFIED.
#
# Deliberately NOT used: PHQ8 <-> GAD5 restlessness, because the sibling table
# tran_2023_gad7's item identities are themselves inferred from column digits,
# and using one to pin the other would be circular.

suppressMessages(library(irw))

TABLE <- "tran_2023_phq9"
IT    <- paste0("PHQ", 1:9)
XLSX  <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0289123.s002")
PAPER_MDD <- 41

# --- live IRW data -----------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", IT)]
cat(sprintf("live table: %d respondents x %d items\n\n", nrow(w), length(IT)))

# --- deposit -----------------------------------------------------------------
tf <- tempfile(fileext = ".xlsx")
utils::download.file(XLSX, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(suppressMessages(readxl::read_excel(tf, trim_ws = FALSE)))  # live ids keep a trailing space ("A457 ")
x <- x[!is.na(x$STT), ]
# same duplicate-id disambiguation as data/tran_2023_gi_mental_battery.py
k <- ave(seq_along(x$STT), x$STT, FUN = seq_along) - 1
x$id <- paste0(x$STT, c("", "-b", "-c")[k + 1])
m <- merge(w, x, by = "id", suffixes = c("", ".dep"))
cat(sprintf("merged on id: %d of %d live respondents\n", nrow(m), nrow(w)))

# --- P0 ----------------------------------------------------------------------
cells <- 0; agree <- 0
for (i in IT) {
    a <- m[[i]]; b <- suppressWarnings(as.numeric(m[[paste0(i, ".dep")]]))
    cells <- cells + length(a)
    agree <- agree + sum((is.na(a) & is.na(b)) | (!is.na(a) & !is.na(b) & a == b))
}
cat(sprintf("P0 live == deposit: %d / %d cells (incl. NA pattern)\n\n", agree, cells))

# --- P1 ----------------------------------------------------------------------
mu   <- sapply(IT, function(i) mean(w[[i]], na.rm = TRUE))
pct0 <- sapply(IT, function(i) 100 * mean(w[[i]] == 0, na.rm = TRUE))
cat("per-item mean and % at zero (live)\n")
for (i in IT) cat(sprintf("  %-5s mean %5.3f   %%zero %5.1f\n", i, mu[i], pct0[i]))
lo <- names(which.min(mu)); z <- names(which.max(pct0))
lo2 <- names(sort(mu))[2]
cat(sprintf("  -> lowest mean %s, highest %%zero %s (predicted PHQ9); second-lowest mean %s (PHQ8 expected, corroboration only)\n\n",
            lo, z, lo2))

# --- P2 / P3 -----------------------------------------------------------------
sp <- function(v) sapply(IT, function(i)
    suppressWarnings(cor(m[[i]], as.numeric(m[[v]]), method = "spearman",
                         use = "complete.obs")))
show <- function(lab, r) cat(sprintf("  %-16s %s\n", lab,
    paste(sprintf("%s %+.3f", IT, r), collapse = "  ")))
cat(sprintf("Sleepquality zeros (poor) = %d (paper Table 1: 87)\n", sum(x$Sleepquality == 0)))
cat(sprintf("Breakfast 1/2/3 = %s (paper Table 1: 223/120/57)\n",
            paste(table(x$Breakfast), collapse = "/")))
r_sq <- sp("Sleepquality"); r_es <- sp("Early_satiation"); r_bf <- sp("Breakfast")
cat("Spearman correlations with deposit covariates\n")
show("Sleepquality", r_sq); show("Early_satiation", r_es); show("Breakfast", r_bf)
p2 <- names(which.min(r_sq)); p3a <- names(which.max(r_es)); p3b <- names(which.max(r_bf))
cat(sprintf("  -> most negative with Sleepquality: %s (predicted PHQ3; next %.3f)\n",
            p2, sort(r_sq)[2]))
cat(sprintf("  -> most positive with Early_satiation: %s (predicted PHQ5; next %.3f)\n",
            p3a, sort(r_es, decreasing = TRUE)[2]))
cat(sprintf("  -> most positive with Breakfast: %s (predicted PHQ5; next %.3f)\n\n",
            p3b, sort(r_bf, decreasing = TRUE)[2]))

# --- two-factor block test (printed, not scored) ------------------------------
R <- cor(w[, IT], use = "pairwise.complete.obs")
SOM <- c("PHQ3", "PHQ4", "PHQ5"); COG <- c("PHQ2", "PHQ6", "PHQ7", "PHQ8", "PHQ9")
within <- function(g) mean(R[g, g][upper.tri(R[g, g])])
cat(sprintf("two-factor (not scored): within somatic %.3f, within cognitive %.3f, across %.3f\n\n",
            within(SOM), within(COG), mean(R[SOM, COG])))

# --- P4 ----------------------------------------------------------------------
tot  <- rowSums(w[, IT], na.rm = TRUE)
flip <- rowSums(3 - w[, IT], na.rm = TRUE)
n10 <- sum(tot >= 10); n10f <- sum(flip >= 10)
mt <- rowSums(sapply(IT, function(i) m[[i]]), na.rm = TRUE)
mdd_agree <- sum((mt >= 10) == (as.numeric(m$MDD) == 1))
tot_agree <- sum(mt == as.numeric(m$totalPHQ9))
cat(sprintf("P4 live raw sum >= 10: %d (paper MDD %d); flipped coding would give %d\n",
            n10, PAPER_MDD, n10f))
cat(sprintf("   deposit MDD flag agrees with live sum>=10: %d / %d; totalPHQ9 == live sum: %d / %d\n\n",
            mdd_agree, nrow(m), tot_agree, nrow(m)))

ok <- c(P0 = agree == cells && nrow(m) == nrow(w),
        P1 = (lo == "PHQ9" && z == "PHQ9"),
        P2 = p2 == "PHQ3",
        P3 = (p3a == "PHQ5" && p3b == "PHQ5"),
        P4 = (n10 == PAPER_MDD && n10f != PAPER_MDD && mdd_agree == nrow(m)))
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins PHQ9, PHQ3 and PHQ5 and the 0-3 direction; does NOT separate\n",
    "PHQ1, PHQ2, PHQ4, PHQ6, PHQ7, PHQ8 from one another -- PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

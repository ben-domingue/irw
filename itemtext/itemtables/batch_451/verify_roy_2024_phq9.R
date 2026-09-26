# verify_roy_2024_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: live codes phq1..phq9 carry the canonical PHQ-9 wording in the
# form's printed numbering (phq1 = "Little interest or pleasure in doing things" ...
# phq9 = "Thoughts that you would be better off dead or of hurting yourself in some
# way"), and resp 0/1/2/3 = Not at all / Several days / More than half the days /
# Nearly every day, ascending.
#
# The PLOS S1 Appendix (journal.pone.0315687.s001.xlsx, one sheet) carries bare
# column headers phq1..phq9 with numeric 0-3 cells and no codebook; the paper names
# the PHQ-9 but prints no item. data/roy_2024_fgid_screeners.py melts the columns by
# name, so the IRW code IS the source column name -- what is inferred is that column
# phqN is PHQ-9 item N.
#
# Predictions:
#   P0  live table == deposit: per-item x level counts of live phq1..9 equal the S1
#       xlsx cell for cell (ties the deposit-side numbers below to the live table;
#       not itself mapping evidence).
#   P1  MARKER (route 7): phq9 (suicidal ideation) has the lowest mean AND the
#       highest share of zeros of the nine, in a student sample.
#   P2  RESP DIRECTION: the deposit's phq_sc equals the raw row sum of phq1..9, and
#       phq_cat reproduces the PHQ-9's published severity bands (0-4 minimal, 5-9
#       mild, 10-14 moderate, 15-19 moderately severe, 20-27 severe) with zero
#       disagreements; phq9 >= 60% at 0 (a reversed coding would put that share at
#       "Nearly every day" thoughts of death). The paper states "'0' (not at all) to
#       '3' (nearly every day)".
#   Descriptive only (printed, NOT part of the verdict): the item correlation matrix,
#       which in this deposit is weak and does not show the usual PHQ-9 structure.
#
# WHAT THIS DOES NOT ESTABLISH: pins phq9 individually and the response direction.
# It does NOT separate phq1..phq8 from one another. Status: PARTIAL.

suppressMessages(library(irw))

TABLE <- "roy_2024_phq9"
IT <- paste0("phq", 1:9)
URL <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0315687.s001&type=supplementary"

d <- as.data.frame(irw::irw_fetch(TABLE))
cat(sprintf("live table: %d rows, %d respondents\n", nrow(d), length(unique(d$id))))
live_tab <- table(factor(d$item, IT), factor(d$resp, 0:3))

tf <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tf))
w <- as.data.frame(lapply(x[, IT], function(v) suppressWarnings(as.numeric(v))))
dep_tab <- t(sapply(IT, function(i) table(factor(w[[i]], 0:3))))
p0 <- all(as.matrix(unclass(live_tab)) == dep_tab)
cat("\nP0 per-item level counts (0/1/2/3), live vs deposit\n")
for (i in IT) cat(sprintf("  %-5s live %s | deposit %s\n", i,
    paste(live_tab[i, ], collapse = "/"), paste(dep_tab[i, ], collapse = "/")))
cat(sprintf("  -> identical: %s\n\n", p0))

mu <- colMeans(w, na.rm = TRUE); z <- colMeans(w == 0, na.rm = TRUE) * 100
cat("P1 per-item mean / %zero\n")
for (i in IT) cat(sprintf("  %-5s mean %.3f  %%zero %.1f\n", i, mu[i], z[i]))
p1 <- names(which.min(mu)) == "phq9" && names(which.max(z)) == "phq9"
o <- order(mu)
cat(sprintf("  -> lowest mean %s (%.3f), next %s (%.3f); highest %%zero %s (predicted phq9): %s\n\n",
    IT[o[1]], mu[o[1]], IT[o[2]], mu[o[2]], names(which.max(z)), p1))

sc <- suppressWarnings(as.numeric(x$phq_sc)); rs <- rowSums(w)
ok <- !is.na(sc) & !is.na(rs)
sum_match <- sum(rs[ok] == sc[ok])
band <- as.character(cut(sc, c(-1, 4, 9, 14, 19, 27),
    labels = c("Minimal depression", "Mild depression", "Moderate depression",
               "Moderately severe depression", "Severe depression")))
cat_ok <- !is.na(x$phq_cat) & ok
band_match <- sum(band[cat_ok] == x$phq_cat[cat_ok])
cat(sprintf("P2 phq_sc == row sum: %d / %d; phq_cat == PHQ-9 severity band: %d / %d; phq9 %%zero %.1f\n",
    sum_match, sum(ok), band_match, sum(cat_ok), z["phq9"]))
p2 <- sum_match == sum(ok) && band_match == sum(cat_ok) && z["phq9"] >= 60
cat(sprintf("  -> %s\n\n", p2))

cat("Descriptive (not in verdict): inter-item correlations\n")
print(round(cor(w, use = "pairwise"), 2))
cat("\nNot established: the order among phq1..phq8 -- no per-item statistics are\n",
    "published and the correlation structure is too weak to pin positions.\n", sep = "")

cat(if (p0 && p1 && p2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

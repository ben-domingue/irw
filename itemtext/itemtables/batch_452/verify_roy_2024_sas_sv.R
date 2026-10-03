# verify_roy_2024_sas_sv.R -- Step 5b mapping evidence, re-runnable.
# (Copied from references/verify_template.R and adapted.)
#
# CLAIM UNDER TEST: live codes sas1..sas10 carry the SAS-SV wording in the order
# Kwon et al. (2013) number it (PLoS ONE 8(12):e83558, Appendix S1 / Table 3:
# 1 missing planned work ... 10 people around me say I use it too much), and
# resp 1..6 = Strongly disagree .. Strongly agree, ascending.
#
# The Roy et al. (2024) S1 Appendix xlsx has bare headers sas1..sas10 with numeric
# 1-6 cells and no labels; data/roy_2024_fgid_screeners.py melts the columns by
# name, so the IRW code IS the source column name. What is inferred is that
# column sasN is SAS-SV item N.
#
# Predictions:
#   P0  live table == deposit: per-item x level counts equal the S1 xlsx cell for
#       cell (ties the deposit-side numbers to the live table; not itself mapping
#       evidence).
#   P1  RESP DIRECTION: (a) deposit sas_sc equals the raw row sum of sas1..10, so
#       the stored integers are the ones the authors scored with their stated
#       1 = strongly disagree .. 6 = strongly agree; (b) sas_sc correlates
#       positively (> 0.15) with the same deposit's PHQ-9, ISI and PSS-4 totals,
#       as smartphone addiction does in the literature -- a reversed coding would
#       flip all three signs. (PHQ direction was pinned in batch_451.)
#   P2  BLOCK STRUCTURE (route 5): SAS-SV items 1-3 are the daily-life-disturbance
#       items (missed work, concentration, wrist/neck pain) and items 4-7 the
#       withdrawal items (can't stand not having it, impatient, in my mind, never
#       give up). Each of these seven items must correlate more, on average, with
#       its own block than with the other block.
#   Descriptive only (NOT in verdict): Spearman between live item means and Kwon
#       2013 Table 3 means (Korean adolescents, N=540 -- a different population).
#
# WHAT THIS DOES NOT ESTABLISH: P2 separates the two blocks but not order within
# a block (1 vs 2 vs 3; 4..7), and items 8, 9, 10 are singletons pinned by nothing
# item-specific. sas3's margin is thin (0.31 own vs ~0.30 rival). Status: PARTIAL.

suppressMessages(library(irw))

TABLE <- "roy_2024_sas_sv"
IT <- paste0("sas", 1:10)
URL <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0315687.s001&type=supplementary"

d <- as.data.frame(irw::irw_fetch(TABLE))
cat(sprintf("live table: %d rows, %d respondents\n", nrow(d), length(unique(d$id))))
live_tab <- table(factor(d$item, IT), factor(d$resp, 1:6))

tf <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tf))
w <- as.data.frame(lapply(x[, IT], function(v) suppressWarnings(as.numeric(v))))
dep_tab <- t(sapply(IT, function(i) table(factor(w[[i]], 1:6))))
p0 <- all(as.matrix(unclass(live_tab)) == dep_tab)
cat("\nP0 per-item level counts (1..6), live vs deposit\n")
for (i in IT) cat(sprintf("  %-5s live %s | deposit %s\n", i,
    paste(live_tab[i, ], collapse = "/"), paste(dep_tab[i, ], collapse = "/")))
cat(sprintf("  -> identical (60 cells): %s\n\n", p0))

sc <- suppressWarnings(as.numeric(x$sas_sc)); rs <- rowSums(w)
ok <- !is.na(sc) & !is.na(rs)
sum_match <- sum(rs[ok] == sc[ok])
cat(sprintf("P1a sas_sc == raw row sum of sas1..10: %d / %d\n", sum_match, sum(ok)))
ext <- sapply(c("phq_sc", "isi_sc", "pss_sc"), function(k)
    cor(sc, suppressWarnings(as.numeric(x[[k]])), use = "complete.obs"))
cat("P1b r(sas_sc, other screener totals) -- smartphone addiction is expected to\n",
    "    correlate POSITIVELY with depression, insomnia and stress; a reversed\n",
    "    1..6 coding would flip all three signs:\n", sep = "")
for (k in names(ext)) cat(sprintf("    %-7s %+.3f\n", k, ext[k]))
p1 <- sum_match == sum(ok) && sum(ok) > 1000 && all(ext > 0.15)
cat(sprintf("  -> %s\n\n", p1))

# Descriptive (NOT in verdict): the deposit's sas_cat does NOT follow the cut-offs
# the paper's Methods state (31/33 and 40); it follows <=21 not addicted, 22..31
# (male) / 22..33 (female) high risk, above that addicted -- and the paper's
# Table 1 (35 / 148 / 836) reports the deposit's categories.
g <- trimws(tolower(x$gender)); cat_obs <- trimws(x$sas_cat)
cat("Descriptive: sas_sc range by gender x deposit sas_cat\n")
print(aggregate(sc ~ g + cat_obs, FUN = function(v) c(min = min(v), max = max(v), n = length(v))))
cat("\n")

r <- cor(w, use = "pairwise")
G <- list(disturbance = paste0("sas", 1:3), withdrawal = paste0("sas", 4:7))
cat("P2 mean r with own block vs other block\n")
p2 <- TRUE
for (k in names(G)) for (i in G[[k]]) {
    own <- mean(r[i, setdiff(G[[k]], i)])
    oth <- mean(r[i, G[[setdiff(names(G), k)]]])
    cat(sprintf("  %-5s own(%s) %.3f  other %.3f  %s\n", i, k, own, oth,
                if (own > oth) "ok" else "MISS"))
    p2 <- p2 && own > oth
}
cat(sprintf("  -> %s\n\n", p2))

KWON <- c(2.78, 2.56, 2.72, 2.40, 2.12, 2.28, 2.19, 2.49, 3.02, 2.70)
mu <- colMeans(w, na.rm = TRUE)
cat("Descriptive (not in verdict): live mean vs Kwon 2013 Table 3 mean\n")
for (j in seq_along(IT)) cat(sprintf("  %-5s %.3f  %.2f\n", IT[j], mu[j], KWON[j]))
cat(sprintf("  Spearman = %.3f\n", cor(mu, KWON, method = "spearman")))
cat("\nNot established: order within each block, and positions of sas8/9/10.\n")

cat(if (p0 && p1 && p2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

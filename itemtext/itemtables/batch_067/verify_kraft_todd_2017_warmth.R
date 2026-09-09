# verify_kraft_todd_2017_warmth.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: WARM1..WARM4 are the four warmth adjectives of the paper's
# 9-item warmth/competence scale (S2 File, "Warmth/competence" block), taken in
# the order the S2 File lists them: Tolerant, Warm, Sincere, Good natured
# (competence takes the other five: Competent, Confident, Independent,
# Competitive, Intelligent). mapping_basis = paper_order.
#
# Data: the study's own S3 File (the exact input to data/kraft_todd_2017_empathic_nonverbal.py),
# so no Redivis export is burned. Its WARM1..WARM4 columns ARE the live item codes.
#
# Two falsifiable predictions, plus one that is deliberately not made.

suppressMessages(library(readxl))

SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0177758.s003")
f <- file.path(tempdir(), "kt2017_s003.xlsx")
if (!file.exists(f)) download.file(SI, f, quiet = TRUE, mode = "wb")
d <- as.data.frame(read_excel(f))

W <- c("WARM1", "WARM2", "WARM3", "WARM4")
TXT <- c(WARM1 = "Tolerant", WARM2 = "Warm", WARM3 = "Sincere", WARM4 = "Good natured")

care <- rowMeans(d[, paste0("CARE", 1:10)], na.rm = TRUE)

cat(sprintf("%-6s %-13s %6s %6s %6s %8s %8s %8s\n",
            "item", "shipped text", "n", "DNA", "mean", "r(condemp)", "r(CARE)", "M_emp-M_un"))
res <- data.frame()
for (w in W) {
    x <- d[[w]]; ok <- !is.na(x)
    r_emp <- cor(x[ok], d$condemp[ok])
    okc <- ok & is.finite(care)
    r_care <- cor(x[okc], care[okc])
    delta <- mean(x[ok & d$condemp == 1]) - mean(x[ok & d$condemp == 0])
    cat(sprintf("%-6s %-13s %6d %6d %6.2f %10.3f %8.3f %8.2f\n",
                w, TXT[[w]], sum(ok), sum(!ok), mean(x[ok]), r_emp, r_care, delta))
    res <- rbind(res, data.frame(item = w, n_dna = sum(!ok), r_emp = r_emp, r_care = r_care))
}
rownames(res) <- res$item

cat("\n-- Prediction 1: WARM1 = 'Tolerant' --\n")
cat("Tolerant is the one warmth adjective that is not an empathic display and is the\n",
    "hardest to judge from a photo+script, so it should draw the most 'Does not apply'\n",
    "(dropped as NA) and be the LEAST tied to the empathy manipulation and to CARE.\n", sep = "")
p1 <- res["WARM1", "n_dna"] == max(res$n_dna) &&
      res["WARM1", "r_emp"] == min(res$r_emp) &&
      res["WARM1", "r_care"] == min(res$r_care)
cat(sprintf("  DNA: %s  (max = %d)\n", paste(res$n_dna, collapse = "/"), max(res$n_dna)))
cat(sprintf("  r(condemp): %s  (min = %.3f)\n", paste(sprintf("%.3f", res$r_emp), collapse = "/"), min(res$r_emp)))
cat(sprintf("  r(CARE):    %s  (min = %.3f)\n", paste(sprintf("%.3f", res$r_care), collapse = "/"), min(res$r_care)))
cat(sprintf("  -> %s\n", if (p1) "holds on all three" else "FAILS"))

cat("\n-- Prediction 2: WARM2 = 'Warm' --\n")
cat("'Warm' is the adjective the empathy manipulation targets most directly and the one\n",
    "the CARE empathy measure is nearest to, so it should top r(condemp) and r(CARE).\n", sep = "")
p2 <- res["WARM2", "r_emp"] == max(res$r_emp) && res["WARM2", "r_care"] == max(res$r_care)
cat(sprintf("  r(condemp) max = %.3f at %s ; r(CARE) max = %.3f at %s\n",
            max(res$r_emp), res$item[which.max(res$r_emp)],
            max(res$r_care), res$item[which.max(res$r_care)]))
cat(sprintf("  -> %s\n", if (p2) "holds" else "FAILS"))

cat("\n-- Prediction 3: option_text direction (resp 1 = 'not at all', 5 = 'very much') --\n")
cat("The empathic condition must score HIGHER if larger integers mean 'very much'.\n")
p3 <- all(sapply(W, function(w) {
    x <- d[[w]]; ok <- !is.na(x)
    mean(x[ok & d$condemp == 1]) > mean(x[ok & d$condemp == 0])
}))
cat(sprintf("  raw range in the source file: %d..%d (5 levels), live table 1..5\n",
            min(unlist(d[, W]), na.rm = TRUE), max(unlist(d[, W]), na.rm = TRUE)))
cat(sprintf("  -> %s\n", if (p3) "all 4 items higher under empathic nonverbal behavior" else "FAILS"))

cat("\nWhat this does NOT establish: WARM3 vs WARM4 are not separated.\n",
    "'Sincere' and 'Good natured' differ by only r(condemp) 0.591 vs 0.521 and\n",
    "r(CARE) 0.762 vs 0.753, with no published per-item statistics to break the tie,\n",
    "so their assignment rests on S2 File listing order alone. Status is PARTIAL.\n", sep = "")

cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

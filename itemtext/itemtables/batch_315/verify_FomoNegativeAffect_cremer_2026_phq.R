# verify_FomoNegativeAffect_cremer_2026_phq.R -- Step 5b mapping check (batch_315).
#
# Claim: phq1_m..phq9_m are canonical PHQ-9 items 1..9 (Kroenke et al., 2001), in
# canonical order. The deposit carries no labels and the paper does not print the
# items, so the mapping is inferred from the code numbering. Falsifiable predictions:
#   (a) Subscale membership. Elhai & Casale (2026) score a 3-item somatic factor
#       (Krause et al., 2008: canonical items 3 sleep, 4 fatigue, 5 appetite) and a
#       6-item cognitive/affective factor. Table 1 publishes Somatic M=3.59 SD=2.56,
#       Cog/Aff M=3.80 SD=3.74; Table 2 splits by sex (men 3.06/2.37, 3.18/3.27;
#       women 3.91/2.62, 4.17/3.96). Sum {phq3,phq4,phq5} and the other six from the
#       live table and compare; also check that {3,4,5} is the ONLY triple of the 84
#       that reproduces the published somatic mean and SD.
#   (b) Marker item: canonical item 9 (suicidal ideation) must be the least endorsed.
# Does NOT establish: order within the somatic triple (3/4/5) or within the six
# cognitive/affective items 1,2,6,7,8 beyond item 9 -- hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "FomoNegativeAffect_cremer_2026_phq"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
sex <- tapply(d$cov_sex, d$id, function(x) x[1])[as.character(w$id)]
ok <- TRUE

som <- rowSums(w[, paste0("phq", 3:5, "_m")])
cog <- rowSums(w[, paste0("phq", c(1, 2, 6:9), "_m")])
chk <- function(lbl, x, M, S) {
  cat(sprintf("%-28s published %5.2f (%4.2f)  observed %5.2f (%4.2f)\n", lbl, M, S, mean(x), sd(x)))
  abs(mean(x) - M) <= 0.006 && abs(sd(x) - S) <= 0.006
}
cat(sprintf("n respondents = %d; cov_sex table: %s\n", nrow(w), paste(names(table(sex)), table(sex), collapse = ", ")))
ok <- chk("Somatic {3,4,5} all", som, 3.59, 2.56) & ok
ok <- chk("Cog/Aff {1,2,6-9} all", cog, 3.80, 3.74) & ok
# men n=172 per paper; identify the sex code with 172 respondents
men <- names(which(table(sex) == 172)); women <- setdiff(names(table(sex)), men)
cat("sex code with n=172 (men per paper):", men, "\n")
ok <- chk("Somatic men", som[sex == men], 3.06, 2.37) & ok
ok <- chk("Somatic women", som[sex == women], 3.91, 2.62) & ok
ok <- chk("Cog/Aff men", cog[sex == men], 3.18, 3.27) & ok
ok <- chk("Cog/Aff women", cog[sex == women], 4.17, 3.96) & ok

cat("\nAll 84 triples: which reproduce somatic M=3.59 & SD=2.56 (to 0.006)?\n")
hits <- c()
for (cmb in combn(1:9, 3, simplify = FALSE)) {
  x <- rowSums(w[, paste0("phq", cmb, "_m")])
  if (abs(mean(x) - 3.59) <= 0.006 && abs(sd(x) - 2.56) <= 0.006) hits <- c(hits, paste(cmb, collapse = ","))
}
cat("  matching triples:", if (length(hits)) paste(hits, collapse = " | ") else "none", "\n")
ok <- ok && identical(hits, "3,4,5")

mn <- sort(colMeans(w[, paste0("phq", 1:9, "_m")]))
cat("\nItem means ascending:\n"); print(round(mn, 3))
cat("Least endorsed item:", names(mn)[1], "(canonical item 9 = suicidal ideation expected)\n")
ok <- ok && names(mn)[1] == "phq9_m"

cat("\nNot established: order within {3,4,5} and within {1,2,6,7,8}; subscale route + marker only.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

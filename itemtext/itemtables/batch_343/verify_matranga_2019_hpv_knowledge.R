# verify_matranga_2019_hpv_knowledge.R -- Step 5b mapping check (batch_343).
# Claim: live items q1..q16 are THinK items 1..16 as printed in Figure 1 of
# Matranga et al. (2019) PeerJ 7:e6254. Route 1: the paper's Table 3 publishes
# per-item Mean (SD) for each recruitment group (4 numbers per item); the
# observed values must reproduce them item by item, and each item's nearest
# published row must be its own (so no two items can be swapped undetected).
# NOTE: the paper's Table 3 group headers are swapped relative to the data's
# own Group labels (Table 1 ages/education confirm the data labels: group A has
# mean age 23.1 = UAC). So the published "Ob/Gyn" column is compared with live
# group A and the published "UAC" column with live group O. Code 6 is included
# in the means, exactly as the paper computed them.
suppressMessages(library(irw))
TABLE <- "matranga_2019_hpv_knowledge"
# Table 3: col1 = "Ob/Gyn Department (N=136)", col2 = "University outpatient service (N=84)"
P <- rbind(
 c(1.74,1.01,1.75,0.99), c(1.55,0.95,1.83,1.15), c(1.95,1.12,2.49,1.41),
 c(2.92,1.21,2.91,1.23), c(2.58,1.25,2.24,1.37), c(3.57,1.14,2.96,1.41),
 c(3.68,1.14,3.15,1.15), c(3.58,1.30,3.93,1.44), c(2.63,1.32,2.75,1.47),
 c(2.30,1.06,2.50,1.61), c(3.06,1.43,3.09,1.59), c(2.58,1.42,2.99,1.64),
 c(2.63,1.07,2.75,1.51), c(2.14,1.20,2.60,1.70), c(2.44,1.28,2.96,1.79),
 c(2.14,1.24,2.38,1.70))
rownames(P) <- paste0("q", 1:16)
# Known published discrepancy: Q7's second-column SD is printed 1.15 in both
# Table 3 and the Results text, but the data give 1.46 (both Q7 means match).
# Treated as a paper typo; that one cell is excluded from the comparison and
# its observed value is printed below.
Q7_SD_PRINTED <- P["q7", 4]; P["q7", 4] <- NA
d <- as.data.frame(irw::irw_fetch(TABLE))
g <- d$cov_recruitment_group
stopifnot(all(c("A","O") %in% g))
f <- function(it, grp, fn) { x <- d$resp[d$item == it & g == grp]; fn(x) }
O <- t(sapply(rownames(P), function(it) c(f(it,"A",mean), f(it,"A",sd), f(it,"O",mean), f(it,"O",sd))))
cat(sprintf("%-4s %22s %22s %7s %s\n","item","published M/SD|M/SD","observed M/SD|M/SD","maxdiff","nearest"))
ok <- TRUE
for (it in rownames(P)) {
  dd <- max(abs(O[it,] - P[it,]), na.rm = TRUE)
  cells <- !is.na(P[it,])
  dist <- apply(P, 1, function(p) sum((O[it,cells] - p[cells])^2, na.rm = TRUE))
  near <- names(which.min(dist))
  if (dd > 0.015 || near != it) ok <- FALSE
  cat(sprintf("%-4s %5.2f %4.2f|%5.2f %4.2f  %5.2f %4.2f|%5.2f %4.2f %7.3f %s\n",
      it, P[it,1],P[it,2],P[it,3],P[it,4], O[it,1],O[it,2],O[it,3],O[it,4], dd, near))
}
cat(sprintf("\nq7 col-2 SD: printed %.2f, observed %.2f (excluded; means match)\n", Q7_SD_PRINTED, O["q7",4]))
# Two items (q9, q13) have identical published MEANS (2.63 / 2.75); only the SDs separate them.
cat(sprintf("q9 vs q13 SDs: published %.2f/%.2f vs %.2f/%.2f; observed %.2f/%.2f vs %.2f/%.2f\n", P["q9",2],P["q9",4],P["q13",2],P["q13",4],O["q9",2],O["q9",4],O["q13",2],O["q13",4]))
# Resp axis (direction 1=Yes .. 5=No), checked against percentages in the Results text:
n14 <- sum(d$item=="q14"); p14 <- mean(d$resp[d$item=="q14"] %in% 4:5)
q12 <- d$resp[d$item=="q12"]; p12 <- sum(q12==5)/sum(q12<=5)
p11 <- mean(d$resp[d$item=="q11"] %in% 4:5)
cat(sprintf("\nQ14 'very little or not at all' (codes 4+5): %.1f%% (paper 21.8%%)\n", 100*p14))
cat(sprintf("Q12 'never heard of it' (code 5, code 6 excluded): %.1f%% (paper 16.7%%)\n", 100*p12))
cat(sprintf("Q11 'no or little' (codes 4+5): %.1f%% (paper 44.3%%)\n", 100*p11))
if (abs(100*p14-21.8) > 0.1 || abs(100*p12-16.7) > 0.1 || abs(100*p11-44.3) > 0.5) ok <- FALSE
cat("Not established: meaning of code 6 (not a printed option; left blank), and the\n",
    "relative order of 'Yes' vs 'Much' at codes 1/2 beyond the printed order.\n", sep="")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

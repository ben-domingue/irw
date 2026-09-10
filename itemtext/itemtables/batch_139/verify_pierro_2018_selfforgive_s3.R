# verify_pierro_2018_selfforgive_s3.R -- re-runnable Step 5b evidence.
#
# CLAIM UNDER TEST: the four item codes carry the wording printed in Pierro et al.
# (2018) PLOS ONE 13(3):e0193357, Study 1 Measures, in listed order --
#   sforgiver1 = "I feel... rejecting of myself" (R)
#   sforgive2  = "I feel... accepting of myself"
#   sforgiver3 = "I feel... dislike toward myself" (R)
#   sforgive4  = "I feel... forgiving myself"
# Two falsifiable predictions follow, and both would break if the negative and
# positive items were interchanged:
#   (A) POLARITY. sforgiver1/sforgiver3 are the negatively-worded pair, so they
#       must correlate positively with each other and NEGATIVELY with
#       sforgive2/sforgive4 in the raw (un-reversed) data.
#   (B) COMPOSITE. Reversing exactly those two items (5 - x) and averaging must
#       reproduce the paper's published Study 3 self-forgiveness composite,
#       M = 3.14, SD = .59, alpha = .74 (Results, Study 3). Reversing the OTHER
#       pair instead must miss it.
# What this does NOT establish: nothing here separates sforgiver1 from
# sforgiver3, or sforgive2 from sforgive4 -- those rest on the code index
# agreeing with the paper's listing position. Status is therefore PARTIAL.

suppressMessages(library(irw))
TABLE <- "pierro_2018_selfforgive_s3"
PUB_M <- 3.14; PUB_SD <- 0.59; PUB_A <- 0.74; TOL_M <- 0.02; TOL_SD <- 0.02

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
its <- c("sforgiver1","sforgive2","sforgiver3","sforgive4")
w <- w[stats::complete.cases(w[, its]), ]
cat("respondents with complete data:", nrow(w), "\n\n")

cat("--- (A) polarity: raw inter-item correlations ---\n")
r <- stats::cor(w[, its])
print(round(r, 3))
neg_pair <- r["sforgiver1","sforgiver3"]
cross <- c(r["sforgiver1","sforgive2"], r["sforgiver1","sforgive4"],
           r["sforgiver3","sforgive2"], r["sforgiver3","sforgive4"])
pos_pair <- r["sforgive2","sforgive4"]
cat(sprintf("\nr(sforgiver1,sforgiver3) = %+.3f   (predicted > 0)\n", neg_pair))
cat(sprintf("r(sforgive2,sforgive4)   = %+.3f   (predicted > 0)\n", pos_pair))
cat(sprintf("cross-polarity r range   = %+.3f .. %+.3f   (predicted all < 0)\n\n",
            min(cross), max(cross)))
ok_pol <- neg_pair > 0 && pos_pair > 0 && all(cross < 0)

cat("--- (B) composite vs published M/SD/alpha ---\n")
alpha <- function(m) { k <- ncol(m); (k/(k-1))*(1 - sum(apply(m,2,var))/var(rowSums(m))) }
scored <- w[, its]; scored$sforgiver1 <- 5 - scored$sforgiver1; scored$sforgiver3 <- 5 - scored$sforgiver3
flip   <- w[, its]; flip$sforgive2   <- 5 - flip$sforgive2;     flip$sforgive4   <- 5 - flip$sforgive4
cm <- rowMeans(scored); fm <- rowMeans(flip)
cat(sprintf("%-34s %8s %8s %8s\n", "", "mean", "sd", "alpha"))
cat(sprintf("%-34s %8.2f %8.2f %8.2f\n", "published (paper, Study 3)", PUB_M, PUB_SD, PUB_A))
cat(sprintf("%-34s %8.2f %8.2f %8.2f\n", "reverse r1 & r3 (our mapping)", mean(cm), sd(cm), alpha(scored)))
cat(sprintf("%-34s %8.2f %8.2f %8.2f\n", "reverse 2 & 4 (swapped polarity)", mean(fm), sd(fm), alpha(flip)))
ok_comp <- abs(mean(cm) - PUB_M) < TOL_M && abs(sd(cm) - PUB_SD) < TOL_SD &&
           abs(mean(fm) - PUB_M) > TOL_M
cat(sprintf("\nour-mapping |dM| = %.3f, |dSD| = %.3f ; swapped |dM| = %.3f\n",
            abs(mean(cm)-PUB_M), abs(sd(cm)-PUB_SD), abs(mean(fm)-PUB_M)))
cat("\npolarity check:", if (ok_pol) "PASS" else "FAIL",
    "| composite check:", if (ok_comp) "PASS" else "FAIL", "\n")
cat(if (ok_pol && ok_comp) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

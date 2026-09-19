# verify_zhang_2024_parasocial.R -- Step 5b mapping check for zhang_2024_parasocial.
#
# Claim: live PSI1/PSI2/PSI3 carry the S1 Appendix 'Parasocial interaction' items
# 1/2/3 respectively (mapping_basis=paper_order).
#
# Route: paper Table 2 (Zhang & Liu 2024, PLOS ONE e0296908) prints standardized CFA
# loadings PSI1=0.696, PSI2=0.865, PSI3=0.796 from the six-construct, 23-item CFA.
# We (a) refit that CFA on the study's S1 dataset (.s002 xlsx) and compare loadings,
# and (b) check the live IRW PSI columns are the S1 columns of the same name,
# id-for-id, so the Table-2 loadings attach to the live codes.
#
# What this does NOT establish: the tie between Table 2's code PSI<k> and the S1
# Appendix's k-th numbered wording. The appendix lists the items as a numbered list
# under a construct heading without printing codes; that step is presentation order
# (paper_order) and is untestable from the data. Hence status PARTIAL.

suppressMessages({library(irw); library(readxl); library(lavaan)})

TABLE <- "zhang_2024_parasocial"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0296908.s002"
PUBLISHED <- c(PSI1 = 0.696, PSI2 = 0.865, PSI3 = 0.796)
TOL <- 0.01

tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))

m <- "ATR=~ATR1+ATR2+ATR3+ATR4
EXP=~EXP1+EXP2+EXP3
PSI=~PSI1+PSI2+PSI3
VDSP=~VDSP1+VDSP2+VDSP3+VDSP4+VDSP5+VDSP6
SDSP=~SDSP1+SDSP2+SDSP3+SDSP4
INT=~INT1+INT2+INT3"
fit <- cfa(m, data = s1)
ss <- standardizedSolution(fit)
ss <- ss[ss$op == "=~" & ss$lhs == "PSI", ]
obs <- setNames(ss$est.std, ss$rhs)[names(PUBLISHED)]

cat("(a) Table 2 loadings vs refit on S1 dataset\n")
cat(sprintf("%-6s %10s %10s %8s\n", "item", "published", "refit", "diff"))
for (k in names(PUBLISHED))
  cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", k, PUBLISHED[k], obs[k], obs[k] - PUBLISHED[k]))
worst <- max(abs(obs - PUBLISHED))
# every permutation other than identity must fit worse than tolerance
perms <- list(c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
best_other <- min(sapply(perms, function(p) max(abs(obs[p] - PUBLISHED))))
cat(sprintf("largest deviation (identity): %.3f; best non-identity permutation: %.3f\n", worst, best_other))

cat("\n(b) live IRW PSI<k> vs S1 column PSI<k>, id-for-id\n")
d <- irw::irw_fetch(TABLE)
ok_b <- TRUE
for (k in names(PUBLISHED)) {
  lv <- d[d$item == k, c("id", "resp")]
  agree <- sapply(names(PUBLISHED), function(j) {
    s <- s1[match(lv$id, s1$Number), j]
    sum(s == lv$resp, na.rm = TRUE)
  })
  cat(sprintf("live %s: n=%d; agreement with S1 PSI1/PSI2/PSI3 = %s\n",
              k, nrow(lv), paste(agree, collapse = "/")))
  if (agree[k] != nrow(lv) || any(agree[names(agree) != k] == nrow(lv))) ok_b <- FALSE
}

cat("\nNot established: Table-2 code PSI<k> <-> S1 Appendix item k (presentation order).\n")
pass <- worst <= TOL && best_other > TOL && ok_b
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

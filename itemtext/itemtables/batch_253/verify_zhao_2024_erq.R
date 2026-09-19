# verify_zhao_2024_erq.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST. zhao_2024_erq ships Gross & John's (2003) canonical English
# ERQ wording against the deposit's own column names ERQr1, ERQs2, ERQr3, ERQs4,
# ERQr5, ERQs6, ERQr7, ERQr8, ERQs9, ERQr10 (data/zhao_2024_erq.py melts them by
# name, so the item code IS the S1 column name -- no positional step). The S1
# workbook carries no item text, and neither the paper nor any supplement prints
# item wording, so the code -> text tie rests on (i) the number in each code being
# the ERQ's printed item number and (ii) the r/s letter being the subscale.
#
# TEST 1 -- the r/s partition is a property of the DATA, not just of the codes.
#   Among all 210 ways to split the ten items 6/4, the canonical
#   reappraisal={1,3,5,7,8,10} / suppression={2,4,6,9} split should maximise
#   mean within-block minus mean between-block inter-item correlation.
# TEST 2 -- the paper's own item numbering Q1..Q10 is the code numbering.
#   Refit the paper's CFA (two correlated factors, MLM estimator, as in Mplus) on
#   the live data and compare standardised loadings with Table 3 for Model 1-10
#   and Model 2-8 (Q1, Q3 dropped), plus Table 2's chi-square/df and Table 4's
#   alphas and factor correlation.
#
# WHAT THIS DOES NOT ESTABLISH: that paper item Qk carries canonical ERQ wording k
# WITHIN a subscale. The paper never prints wording. The subscale of every item is
# pinned (Test 1), items 1 and 3 are pinned as the pair the ERQ-8 literature drops
# (canonical items 1 and 3, Balzarotti), but nothing in the data separates, e.g.,
# the near-parallel reappraisal items 5/7/8/10 or suppression items 2/4/6/9 by
# wording. Hence PARTIAL.

suppressMessages({library(irw); library(lavaan)})

TABLE <- "zhao_2024_erq"
REA <- c(1, 3, 5, 7, 8, 10); SUP <- c(2, 4, 6, 9)
code <- function(k) paste0("ERQ", ifelse(k %in% REA, "r", "s"), k)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, code(1:10)]
names(X) <- paste0("Q", 1:10)
cat(sprintf("live: %d respondents x %d items, complete cases %d\n",
            nrow(X), ncol(X), sum(complete.cases(X))))

## ---- TEST 1 -------------------------------------------------------------
R <- cor(X)
score <- function(a) {
  b <- setdiff(1:10, a)
  wi <- c(R[a, a][upper.tri(R[a, a])], R[b, b][upper.tri(R[b, b])])
  be <- R[a, b]
  mean(wi) - mean(be)
}
subs <- combn(1:10, 6, simplify = FALSE)
sc <- sapply(subs, score); o <- order(-sc)
cat("\nTEST 1: within-minus-between mean r, top 3 of 210 six-item splits:\n")
for (i in o[1:3]) cat(sprintf("  {%-16s}  %.4f\n", paste(subs[[i]], collapse = ","), sc[i]))
can <- which(sapply(subs, function(s) identical(as.numeric(s), REA)))
cat(sprintf("canonical {1,3,5,7,8,10}: %.4f, rank %d\n", sc[can], which(o == can)))
cat(sprintf("mean r within reappraisal %.3f, within suppression %.3f, between %.3f\n",
            mean(R[REA, REA][upper.tri(R[REA, REA])]),
            mean(R[SUP, SUP][upper.tri(R[SUP, SUP])]), mean(R[REA, SUP])))
t1 <- which(o == can) == 1L

## ---- TEST 2 -------------------------------------------------------------
m10 <- 'rea =~ Q1 + Q3 + Q5 + Q7 + Q8 + Q10
        sup =~ Q2 + Q4 + Q6 + Q9'
m8  <- 'rea =~ Q5 + Q7 + Q8 + Q10
        sup =~ Q2 + Q4 + Q6 + Q9'
f10 <- cfa(m10, X, estimator = "MLM")
f8  <- cfa(m8,  X, estimator = "MLM")
ld <- function(f) { s <- standardizedSolution(f); s <- s[s$op == "=~", ]; setNames(s$est.std, s$rhs) }
l10 <- ld(f10); l8 <- ld(f8)
PUB10 <- c(Q1=.553, Q3=.620, Q5=.643, Q7=.813, Q8=.840, Q10=.736, Q2=.573, Q4=.590, Q6=.757, Q9=.681)
PUB8  <- c(Q5=.624, Q7=.795, Q8=.875, Q10=.735, Q2=.573, Q4=.590, Q6=.757, Q9=.681)
cat("\nTEST 2: standardised loadings, paper Table 3 vs refit on live data\n")
cat(sprintf("%-4s %8s %8s %8s | %8s %8s %8s\n", "item", "pub10", "obs10", "diff", "pub8", "obs8", "diff"))
for (q in names(PUB10))
  cat(sprintf("%-4s %8.3f %8.3f %8.3f | %8s %8s %8s\n", q, PUB10[q], l10[q], l10[q] - PUB10[q],
              ifelse(q %in% names(PUB8), sprintf("%.3f", PUB8[q]), "-"),
              ifelse(q %in% names(PUB8), sprintf("%.3f", l8[q]), "-"),
              ifelse(q %in% names(PUB8), sprintf("%.3f", l8[q] - PUB8[q]), "-")))
worst <- max(abs(l10[names(PUB10)] - PUB10), abs(l8[names(PUB8)] - PUB8))
cat(sprintf("largest loading deviation: %.4f\n", worst))
fm10 <- fitMeasures(f10, c("chisq.scaled", "df")); fm8 <- fitMeasures(f8, c("chisq.scaled", "df"))
cat(sprintf("Table 2 chi-square/df: Model 1-10 pub 132.219/34 obs %.3f/%d ; Model 2-8 pub 43.010/19 obs %.3f/%d\n",
            fm10[1], fm10[2], fm8[1], fm8[2]))
alpha <- function(Y) { k <- ncol(Y); v <- var(Y); k / (k - 1) * (1 - sum(diag(v)) / sum(v)) }
aR <- alpha(X[, c("Q5", "Q7", "Q8", "Q10")]); aS <- alpha(X[, c("Q2", "Q4", "Q6", "Q9")])
fc <- standardizedSolution(f8); fc <- fc$est.std[fc$op == "~~" & fc$lhs == "rea" & fc$rhs == "sup"]
cat(sprintf("Table 4: alpha reappraisal pub 0.840 obs %.3f ; suppression pub 0.745 obs %.3f ; factor r pub 0.084 obs %.3f\n",
            aR, aS, fc))
t2 <- worst <= 0.005 && abs(aR - .840) < .0015 && abs(aS - .745) < .0015

cat("\nNote: pins every item's subscale and ties each live code to the paper's own Q-number;\n",
    "does NOT establish which canonical wording each Q-number carries within a subscale\n",
    "(the paper prints no wording) -- the tie to canonical item k is the instrument's numbering.\n", sep = "")
cat(sprintf("test1=%s test2=%s\n", t1, t2))
cat(if (t1 && t2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

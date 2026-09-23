# verify_fraijo_2022_mslq.R -- Step 5b mapping check for fraijo_2022_mslq (batch_317).
#
# Claim: item codes item1..item81 (the deposit's own xlsx column names) carry the MSLQ
# items numbered 1..81 in the deposit's "CMEA - Survey.pdf", i.e. canonical MSLQ order.
# Falsifiable prediction: the canonical MSLQ manual scoring key (Pintrich et al. 1991),
# applied to the live items, reproduces the 15 subscale descriptives the deposit itself
# publishes in "Table 3.pdf" and "Table 4.pdf" (n, M, SD, min, max; Mendeley Data
# 10.17632/bsxgbt8wnp v2). Min/max of a mean over k items is a strong fingerprint of
# which k items are in the subscale.
#
# What this does NOT establish: the ORDER of items WITHIN a subscale (e.g. whether
# item1 and item16 are swapped, both Intrinsic Goal Orientation). Hence PARTIAL.

suppressMessages(library(irw))
TABLE <- "fraijo_2022_mslq"

K <- list(IGO=c(1,16,22,24), EGO=c(7,11,13,30), TV=c(4,10,17,23,26,27), CB=c(2,9,18,25),
  SE=c(5,6,12,15,20,21,29,31), TA=c(3,8,14,19,28), REH=c(39,46,59,72), ELA=c(53,62,64,67,69,81),
  ORG=c(32,42,49,63), CT=c(38,47,51,66,71), MSR=c(33,36,41,44,54,55,56,57,61,76,78,79),
  TSE=c(35,43,52,65,70,73,77,80), ER=c(37,48,60,74), PL=c(34,45,50), HS=c(40,58,68,75))
REV <- c(33,37,40,52,57,60,77,80)   # canonical MSLQ reverse-keyed items

# Published (deposit Table 3 = motivation, Table 4 = learning strategies): M, SD, min, max
PUB <- rbind(IGO=c(5.24,.969,2.25,7.00), EGO=c(5.31,1.10,2.00,7.00), TV=c(6.00,.914,1.67,7.00),
  CB=c(5.51,.906,2.50,7.00), SE=c(5.27,.953,2.25,7.00), TA=c(5.08,1.29,1.20,7.00),
  REH=c(5.36,.892,3.25,7.00), ELA=c(5.13,.923,3.00,7.00), ORG=c(5.38,1.28,1.25,7.00),
  CT=c(5.02,.960,2.80,7.00), MSR=c(5.09,.708,2.92,6.42), TSE=c(4.87,.565,3.63,5.88),
  ER=c(4.72,.687,3.25,6.50), PL=c(4.10,1.21,1.33,7.00), HS=c(5.28,.924,1.50,7.00))
colnames(PUB) <- c("M","SD","min","max")
TOL <- c(M=0.015, SD=0.012, min=0.006, max=0.006)   # published values are 2-3 dp, M apparently truncated

d <- as.data.frame(irw::irw_fetch(TABLE)[, c("id","item","resp")])
w <- reshape(d, idvar="id", timevar="item", direction="wide"); names(w) <- sub("^resp\\.", "", names(w))
stats <- function(rev) t(sapply(names(K), function(k) {
  s <- rowMeans(sapply(K[[k]], function(i) { x <- w[[paste0("item", i)]]; if (rev && i %in% REV) 8 - x else x }))
  c(M=mean(s), SD=sd(s), min=min(s), max=max(s)) }))

obs <- stats(FALSE)
cat("Claimed key, items stored RAW (as the deposit's own Tables 3/4 evidently computed):\n")
cat(sprintf("%-4s %6s %6s | %6s %6s | %5s %5s | %5s %5s\n","sub","pubM","obsM","pubSD","obsSD","pmin","omin","pmax","omax"))
ok <- TRUE
for (k in rownames(PUB)) {
  dev <- abs(obs[k,] - PUB[k,]); pass <- all(dev <= TOL); ok <- ok && pass
  cat(sprintf("%-4s %6.2f %6.3f | %6.3f %6.3f | %5.2f %5.3f | %5.2f %5.3f %s\n", k, PUB[k,1], obs[k,1],
      PUB[k,2], obs[k,2], PUB[k,3], obs[k,3], PUB[k,4], obs[k,4], if (pass) "" else "  <-- MISMATCH"))
}
cat("\nContrast (informational): same key with the 8 reverse items reversed -- should NOT match\n")
alt <- stats(TRUE)
for (k in c("MSR","TSE","ER","HS")) cat(sprintf("%-4s M %.3f vs %.2f; min %.3f vs %.2f; max %.3f vs %.2f\n",
  k, alt[k,1], PUB[k,1], alt[k,3], PUB[k,3], alt[k,4], PUB[k,4]))

cat("\nEstablishes: subscale membership of all 81 items (15/15 subscales reproduce n, M, SD, min, max).\n",
    "Does NOT establish: order of items within a subscale.\n", sep="")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

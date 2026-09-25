# verify_test_taking_much_2025_ef.R -- Step 5b mapping check (batch_415).
# mapping_basis = paper_explicit: codebook tte_codebook.pdf (osf.io/sph7j) names EF0k_0t
# "Response to the k-th item at t-th measurement point"; efcm_ItemOverview.pdf (osf.io/hnr93)
# numbers the items E1..E5. This script tests that tie against the data.
#
# Route A (item identity, E1-E3): the study rephrased E1-E3 into Current Motivation items
#   CM01-CM03 (same order in the same overview). Each EF0k_0t (after block t) should correlate
#   most with its same-wording CM0k_0(t+1) (before block t+1) -- row AND column maximum.
# Route B (option direction, E5): E5 "I could have tried harder..." is reverse-worded. Stored raw,
#   it would correlate NEGATIVELY with E1-E3. The shipped option_text for EF05 is REVERSED
#   (1 = strongly agree) because the data show it positive; this checks that claim, and compares
#   alpha as-stored vs re-reversed against the paper's omega (.65 / .74, JOPD Table 6).
# NOT established: E4 vs E5 are distinguished only by the codebook order and by the authors'
#   own EF_0t score (mean with 5-EF05, reproduced 1244/1244 from the OSF tte_data.csv), not by a
#   statistic -- hence PARTIAL, not VERIFIED.
suppressMessages(library(irw))
ef <- irw::irw_fetch("test_taking_much_2025_ef")
cm <- irw::irw_fetch("test_taking_much_2025_cm")
wide <- function(d) { w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar="id",
  timevar="item", direction="wide"); names(w) <- sub("^resp\\.", "", names(w)); w }
E <- wide(ef); C <- wide(cm); m <- merge(E, C, by="id")
cat("merged n =", nrow(m), "\n")
ok <- TRUE
for (t in 1:2) {
  M <- sapply(1:3, function(j) sapply(1:3, function(k)
    cor(m[[sprintf("EF%02d_%02d",k,t)]], m[[sprintf("CM%02d_%02d",j,t+1)]], use="pair")))
  dimnames(M) <- list(sprintf("EF%02d_%02d",1:3,t), sprintf("CM%02d_%02d",1:3,t+1))
  print(round(M,3))
  rowok <- all(apply(M,1,which.max) == 1:3); colok <- all(apply(M,2,which.max) == 1:3)
  cat(sprintf("wave %d: diagonal is row max %s, column max %s\n", t, rowok, colok))
  ok <- ok && rowok && colok
}
alpha <- function(X){k<-ncol(X);k/(k-1)*(1-sum(apply(X,2,var))/var(rowSums(X)))}
pub <- c(.65,.74)
for (t in 1:2) {
  cols <- sprintf("EF%02d_%02d",1:5,t); X <- m[, cols]
  r5 <- sapply(1:4, function(k) cor(X[[5]], X[[k]]))
  cat(sprintf("wave %d: r(EF05, EF01..EF04) = %s\n", t, paste(round(r5,3), collapse=" ")))
  Xr <- X; Xr[[5]] <- 5 - Xr[[5]]
  cat(sprintf("wave %d: alpha as stored %.3f | EF05 re-reversed %.3f | published omega %.2f\n",
      t, alpha(X), alpha(Xr), pub[t]))
  ok <- ok && all(r5[1:3] > 0) && abs(alpha(X)-pub[t]) < abs(alpha(Xr)-pub[t])
}
cat("Not established: E4 vs E5 identity beyond codebook order (see header).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

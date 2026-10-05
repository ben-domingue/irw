# verify_rvobgvmaas_lsf_lehing_2024.R -- Step 5b mapping check (batch_530).
#
# Claim: item code maas_<N>[r]_t<k> carries MAAS item N (Condon 1993; German MABS,
# PLOS ONE S1 File numbered list 1..19), and resp 5 = the high-attachment option for
# every item (Condon's scoring: "Scoring is 1-5, with 5 high attachment"; the r items
# are stored already reversed).
#
# Route 1 (per-item descriptives): Lehnig et al. 2024 PLOS ONE Table 2 (t002, image)
# prints, per numbered item and with a content descriptor, M / SD / skewness /
# kurtosis at T1. The live wave-0 rows are T1. Each live item's 4-vector must be
# nearest to its OWN published row, and within rounding.
# Route 6 (polarity): if option direction were wrong for the r items they would
# correlate negatively with the rest; print the corrected item-total r per item.
#
# Does NOT establish: t2 codes are not in Table 2 (T1 only); they are tied by the
# shared item number in the source column name. Printed as support: each t2 item's
# highest cross-wave correlation with the T1 items.

suppressMessages(library(irw))
TABLE <- "rvobgvmaas_lsf_lehing_2024"

# Table 2, "Original MAAS" block, T1: item -> M, SD, S, K
PUB <- rbind(
  `1`=c(3.60,0.80,-0.18,-0.39), `2`=c(3.95,0.83,-0.20,-0.87), `3`=c(4.60,0.63,-1.45,1.54),
  `4`=c(3.62,0.98,-0.18,-0.68), `5`=c(2.90,0.99,0.13,-0.74),  `6`=c(4.03,1.17,-0.82,-0.67),
  `7`=c(3.57,1.14,-0.63,-0.29), `8`=c(2.35,0.99,0.83,0.42),   `9`=c(4.68,0.52,-1.37,0.94),
  `10`=c(3.46,0.92,-0.53,0.64), `11`=c(4.45,0.67,-0.92,0.18), `12`=c(4.88,0.40,-4.05,19.51),
  `13`=c(4.44,0.65,-1.34,3.84), `14`=c(3.63,0.87,-0.86,1.21), `15`=c(4.81,0.42,-2.03,3.27),
  `16`=c(4.80,0.51,-2.60,5.80), `17`=c(2.05,0.98,0.95,0.44),  `18`=c(4.72,0.56,-1.91,2.65),
  `19`=c(4.93,0.39,-7.26,61.66))
REV <- c(1,3,5,6,7,9,10,12,15,16,18)
code1 <- function(n) sprintf("maas_%d%s_t1", n, ifelse(n %in% REV, "r", ""))

sk <- function(x){n<-length(x);m<-mean(x);s<-sd(x); n/((n-1)*(n-2))*sum(((x-m)/s)^3)}
ku <- function(x){n<-length(x);m<-mean(x);s<-sd(x)
  n*(n+1)/((n-1)*(n-2)*(n-3))*sum(((x-m)/s)^4) - 3*(n-1)^2/((n-2)*(n-3))}

d <- as.data.frame(irw::irw_fetch(TABLE))
d0 <- d[d$wave == 0 & !is.na(d$resp), ]
OBS <- t(sapply(1:19, function(n){x <- d0$resp[d0$item == code1(n)]
  c(mean(x), sd(x), sk(x), ku(x), length(x))}))
rownames(OBS) <- 1:19

scale_ <- c(1,1,1,10)  # kurtosis spans 0..62; down-weight so it cannot dominate
ok <- TRUE
cat(sprintf("%-12s %4s | %5s %5s %6s %6s | %5s %5s %6s %6s | nearest\n","code","n",
            "M_pub","SD","S","K","M_obs","SD","S","K"))
for (n in 1:19) {
  dist <- apply(PUB, 1, function(p) sqrt(sum(((OBS[n,1:4]-p)/scale_)^2)))
  near <- as.integer(names(which.min(dist)))
  within <- all(abs(OBS[n,1:4]-PUB[n,]) <= c(0.006,0.006,0.006,0.006))
  if (near != n || !within) ok <- FALSE
  cat(sprintf("%-12s %4d | %5.2f %5.2f %6.2f %6.2f | %5.2f %5.2f %6.2f %6.2f | %d %s\n",
      code1(n), OBS[n,5], PUB[n,1],PUB[n,2],PUB[n,3],PUB[n,4],
      OBS[n,1],OBS[n,2],OBS[n,3],OBS[n,4], near, if (within) "" else "OUT OF ROUNDING"))
}

# polarity: corrected item-total r at wave 0 (wide by id)
w <- reshape(d0[, c("id","item","resp")], idvar="id", timevar="item", direction="wide")
names(w) <- sub("^resp\\.", "", names(w))
M <- as.matrix(w[, code1(1:19)])
itc <- sapply(1:19, function(j) cor(M[,j], rowSums(M[,-j]), use="complete.obs"))
cat("\ncorrected item-total r (wave 0):", paste(sprintf("%d:%.2f",1:19,itc), collapse=" "), "\n")
if (any(itc < 0)) ok <- FALSE

# support only: t2 items vs T1 items, cross-wave
d1 <- d[d$wave == 1 & grepl("_t2$", d$item), c("id","item","resp")]
w1 <- reshape(d1, idvar="id", timevar="item", direction="wide"); names(w1) <- sub("^resp\\.","",names(w1))
m <- merge(w, w1, by="id")
cat("\nsupport (not gating): t2 item -> T1 item with highest cross-wave r\n")
for (c2 in grep("_t2$", names(w1), value=TRUE)) {
  r <- sapply(code1(1:19), function(c1) suppressWarnings(cor(m[[c1]], m[[c2]], use="complete.obs")))
  cat(sprintf("  %-11s -> %-12s r=%.2f\n", c2, names(which.max(r)), max(r, na.rm=TRUE)))
}
cat("\nNot established: the t2 codes are tied by item number in the source column name only.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

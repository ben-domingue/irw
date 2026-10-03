# verify_yoshimura_2026_isu_scale.R -- Step 5b check for batch_533.
#
# Claim: isu1m9..isu1m14 are items 9..14 of Komaki's (1994) 14-item workplace
# social support scale (emotional = items 1-8, instrumental = 9-14; the sibling
# table's codes are es1m1..es1m8), and the shipped item_text for isu1m<k> is
# Komaki's Appendix item k.
#
# Route A (study-internal, pins code -> study item-number pairs):
#   The study's S1 File (pone.0346791.s004) path diagram names the IS parcels
#   isupA910, isupB1112, isupC1314, i.e. items {9,10}, {11,12}, {13,14}.
#   S1 Table (pone.0346791.s001) Table B publishes IS1 3.23 (1.05),
#   IS2 3.17 (1.05), IS3 2.99 (1.04), r(IS1,IS2)=.77, r(IS1,IS3)=.60,
#   r(IS2,IS3)=.71. We test the claimed pairing AND all 90 alternative
#   (pair-partition x parcel-label) assignments of the six codes to count how
#   many also reproduce the published values.
# Route B (content, ties code numbers to Komaki's TEXT):
#   Komaki 9-11 are information/advice (知識や情報 / やり方やコツ / アドバイス);
#   12-14 are hands-on help with the work (手伝って / 仕事をしてくれる /
#   手伝って). Prediction: {12,13,14} and {9,10,11} are the two highest
#   mean-intercorrelation triplets of all 20.
# Neither route orders items within the pairs {9,10}, {11,12}, {13,14}.

suppressMessages(library(irw))
TABLE <- "yoshimura_2026_isu_scale"
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, paste0("isu1m", 9:14)]
cat("N respondents:", nrow(w), " complete:", sum(complete.cases(w)), "\n\n")

ok <- TRUE
pub_m <- c(3.23, 3.17, 2.99)
pub_sd <- c(1.05, 1.05, 1.04); pub_r <- c(.77, .60, .71)
tol <- 0.006
fit <- function(parcels) {
  P <- sapply(parcels, function(ix) rowMeans(w[, paste0("isu1m", ix), drop = FALSE]))
  m <- colMeans(P); s <- apply(P, 2, sd)
  r <- c(cor(P[,1], P[,2]), cor(P[,1], P[,3]), cor(P[,2], P[,3]))
  list(m = m, s = s, r = r,
       pass = all(abs(m - pub_m) <= tol) && all(abs(s - pub_sd) <= tol) && all(abs(r - pub_r) <= tol))
}
claimed <- list(IS1 = c(9, 10), IS2 = c(11, 12), IS3 = c(13, 14))
f <- fit(claimed)
cat("Route A: claimed parcels vs S1 Table B\n")
for (j in 1:3)
  cat(sprintf("  %s items {%s}: M %.3f (pub %.2f)  SD %.3f (pub %.2f)\n", names(claimed)[j],
              paste(claimed[[j]], collapse = ","), f$m[j], pub_m[j], f$s[j], pub_sd[j]))
cat(sprintf("  r(IS1,IS2) %.3f (pub .77)  r(IS1,IS3) %.3f (pub .60)  r(IS2,IS3) %.3f (pub .71)\n",
            f$r[1], f$r[2], f$r[3]))
if (!f$pass) ok <- FALSE

# every assignment of the six codes to three labelled pairs (15 partitions x 6 labelings)
codes <- 9:14; n_pass <- 0; n_all <- 0
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
seen <- character(0)
for (p in perms(codes)) {
  pr <- list(sort(p[1:2]), sort(p[3:4]), sort(p[5:6]))
  key <- paste(sapply(pr, paste, collapse = "-"), collapse = "|")
  if (key %in% seen) next
  seen <- c(seen, key); n_all <- n_all + 1
  if (fit(pr)$pass) { n_pass <- n_pass + 1; cat("  reproducing assignment:", key, "\n") }
}
cat(sprintf("  %d of %d labelled pair-assignments reproduce Table B within %.3f\n", n_pass, n_all, tol))
if (n_pass != 1) ok <- FALSE

cat("\nRoute B: triplets by mean inter-item r (all 20)\n")
R <- cor(w, use = "pairwise.complete.obs")
tr <- combn(6, 3)
mr <- apply(tr, 2, function(ix) mean(R[ix, ix][upper.tri(R[ix, ix])]))
o <- order(mr, decreasing = TRUE)
for (k in o[1:5]) cat(sprintf("  {%s}  %.3f\n", paste(codes[tr[, k]], collapse = ","), mr[k]))
top2 <- sort(c(paste(codes[tr[, o[1]]], collapse = ","), paste(codes[tr[, o[2]]], collapse = ",")))
cat(sprintf("  within {9,10,11} %.3f | within {12,13,14} %.3f | across %.3f\n",
            mean(R[1:3,1:3][upper.tri(R[1:3,1:3])]), mean(R[4:6,4:6][upper.tri(R[4:6,4:6])]), mean(R[1:3,4:6])))
if (!identical(top2, sort(c("9,10,11", "12,13,14")))) ok <- FALSE

cat("\nNot established: order within the pairs {9,10}, {11,12}, {13,14}\n",
    "(e.g. a swap of isu1m9 and isu1m10 would pass both routes).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

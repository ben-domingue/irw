# verify_yoshimura_2026_es_scale.R -- Step 5b check for batch_532.
#
# Claim: es1m1..es1m8 are items 1..8 of Komaki's (1994) 14-item workplace social
# support scale (emotional support = items 1-8, instrumental = 9-14; the study's
# sibling columns are isu1m9..isu1m14, continuing that numbering), and the shipped
# item_text for es1m<k> is Komaki's Appendix item k.
#
# Route A (study-internal, pins code -> study item number partition):
#   The study's S1 File (pone.0346791.s004) path diagram names the ES parcels
#   esupA125, esupB367, esupC48, i.e. items {1,2,5}, {3,6,7}, {4,8}. S1 Table
#   (pone.0346791.s001) Table B publishes ES1 2.99 (0.99), ES2 3.22 (0.97),
#   ES3 3.07 (0.98), r(ES1,ES2)=.77, r(ES1,ES3)=.78, r(ES2,ES3)=.83.
#   A mis-numbered code set moves items between parcels and breaks these.
# Route B (content, ties code numbers to Komaki's TEXT):
#   Komaki items 6, 7, 8 are the three evaluation/recognition items
#   (正しく評価 / 高く評価 / 実力を評価し、認めて). Prediction: {es1m6, es1m7, es1m8}
#   is the highest mean-intercorrelation triplet of all 56.
# Neither route orders items within {1..5} or within {6,7,8}; see evidence.

suppressMessages(library(irw))
TABLE <- "yoshimura_2026_es_scale"
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, paste0("es1m", 1:8)]
cat("N respondents:", nrow(w), "\n\n")

ok <- TRUE
parcels <- list(ES1 = c(1, 2, 5), ES2 = c(3, 6, 7), ES3 = c(4, 8))
pub_m <- c(2.99, 3.22, 3.07); pub_sd <- c(0.99, 0.97, 0.98)
P <- sapply(parcels, function(ix) rowMeans(w[, paste0("es1m", ix), drop = FALSE]))
cat("Route A: parcel means/SDs vs S1 Table B\n")
for (j in 1:3) {
  m <- mean(P[, j]); s <- sd(P[, j])
  cat(sprintf("  %s items {%s}: M %.2f (pub %.2f)  SD %.2f (pub %.2f)\n", names(parcels)[j],
              paste(parcels[[j]], collapse = ","), m, pub_m[j], s, pub_sd[j]))
  if (abs(m - pub_m[j]) > 0.006 || abs(s - pub_sd[j]) > 0.006) ok <- FALSE
}
pub_r <- c(.77, .78, .83); obs_r <- c(cor(P[,1], P[,2]), cor(P[,1], P[,3]), cor(P[,2], P[,3]))
cat(sprintf("  r(ES1,ES2) %.3f (pub .77)  r(ES1,ES3) %.3f (pub .78)  r(ES2,ES3) %.3f (pub .83)\n",
            obs_r[1], obs_r[2], obs_r[3]))
if (any(abs(obs_r - pub_r) > 0.006)) ok <- FALSE

cat("\nRoute B: evaluation triplet {6,7,8} vs all 56 triplets (mean inter-item r)\n")
R <- cor(w)
tr <- combn(8, 3)
mr <- apply(tr, 2, function(ix) mean(R[ix, ix][upper.tri(R[ix, ix])]))
o <- order(mr, decreasing = TRUE)
for (k in o[1:5]) cat(sprintf("  {%s}  %.3f\n", paste(tr[, k], collapse = ","), mr[k]))
top <- paste(tr[, o[1]], collapse = ",")
cat(sprintf("  top triplet: {%s}; gap to next: %.3f\n", top, mr[o[1]] - mr[o[2]]))
within678 <- mr[o[1]]
cross <- mean(R[1:5, 6:8]); within15 <- mean(R[1:5, 1:5][upper.tri(R[1:5, 1:5])])
cat(sprintf("  mean r within {6,7,8} %.3f | within {1..5} %.3f | across %.3f\n", within678, within15, cross))
if (top != "6,7,8") ok <- FALSE

cat("\nNot established: order within {1..5} and within {6,7,8} (route B is a content\n",
    "cluster; route A pins parcel membership in the study's own numbering, not text).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

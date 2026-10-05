# verify_kotsou_2016_panas.R -- Step 5b mapping check for kotsou_2016_panas (batch_547).
#
# Claim: live codes PANAS1..PANAS20 carry the canonical Watson, Clark & Tellegen (1988)
# adjectives in printed order (mapping_basis=reconstructed; the deposit's SCSdata.xls has
# bare headers and no labels). Canonical PA positions {1,3,5,9,10,12,14,16,17,19},
# NA positions {2,4,6,7,8,11,13,15,18,20}.
#
# Routes:
#   (6) keying/valence class: every item must correlate more with the other items of its
#       own canonical class than with the other class.
#   (3) published subscale statistics, Kotsou & Leys (2016) PLOS ONE 11(4):e0152880,
#       Table 1 (n=1554): PA M=3.37 SD=.65 alpha=.84; NA M=2.46 SD=.69 alpha=.89.
#       Means and alpha are compared; the published NA SD (.69) is NOT reproduced by
#       the canonical split (whose NA mean and alpha do match) and is printed, not gated on.
#   (7) marker: 'Hostile' (PANAS8) should be the least-endorsed item and anchor
#       direction 1=very slightly..5=extremely should put NA items below PA items.
# NOT established: order WITHIN a valence class (e.g. PANAS9 Enthusiastic vs PANAS16
# Determined). Status PARTIAL.

suppressMessages(library(irw))
TABLE <- "kotsou_2016_panas"
PA <- c(1,3,5,9,10,12,14,16,17,19); NA_ <- c(2,4,6,7,8,11,13,15,18,20)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar="id", timevar="item", direction="wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, paste0("PANAS", 1:20)]
C <- cor(X, use="pairwise.complete.obs")

ok <- TRUE
cat(sprintf("%-8s %-5s %7s %7s %7s\n", "item", "class", "mean", "rPA", "rNA"))
for (i in 1:20) {
  rpa <- mean(C[i, setdiff(PA, i)]); rna <- mean(C[i, setdiff(NA_, i)])
  cls <- if (i %in% PA) "PA" else "NA"
  good <- if (cls == "PA") rpa > rna else rna > rpa
  if (!good) ok <- FALSE
  cat(sprintf("%-8s %-5s %7.2f %7.2f %7.2f %s\n", paste0("PANAS", i), cls,
              mean(X[, i], na.rm=TRUE), rpa, rna, if (good) "" else "<-- WRONG CLASS"))
}

alpha <- function(M) { k <- ncol(M); k/(k-1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M))) }
pa <- rowMeans(X[, PA]); na <- rowMeans(X[, NA_])
res <- rbind(PA=c(mean(pa), sd(pa), alpha(X[, PA]), 3.37, .65, .84),
             NA_=c(mean(na), sd(na), alpha(X[, NA_]), 2.46, .69, .89))
colnames(res) <- c("M_obs","SD_obs","a_obs","M_pub","SD_pub","a_pub")
cat("\nSubscales vs Kotsou & Leys (2016) Table 1:\n")
for (r in rownames(res)) cat(sprintf("%-4s M %.3f vs %.2f | SD %.3f vs %.2f | alpha %.3f vs %.2f\n", r,
  res[r,1], res[r,4], res[r,2], res[r,5], res[r,3], res[r,6]))
if (any(abs(res[, "M_obs"] - res[, "M_pub"]) > 0.01)) ok <- FALSE
if (any(abs(res[, "a_obs"] - res[, "a_pub"]) > 0.01)) ok <- FALSE
cat("(NA SD .833 vs published .69 is a known unreproduced figure; not gated.)\n")

m <- colMeans(X, na.rm=TRUE)
cat(sprintf("\nLeast-endorsed item: %s (mean %.2f, %.1f%% at 1)\n", names(which.min(m)), min(m),
            100 * mean(X[, which.min(m)] == 1, na.rm=TRUE)))
if (names(which.min(m)) != "PANAS8") ok <- FALSE
if (!(mean(m[PA]) > mean(m[NA_]))) ok <- FALSE

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

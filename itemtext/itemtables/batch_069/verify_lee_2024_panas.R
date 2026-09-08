# verify_lee_2024_panas.R -- Step 5b mapping verification, re-runnable.
#
# CLAIM UNDER TEST -----------------------------------------------------------
# lee_2024_panas ships item codes PANAS1..PANAS20 (the bare column headers of
# the PeerJ deposit peerj-12-18379-s002.xlsx; the deposit carries no item text
# at all). The item_text shipped is the K-PANAS item order of Park & Lee (2016),
# the very translation Lee et al. (2024) say they used:
#
#   1 interested   2 irritable   3 distressed  4 alert     5 excited
#   6 ashamed      7 upset       8 inspired    9 strong   10 nervous
#  11 guilty      12 determined 13 scared     14 attentive 15 hostile
#  16 jittery     17 enthusiastic 18 active   19 proud    20 afraid
#
# That order is NOT the canonical Watson/Clark/Tellegen (1988) order, which is
# what a default extraction would have assumed. The two routes below are what
# separate them, and what pin the numbering item by item.
#
# ROUTE A (SKILL.md route 5) -- PA/NA block structure. Under the K-PANAS order
#   PA = {1,4,5,8,9,12,14,17,18,19}; under canonical PANAS PA = {1,3,5,9,10,12,
#   14,16,17,19}. Only one of those partitions the live correlation matrix.
#
# ROUTE B (SKILL.md route 1, applied to a full published correlation matrix
#   rather than to means) -- Park H, Lee J-M, Koo S, Chung S-Y, Lee S, Cho YI
#   (2022) "A PANAS Structure Analysis: On the Validity of a Bifactor Model in
#   Korean College Students", Sustainability 14:16456, Table 1, publishes the
#   complete 20x20 K-PANAS correlation matrix for an independent Korean college
#   sample (N=875), with its rows labelled by adjective in that paper's Table 3
#   ("C1 (interested)", "C2 (irritable)", ...). Matching each live item's
#   correlation profile against each published item's profile is a per-item,
#   falsifiable prediction: a permuted mapping breaks it.
#
# WHAT THIS DOES NOT ESTABLISH: PANAS13 (scared) and PANAS20 (afraid) are near
# synonyms (published r = .71, live r = .72) and route B cannot separate them --
# swapping just those two labels leaves the fit essentially unchanged. Every
# other item is separated. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "lee_2024_panas"

# --- published lower triangle, Park et al. (2022) Sustainability 14:16456, Table 1
pub_rows <- list(
 c(),
 c(-0.21),
 c(-0.24,0.59),
 c(0.34,-0.23,-0.29),
 c(0.53,-0.17,-0.27,0.42),
 c(-0.02,0.16,0.24,-0.13,-0.04),
 c(-0.02,0.57,0.52,-0.18,-0.15,0.31),
 c(0.32,-0.09,0.02,0.20,0.20,0.14,0.03),
 c(0.30,-0.06,-0.04,0.24,0.22,-0.04,0.03,0.45),
 c(-0.03,0.27,0.28,-0.09,-0.04,0.31,0.32,0.18,0.19),
 c(-0.08,0.21,0.29,-0.12,-0.12,0.45,0.31,0.10,0.02,0.23),
 c(0.36,-0.07,-0.09,0.24,0.27,0.04,-0.03,0.34,0.39,0.11,0.09),
 c(-0.13,0.29,0.42,-0.18,-0.17,0.38,0.38,0.07,-0.02,0.44,0.45,0.02),
 c(0.23,-0.004,-0.02,0.20,0.15,0.12,0.04,0.33,0.40,0.32,0.04,0.40,0.13),
 c(-0.09,0.36,0.42,-0.10,-0.12,0.28,0.51,0.06,0.08,0.26,0.40,0.07,0.38,0.08),
 c(-0.16,0.34,0.45,-0.21,-0.19,0.32,0.35,0.03,-0.03,0.47,0.34,-0.04,0.52,0.07,0.41),
 c(0.46,-0.09,0.10,0.26,0.35,-0.02,-0.06,0.37,0.44,0.19,-0.05,0.43,-0.05,0.41,0.03,-0.02),
 c(0.54,-0.21,-0.29,0.37,0.58,-0.06,-0.17,0.24,0.34,-0.01,-0.14,0.31,-0.15,0.23,-0.16,-0.17,0.57),
 c(0.47,-0.20,-0.25,0.36,0.45,-0.01,-0.15,0.33,0.46,0.09,-0.09,0.45,-0.11,0.37,-0.04,-0.15,0.57,0.61),
 c(-0.16,0.37,0.49,-0.20,-0.18,0.37,0.45,0.05,-0.02,0.45,0.41,-0.01,0.71,0.10,0.45,0.65,-0.05,-0.19,-0.12)
)
P <- diag(20)
for (i in 2:20) { P[i, 1:(i-1)] <- pub_rows[[i]]; P[1:(i-1), i] <- pub_rows[[i]] }

ADJ <- c("interested","irritable","distressed","alert","excited","ashamed","upset",
         "inspired","strong","nervous","guilty","determined","scared","attentive",
         "hostile","jittery","enthusiastic","active","proud","afraid")

d <- irw::irw_fetch(TABLE)
nm <- paste0("PANAS", 1:20)
w  <- reshape(as.data.frame(d[, c("id","item","resp")]),
              idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, nm]
C <- cor(w, use = "pairwise")

ok <- TRUE

## ---- ROUTE A: which PA/NA partition does the data support? -----------------
gap <- function(pa) {
  na <- setdiff(1:20, pa)
  within <- mean(c(C[pa, pa][upper.tri(diag(length(pa)))],
                   C[na, na][upper.tri(diag(length(na)))]))
  between <- mean(C[pa, na])
  c(within = within, between = between, gap = within - between)
}
pa_k   <- c(1,4,5,8,9,12,14,17,18,19)   # K-PANAS (Park & Lee) -- what we shipped
pa_std <- c(1,3,5,9,10,12,14,16,17,19)  # canonical Watson et al. (1988) order
gk <- gap(pa_k); gs <- gap(pa_std)
cat("=== ROUTE A: PA/NA block structure in the live correlation matrix ===\n")
cat(sprintf("K-PANAS order  (shipped):  within=%.3f  between=%+.3f  gap=%.3f\n", gk[1], gk[2], gk[3]))
cat(sprintf("canonical PANAS order   :  within=%.3f  between=%+.3f  gap=%.3f\n", gs[1], gs[2], gs[3]))
cat("\nper item, mean r with its own K-PANAS valence block vs the other block:\n")
nA <- 0
for (i in 1:20) {
  own <- if (i %in% pa_k) pa_k else setdiff(1:20, pa_k)
  ro <- mean(C[i, setdiff(own, i)]); rx <- mean(C[i, setdiff(1:20, own)])
  hit <- ro > rx; nA <- nA + hit
  cat(sprintf("  %-8s %-11s own=%+.3f other=%+.3f  %s\n", nm[i], ADJ[i],
              ro, rx, ifelse(hit, "OK", "MISMATCH")))
}
cat(sprintf("route A: %d/20 items sit with their own valence block\n", nA))
if (nA < 20 || gk[3] < 3 * gs[3]) ok <- FALSE

## ---- ROUTE B: profile match against the published 20x20 matrix -------------
S <- matrix(NA_real_, 20, 20)
for (i in 1:20) for (j in 1:20) {
  k <- setdiff(1:20, unique(c(i, j)))
  S[i, j] <- cor(P[i, k], C[j, k])
}
cat("\n=== ROUTE B: live vs published (Park et al. 2022, N=875) profile match ===\n")
cat(sprintf("elementwise r of the two 190-entry lower triangles: %.3f\n",
            cor(P[lower.tri(P)], C[lower.tri(C)])))
cat("\npublished item -> best-matching live item (profile correlation):\n")
nB <- 0
for (i in 1:20) {
  b <- order(S[i, ], decreasing = TRUE)[1:2]
  hit <- b[1] == i; nB <- nB + hit
  cat(sprintf("  C%-2d %-11s best=%-8s %.3f | 2nd=%-8s %.3f | identity %.3f  %s\n",
              i, ADJ[i], nm[b[1]], S[i, b[1]], nm[b[2]], S[i, b[2]], S[i, i],
              ifelse(hit, "OK", "near-tie")))
}
cat(sprintf("route B: identity is the argmax for %d/20 published items\n", nB))

# Globally optimal 1-1 assignment: is it the identity?
assign_opt <- as.integer(clue::solve_LSAP(S - min(S), maximum = TRUE))
cat(sprintf("optimal one-to-one assignment (Hungarian): %d/20 fixed points\n",
            sum(assign_opt == 1:20)))
cat("assignment:", paste(assign_opt, collapse = " "), "\n")
set.seed(1)
perm <- replicate(20000, sum(S[cbind(1:20, sample(20))]))
cat(sprintf("sum of matched profile r: identity %.2f vs random permutations %.2f (SD %.2f), p = %.5f\n",
            sum(diag(S)), mean(perm), sd(perm), mean(perm >= sum(diag(S)))))

# The one pair this route cannot separate.
frob <- function(pi) sum((P - C[pi, pi])^2)
pi_swap <- 1:20; pi_swap[c(13, 20)] <- c(20, 13)
cat(sprintf("\nFrobenius ||P - C||^2: identity %.3f ; 13<->20 (scared/afraid) swapped %.3f\n",
            frob(1:20), frob(pi_swap)))
cat(sprintf("published r(C13,C20) = %.2f ; live r(PANAS13,PANAS20) = %.2f -- near synonyms, NOT separated here\n",
            P[13, 20], C[13, 20]))

if (!(sum(assign_opt == 1:20) == 20)) ok <- FALSE
if (cor(P[lower.tri(P)], C[lower.tri(C)]) < 0.9) ok <- FALSE

cat("\nNote: routes A and B jointly pin all 20 code->adjective assignments except the\n",
    "scared/afraid pair (PANAS13/PANAS20), which the data cannot distinguish. The\n",
    "shipped order for those two follows Park et al. (2022) Table 3. Hence PARTIAL.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_silvia_2024_funny.R -- Step 5b mapping check for silvia_2024_funny.
#
# Claim: hef1..hef4 = HEISS efficacy items [eff1]..[eff4] and hid1..hid4 = identity
# items [id1]..[id4], in the order of the paper's Table 1 (Silvia, Rodriguez &
# Karwowski, PsyArXiv 10.31234/osf.io/p3mza), which is the order the authors' own
# OSF script "S1 HEISS, Analyses and Figures, OSF.R" uses when it labels hef1..hid4.
#
# Falsifiable prediction: the paper's Table 2 (Study 1, n = 1842, 1-5 scale) prints
# per-item M, SD and graded-response-model discrimination a. The IRW table stores
# 0-4 (the authors' script adds 1 before describing), so live mean + 1 must match M,
# live SD must match SD, and a GRM fitted per subscale must reproduce a. Means tie
# for eff2/eff3 (3.32/3.32) and nearly for id1/id3 (3.09/3.07); the discriminations
# (4.56 vs 3.81; 3.91 vs 2.79) are what separate those pairs.
suppressMessages({library(irw); library(mirt)})
TABLE <- "silvia_2024_funny"
codes <- c("hef1","hef2","hef3","hef4","hid1","hid2","hid3","hid4")
PUB_M  <- c(2.81, 3.32, 3.32, 3.38, 3.09, 3.26, 3.07, 3.63)
PUB_SD <- c(1.06, 0.97, 0.99, 1.04, 1.10, 1.01, 1.08, 0.95)
PUB_A  <- c(2.17, 4.56, 3.81, 3.18, 3.91, 3.06, 2.79, 2.52)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, codes]
obs_m  <- colMeans(w, na.rm = TRUE) + 1
obs_sd <- apply(w, 2, sd, na.rm = TRUE)
a_ef <- coef(mirt(w[, 1:4], 1, itemtype = "graded", verbose = FALSE), IRTpars = TRUE, simplify = TRUE)$items[, "a"]
a_id <- coef(mirt(w[, 5:8], 1, itemtype = "graded", verbose = FALSE), IRTpars = TRUE, simplify = TRUE)$items[, "a"]
obs_a <- c(a_ef, a_id)

cat(sprintf("%-6s %7s %7s %7s %7s %7s %7s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD", "pub_a", "obs_a"))
for (i in seq_along(codes))
  cat(sprintf("%-6s %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f\n", codes[i],
              PUB_M[i], obs_m[i], PUB_SD[i], obs_sd[i], PUB_A[i], obs_a[i]))

dm <- max(abs(obs_m - PUB_M)); dsd <- max(abs(obs_sd - PUB_SD)); da <- max(abs(obs_a - PUB_A))
cat(sprintf("\nmax |dM| = %.3f, max |dSD| = %.3f, max |da| = %.3f\n", dm, dsd, da))

# Tie-breakers: the discrimination ordering must hold for the pairs whose means tie.
tie_ok <- obs_a["hef2"] > obs_a["hef3"] + 0.3 && obs_a["hid1"] > obs_a["hid3"] + 0.3
cat(sprintf("tie-breaks: a(hef2)=%.2f > a(hef3)=%.2f ; a(hid1)=%.2f > a(hid3)=%.2f -> %s\n",
            obs_a["hef2"], obs_a["hef3"], obs_a["hid1"], obs_a["hid3"], tie_ok))

# Would any other within-subscale permutation fit as well? Count permutations whose
# means AND a both land within tolerance of the published vector.
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
fits <- 0
for (pe in perms(1:4)) for (pi in perms(1:4)) {
  idx <- c(pe, pi + 4)
  if (max(abs(obs_m[idx] - PUB_M)) <= 0.02 && max(abs(obs_a[idx] - PUB_A)) <= 0.25) fits <- fits + 1
}
cat(sprintf("within-subscale permutations consistent with Table 2: %d of 576 (1 = only the claimed mapping)\n", fits))
# Cross-subscale: can any efficacy item be matched to an identity row on means alone?
cross <- outer(obs_m[1:4], PUB_M[5:8], function(a, b) abs(a - b))
cross2 <- outer(obs_m[5:8], PUB_M[1:4], function(a, b) abs(a - b))
cmin <- min(cross, cross2)
cat(sprintf("closest cross-subscale mean match: %.3f (tolerance 0.02) -> no efficacy/identity swap fits\n", cmin))

ok <- dm <= 0.01 && dsd <= 0.01 && da <= 0.25 && tie_ok && fits == 1 && cmin > 0.02
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

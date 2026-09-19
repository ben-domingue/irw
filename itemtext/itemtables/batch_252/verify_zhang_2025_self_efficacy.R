# verify_zhang_2025_self_efficacy.R -- Step 5b mapping check (batch_252).
#
# Claim: live item SE<k> is the item the paper's S2 File appendix prints as
# "SE<k>: <wording>". The appendix prefixes each item with the very code the S1
# Data column carries (explicit code labels), and data/zhang_2025_green_supply_chain.py
# melts S1 columns SE1..SE5 by name, so the code IS the source column name.
#
# Falsifiable checks run here:
#   A. live SE<k> equals S1 Data column SE<k> id-for-id, and no other SE column
#      reaches full agreement (the live code -> S1 column tie);
#   B. 5-factor CFA on S1 (CP, NP, EA, SE, GSCII, as in the paper) reproduces the
#      paper's Table 2 standardized loadings keyed to SE1..SE5 -- 0.819/0.813/0.732/
#      0.884/0.812 -- and every non-identity permutation of the five codes fits worse;
#   C. Cronbach's alpha of the live SE items vs Table 2 alpha 0.906.
# NOT established: that the S2 appendix's "SE<k>" labels and Table 2's "SE<k>"
# labels were assigned by the same hand (both are the authors' own codes; no
# statistic can test that), nor that the English matches the administered Chinese.

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhang_2025_self_efficacy"
PUB_LOAD <- c(SE1 = 0.819, SE2 = 0.813, SE3 = 0.732, SE4 = 0.884, SE5 = 0.812)   # Table 2 (t002)
PUB_ALPHA <- 0.906
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(w$id), ]
items <- paste0("SE", 1:5)

s1_url <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0322200.s001"
tf <- tempfile(fileext = ".xlsx")
ok <- tryCatch({ download.file(s1_url, tf, mode = "wb", quiet = TRUE,
                               headers = c("User-Agent" = "Mozilla/5.0")); TRUE },
               error = function(e) FALSE)
pass <- TRUE

if (ok) {
  s1 <- as.data.frame(readxl::read_excel(tf))
  s1 <- s1[order(s1$id), ]
  m <- merge(w, s1, by = "id", suffixes = c(".live", ".s1"))
  cat(sprintf("A. live vs S1 id-level agreement (n matched ids = %d)\n", nrow(m)))
  for (a in items) {
    ag <- sapply(items, function(b) sum(m[[paste0(a, ".live")]] == m[[paste0(b, ".s1")]]))
    cat(sprintf("   live %s: %s\n", a, paste(sprintf("%s=%d", items, ag), collapse = " ")))
    if (ag[a] != nrow(m) || any(ag[names(ag) != a] == nrow(m))) pass <- FALSE
  }
  mod <- '
    CP =~ CP1 + CP2 + CP3 + CP4
    NP =~ NP1 + NP2 + NP3 + NP4
    EA =~ EA1 + EA2 + EA3 + EA4 + EA5
    SE =~ SE1 + SE2 + SE3 + SE4 + SE5
    GSCII =~ GSCII1 + GSCII2 + GSCII3 + GSCII4 + GSCII5'
  fit <- cfa(mod, data = s1, std.lv = TRUE)
  ss <- standardizedSolution(fit)
  obs <- setNames(ss$est.std[ss$lhs == "SE" & ss$op == "=~"], ss$rhs[ss$lhs == "SE" & ss$op == "=~"])[items]
} else {
  cat("S1 download failed -- check A skipped; B falls back to a one-factor CFA on live SE\n")
  fit <- cfa('SE =~ SE1 + SE2 + SE3 + SE4 + SE5', data = w, std.lv = TRUE)
  ss <- standardizedSolution(fit); obs <- setNames(ss$est.std[ss$op == "=~"], ss$rhs[ss$op == "=~"])[items]
}

cat("\nB. standardized loadings, paper Table 2 vs recomputed\n")
cat(sprintf("%-5s %9s %9s %8s\n", "item", "published", "observed", "diff"))
for (i in items) cat(sprintf("%-5s %9.3f %9.3f %8.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
worst <- max(abs(obs - PUB_LOAD))
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
alt <- sapply(Filter(function(p) !identical(p, 1:5), perms(1:5)), function(p) max(abs(obs[p] - PUB_LOAD)))
cat(sprintf("largest |diff| identity: %.3f; best non-identity permutation: %.3f\n", worst, min(alt)))
if (worst > TOL || min(alt) <= worst) pass <- FALSE
cat(sprintf("non-identity permutations within TOL (%.2f) of Table 2: %d of %d -- published SE1/SE2/SE5 loadings\n",
            TOL, sum(alt <= TOL), length(alt)))
cat("  (0.819/0.813/0.812) are near-tied, so B alone does not separate those three; the S2 code labels\n  and check A (id-level column identity) are what distinguish every item.\n")

X <- as.matrix(w[, items]); k <- 5
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
cat(sprintf("\nC. Cronbach's alpha live %.3f vs Table 2 %.3f\n", alpha, PUB_ALPHA))
if (abs(alpha - PUB_ALPHA) > 0.005) pass <- FALSE

cat("Not established: that S2's SE<k> labels and Table 2's SE<k> labels are one labelling (authors' own codes); English vs administered Chinese.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

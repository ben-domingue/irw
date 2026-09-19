# verify_zhang_2025_environ_awareness.R -- Step 5b mapping check (batch_252).
# Copied from references/verify_template.R.
#
# Claim: live item EA<k> is the item the paper's S2 File appendix prints as
# "EA<k>: <wording>". The appendix prefixes each item with the very code the S1
# Data column carries (explicit code labels), and data/zhang_2025_green_supply_chain.py
# melts S1 columns matching ^EA\d+$ by name, so the IRW code IS the source column name.
#
# Falsifiable checks run here:
#   A. live EA<k> equals S1 Data column EA<k> id-for-id, and no other EA column
#      reaches full agreement (the live code -> S1 column tie);
#   B. 5-factor CFA on S1 (CP, NP, EA, SE, GSCII, as in the paper) reproduces the
#      paper's Table 2 (t002) standardized loadings keyed to EA1..EA5 --
#      0.847/0.765/0.695/0.663/0.701 -- and every non-identity permutation of the
#      five codes fits worse;
#   C. Cronbach's alpha of the live EA items vs Table 2 alpha 0.852.
# NOT established: that the S2 appendix's "EA<k>" labels and Table 2's "EA<k>"
# labels were assigned by the same hand (both are the authors' own codes; no
# statistic can test that), nor that the English matches the administered Chinese.

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhang_2025_environ_awareness"
PUB_LOAD <- c(EA1 = 0.847, EA2 = 0.765, EA3 = 0.695, EA4 = 0.663, EA5 = 0.701)  # Table 2 (t002)
PUB_ALPHA <- 0.852
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(w$id), ]
items <- paste0("EA", 1:5)

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
  sel <- ss$lhs == "EA" & ss$op == "=~"
  obs <- setNames(ss$est.std[sel], ss$rhs[sel])[items]
} else {
  cat("S1 download failed -- check A skipped; B falls back to a one-factor CFA on live EA\n")
  fit <- cfa('EA =~ EA1 + EA2 + EA3 + EA4 + EA5', data = w, std.lv = TRUE)
  ss <- standardizedSolution(fit); sel <- ss$op == "=~"
  obs <- setNames(ss$est.std[sel], ss$rhs[sel])[items]
}

cat("\nB. standardized loadings, paper Table 2 vs recomputed\n")
cat(sprintf("%-5s %9s %9s %8s\n", "item", "published", "observed", "diff"))
for (i in items) cat(sprintf("%-5s %9.3f %9.3f %8.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
worst <- max(abs(obs - PUB_LOAD))
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
alt <- sapply(Filter(function(p) !identical(p, 1:5), perms(1:5)), function(p) max(abs(obs[p] - PUB_LOAD)))
cat(sprintf("largest |diff| identity: %.3f; best non-identity permutation (of %d): %.3f\n",
            worst, length(alt), min(alt)))
if (worst > TOL || min(alt) <= worst) pass <- FALSE

X <- as.matrix(w[, items]); k <- 5
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
cat(sprintf("\nC. Cronbach's alpha live %.3f vs Table 2 %.3f\n", alpha, PUB_ALPHA))
if (abs(alpha - PUB_ALPHA) > 0.005) pass <- FALSE

cat("Not established: that S2's EA<k> labels and Table 2's EA<k> labels are one labelling (authors' own codes); English vs administered Chinese.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

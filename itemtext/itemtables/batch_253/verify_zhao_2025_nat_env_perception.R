# verify_zhao_2025_nat_env_perception.R -- Step 5b mapping check (batch_253).
# Copied from references/verify_template.R.
#
# Claim: live item NEP<k> is the item the paper's Table 1 (t001, "Measurement
# items", an image table) prints in the "Variable quantity" column as NEP<k>.
# Table 1 labels each wording with the very code the S1 Dataset column carries
# (explicit code labels), and data/zhao_2025_psych_recovery.py melts S1 columns
# NEP1..NEP6 by name, so the IRW code IS the source column name.
#
# Falsifiable checks run here:
#   A. live NEP<k> equals S1 column NEP<k> id-for-id, and no other NEP column
#      reaches full agreement (the live code -> S1 column tie; this is what would
#      break if the processing script had shifted a column range);
#   B. corroboration only: 5-factor CFA on S1 vs Table 4 (t004) loadings, which
#      the paper reports under its own internal codes NSP1-3/NFP1-3 for N=457,
#      while S1 is a 199-respondent "minimum data set". Loadings therefore do NOT
#      reproduce; the one prediction tested is the marker that NEP1/NSP1 has the
#      lowest loading of the six in both.
# NOT established: that Table 1's NEP<k> labels and the S1 column headers were
# assigned by the same hand (both are the authors' own codes; no statistic can
# test that), that NSP/NFP in Table 4 are NEP1-3/NEP4-6 in order, nor that the
# English matches the administered (Chinese) wording.

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhao_2025_nat_env_perception"
items <- paste0("NEP", 1:6)
PUB_LOAD <- c(NEP1 = 0.592, NEP2 = 0.752, NEP3 = 0.707, NEP4 = 0.708, NEP5 = 0.609, NEP6 = 0.637)  # t004, NSP1-3, NFP1-3
PUB_ALPHA <- 0.826  # t003, N = 457

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

s1_url <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0325755.s001"
tf <- tempfile(fileext = ".xlsx")
ok <- tryCatch({ download.file(s1_url, tf, mode = "wb", quiet = TRUE,
                               headers = c("User-Agent" = "Mozilla/5.0")); TRUE },
               error = function(e) FALSE)
if (!ok) { cat("S1 download failed -- cannot run check A\nVERDICT: FAIL\n"); quit(save = "no") }
s1 <- as.data.frame(readxl::read_excel(tf))
names(s1)[1] <- "id"
pass <- TRUE

m <- merge(w, s1[, c("id", items)], by = "id", suffixes = c(".live", ".s1"))
cat(sprintf("A. live vs S1 id-level agreement (live ids %d, S1 rows %d, matched %d)\n",
            nrow(w), nrow(s1), nrow(m)))
if (nrow(m) != nrow(w)) pass <- FALSE
for (a in items) {
  ag <- sapply(items, function(b) sum(m[[paste0(a, ".live")]] == m[[paste0(b, ".s1")]]))
  cat(sprintf("   live %s: %s\n", a, paste(sprintf("%s=%d", items, ag), collapse = " ")))
  if (ag[a] != nrow(m) || any(ag[names(ag) != a] == nrow(m))) pass <- FALSE
}

mod <- paste("NEP =~", paste(items, collapse = "+"),
             "\nLI =~", paste0("LI", 1:12, collapse = "+"),
             "\nPA =~", paste0("PA", 1:8, collapse = "+"),
             "\nREP =~", paste0("REP", 1:12, collapse = "+"),
             "\nPRE =~", paste0("PRE", 1:12, collapse = "+"))
ss <- standardizedSolution(cfa(mod, data = s1, std.lv = TRUE))
sel <- ss$lhs == "NEP" & ss$op == "=~"
obs <- setNames(ss$est.std[sel], ss$rhs[sel])[items]
cat("\nB. (corroboration) loadings, paper Table 4 (N=457) vs S1 CFA (N=199)\n")
for (i in items) cat(sprintf("   %-5s %7.3f %7.3f %7.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
cat(sprintf("   Spearman(published, observed) = %.2f\n", cor(PUB_LOAD, obs, method = "spearman")))
cat(sprintf("   lowest loading: published %s, observed %s\n", names(which.min(PUB_LOAD)), names(which.min(obs))))
if (names(which.min(obs)) != "NEP1") pass <- FALSE
X <- as.matrix(w[, items]); k <- 6
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
cat(sprintf("   alpha live %.3f vs Table 3 %.3f (different N; informational)\n", alpha, PUB_ALPHA))

cat("Mapping rests on Table 1's explicit NEP<k> code labels + check A; B is corroboration, not proof.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_zhao_2025_place_attachment.R -- Step 5b mapping check (batch_254).
# Copied from references/verify_template.R.
#
# Claim: live item PA<k> is the item the paper's Table 1 (t001, "Measurement
# items", an image table) prints in its "Variable quantity" column as PA<k>.
# Table 1 labels each wording with the very code the S1 Dataset column carries
# (explicit code labels), and data/zhao_2025_psych_recovery.py melts S1 columns
# PA1..PA8 by name, so the IRW code IS the source column name.
#
# Falsifiable checks run here:
#   A. live PA<k> equals S1 column PA<k> id-for-id, and no other PA column
#      reaches full agreement (the live code -> S1 column tie; this is what would
#      break if the processing script had shifted or permuted a column range);
#   B. corroboration only: the paper splits PA into place dependence (Table 4
#      PD1-4) and place identity (PI1-4). Table 1's wording puts the
#      dependence-type items ("meet my needs", "irreplaceable", "best place for
#      me to do what I love", "more important to me") at PA1-4 and the
#      identity-type items ("part of my life", "special to me", "find myself",
#      "means a lot") at PA5-8. Prediction: mean within-block r exceeds mean
#      cross-block r. Also a 5-factor CFA on S1 vs Table 4 loadings (N=457 vs
#      S1's 199-respondent minimum data set -- informational, not decisive).
# NOT established: that Table 1's PA<k> labels and the S1 headers were assigned
# by one hand (both are the authors' own codes; no statistic can test that),
# that PD1-4/PI1-4 are PA1-4/PA5-8 in order, nor that the English matches the
# administered (Chinese) wording.

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhao_2025_place_attachment"
items <- paste0("PA", 1:8)
PUB_LOAD <- c(PA1 = 0.710, PA2 = 0.684, PA3 = 0.725, PA4 = 0.720,
              PA5 = 0.742, PA6 = 0.727, PA7 = 0.733, PA8 = 0.793)  # t004, PD1-4, PI1-4
PUB_ALPHA <- 0.904  # t003, N = 457

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
best_other <- 0
for (a in items) {
  ag <- sapply(items, function(b) sum(m[[paste0(a, ".live")]] == m[[paste0(b, ".s1")]]))
  cat(sprintf("   live %s: %s\n", a, paste(sprintf("%s=%d", items, ag), collapse = " ")))
  best_other <- max(best_other, ag[names(ag) != a])
  if (ag[a] != nrow(m) || any(ag[names(ag) != a] == nrow(m))) pass <- FALSE
}
cat(sprintf("   best off-diagonal agreement: %d/%d\n", best_other, nrow(m)))

X <- as.matrix(w[, items])
R <- cor(X)
pd <- items[1:4]; pi <- items[5:8]
within <- c(R[pd, pd][upper.tri(R[pd, pd])], R[pi, pi][upper.tri(R[pi, pi])])
cross <- as.vector(R[pd, pi])
cat(sprintf("\nB1. (corroboration) mean r within PD(PA1-4)/PI(PA5-8) blocks %.3f vs cross-block %.3f\n",
            mean(within), mean(cross)))
if (mean(within) <= mean(cross)) pass <- FALSE

mod <- paste("NEP =~", paste0("NEP", 1:6, collapse = "+"),
             "\nLI =~", paste0("LI", 1:12, collapse = "+"),
             "\nPA =~", paste(items, collapse = "+"),
             "\nREP =~", paste0("REP", 1:12, collapse = "+"),
             "\nPRE =~", paste0("PRE", 1:12, collapse = "+"))
ss <- standardizedSolution(cfa(mod, data = s1, std.lv = TRUE))
sel <- ss$lhs == "PA" & ss$op == "=~"
obs <- setNames(ss$est.std[sel], ss$rhs[sel])[items]
cat("\nB2. (informational) loadings, paper Table 4 (N=457) vs S1 CFA (N=199)\n")
for (i in items) cat(sprintf("   %-4s %7.3f %7.3f %7.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
cat(sprintf("   max |diff| = %.3f; Spearman(published, observed) = %.2f\n",
            max(abs(obs - PUB_LOAD)), cor(PUB_LOAD, obs, method = "spearman")))
k <- 8
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
cat(sprintf("   alpha live %.3f vs Table 3 %.3f (different N; informational)\n", alpha, PUB_ALPHA))

cat("Mapping rests on Table 1's explicit PA<k> code labels + check A; B is corroboration, not proof.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

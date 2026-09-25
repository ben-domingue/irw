# verify_zhao_2025_leisure_involvement.R -- Step 5b mapping check (batch_442).
# Copied from references/verify_template.R; mirrors the batch_253/254 sibling checks.
#
# Claim: live item LI<k> is the item the paper's Table 1 (t001, "Measurement
# items", an image table) prints in its "Variable quantity" column as LI<k>.
# Table 1 labels each wording with the very code the S1 Dataset column carries
# (explicit code labels), and data/zhao_2025_psych_recovery.py melts S1 columns
# LI1..LI12 by name, so the IRW code IS the source column name.
#
# Falsifiable checks:
#   A. live LI<k> equals S1 column LI<k> id-for-id, and no other LI column
#      reaches full agreement (breaks if the processing script shifted/permuted
#      a column range) -- GATED;
#   B. informational only: 5-factor CFA on S1 (N=199) vs Table 4 loadings
#      (N=457, printed under internal codes ATT1-4/CEN1-4/IE1-4), and alpha vs
#      Table 3. Different samples, so not decisive and not gated.
# NOT established: that Table 1's LI<k> labels and the S1 headers were assigned
# by one hand (authors' own codes, untestable by statistics); that ATT/CEN/IE
# are LI1-4/5-8/9-12 in order; nor that the English matches the administered
# (Chinese) wording.

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhao_2025_leisure_involvement"
items <- paste0("LI", 1:12)
PUB_LOAD <- setNames(c(0.681, 0.679, 0.700, 0.760, 0.707, 0.882, 0.644, 0.621,
                       0.647, 0.581, 0.630, 0.604), items)  # t004 ATT1-4, CEN1-4, IE1-4
PUB_ALPHA <- 0.911  # t003, N = 457

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
  ag <- sapply(items, function(b) sum(m[[paste0(a, ".live")]] == m[[paste0(b, ".s1")]], na.rm = TRUE))
  cat(sprintf("   live %-4s: %s\n", a, paste(sprintf("%s=%d", items, ag), collapse = " ")))
  best_other <- max(best_other, ag[names(ag) != a])
  if (ag[a] != nrow(m) || any(ag[names(ag) != a] == nrow(m))) pass <- FALSE
}
cat(sprintf("   best off-diagonal agreement: %d/%d\n", best_other, nrow(m)))

mod <- paste("NEP =~", paste0("NEP", 1:6, collapse = "+"),
             "\nLI =~", paste(items, collapse = "+"),
             "\nPA =~", paste0("PA", 1:8, collapse = "+"),
             "\nREP =~", paste0("REP", 1:12, collapse = "+"),
             "\nPRE =~", paste0("PRE", 1:12, collapse = "+"))
ss <- standardizedSolution(cfa(mod, data = s1, std.lv = TRUE))
sel <- ss$lhs == "LI" & ss$op == "=~"
obs <- setNames(ss$est.std[sel], ss$rhs[sel])[items]
cat("\nB. (informational) loadings, paper Table 4 (N=457) vs S1 CFA (N=199)\n")
for (i in items) cat(sprintf("   %-4s %7.3f %7.3f %7.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
cat(sprintf("   max |diff| = %.3f; Spearman(published, observed) = %.2f\n",
            max(abs(obs - PUB_LOAD)), cor(PUB_LOAD, obs, method = "spearman")))
X <- as.matrix(w[, items])
k <- length(items)
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
cat(sprintf("   alpha live %.3f vs Table 3 %.3f (different N; informational)\n", alpha, PUB_ALPHA))

cat("Mapping rests on Table 1's explicit LI<k> code labels + check A; B is corroboration, not proof.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_zhao_2025_psych_recovery_eval.R -- Step 5b mapping check (batch_254).
# Copied from references/verify_template.R.
#
# Claim: live item PRE<k> is the item the paper's Table 1 (t001, "Measurement
# items", an image table) prints in its "Variable quantity" column as PRE<k>.
# Table 1 labels each wording with the very code the S1 Dataset column carries
# (explicit code labels), and data/zhao_2025_psych_recovery.py melts S1 columns
# PRE1..PRE12 by name, so the IRW code IS the source column name.
#
# Falsifiable checks run here:
#   A. live PRE<k> equals S1 column PRE<k> id-for-id, and no other PRE column
#      reaches full agreement (the live code -> S1 column tie; this is what would
#      break if the processing script had shifted a column range);
#   B. corroboration only: 3-factor CFA on S1 (PRE1-4 / PRE5-8 / PRE9-12) vs the
#      Table 4 (t004) loadings, printed under internal codes MR1-4 (mental
#      recovery), ER1-4 (emotional), AR1-4 (attention) for N=457, while S1 is a
#      199-respondent "minimum data set". Loadings are not expected to reproduce
#      and are not gated on.
# NOT established: that Table 1's PRE<k> labels and the S1 column headers were
# assigned by the same hand (both are the authors' own codes; no statistic can
# test that), that MR/ER/AR in Table 4 are PRE1-4/5-8/9-12 in order, nor that the
# English matches the administered (Chinese) wording.

suppressMessages({ library(irw); library(lavaan) })
TABLE <- "zhao_2025_psych_recovery_eval"
items <- paste0("PRE", 1:12)
PUB_LOAD <- setNames(c(0.705, 0.708, 0.732, 0.705, 0.655, 0.693, 0.730, 0.755,
                       0.669, 0.698, 0.676, 0.658), items)  # t004, MR1-4, ER1-4, AR1-4

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
  oth <- max(ag[names(ag) != a]); best_other <- max(best_other, oth)
  cat(sprintf("   live %-5s own=%d  best other=%d (%s)\n", a, ag[a], oth,
              names(ag)[names(ag) != a][which.max(ag[names(ag) != a])]))
  if (ag[a] != nrow(m) || any(ag[names(ag) != a] == nrow(m))) pass <- FALSE
}
cat(sprintf("   max agreement with any non-matching column: %d/%d\n", best_other, nrow(m)))

mod <- paste("MR =~", paste(items[1:4], collapse = "+"),
             "\nER =~", paste(items[5:8], collapse = "+"),
             "\nAR =~", paste(items[9:12], collapse = "+"))
ss <- standardizedSolution(cfa(mod, data = s1, std.lv = TRUE))
sel <- ss$op == "=~"
obs <- setNames(ss$est.std[sel], ss$rhs[sel])[items]
cat("\nB. (corroboration, not gated) loadings, paper Table 4 (N=457) vs S1 3-factor CFA (N=199)\n")
for (i in items) cat(sprintf("   %-6s %7.3f %7.3f %7.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))
cat(sprintf("   max |diff| = %.3f; Spearman(published, observed) = %.2f\n",
            max(abs(obs - PUB_LOAD)), cor(PUB_LOAD, obs, method = "spearman")))

cat("Mapping rests on Table 1's explicit PRE<k> code labels + check A; B is corroboration, not proof.\n")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

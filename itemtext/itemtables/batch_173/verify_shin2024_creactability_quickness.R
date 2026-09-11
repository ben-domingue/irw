# verify_shin2024_creactability_quickness.R -- Step 5b mapping check (batch_173).
#
# Claim: Quickness1 / Quickness2 / Quickness3 carry the paper's Table 2 Quickness rows
# 1 / 2 / 3 ("He (she) makes a decision quickly" / "reacts quickly" / "figures out match situations quickly"),
# Shin, Kim, Lee & Lee (2025) Front. Sports Act. Living 7:1521073, doi:10.3389/fspor.2025.1521073.
# Codes are the figshare xlsx's own column names (no rename, no positional step), but the xlsx
# carries no wording, so the code -> text tie is an ORDER inference (paper_order). This checks it.
#
# Route 1 (per-item statistic): Table 3 publishes a Rasch item logit for items 1-9 (Table 2 order:
# Quickness 1-3, Creativity 4-6, Adaptability 7-9). With complete data (241 x 9, no missing) the
# Rasch item measure is a strictly monotone function of the item's raw total, so the published
# logits must be a (near-linear over this narrow range) function of the live per-item totals under
# the correct assignment. Each of the 9 totals is distinct, so the fit distinguishes every item.
# Live per-item x resp counts are computed server-side (GROUP BY; no table export) for this table
# and its two siblings (read-only queries).
#
# Route 9 (resp axis): Table 4 publishes the pooled category frequencies over all 9 items
# (1..7 = 19/142/398/429/610/441/130); the live counts must equal them cell for cell, which pins
# that IRW stores the study's own 1-7 coding in the analysed direction (not reversed).
#
# Bridge: live Quickness counts must equal the figshare xlsx columns (source of the codes).

suppressMessages({ library(irw) })

TABLE <- "shin2024_creactability_quickness"
SIBS  <- c(TABLE, "shin2024_creactability_creativity", "shin2024_creactability_adaptability")
ITEM_ORDER <- c(paste0("Quickness", 1:3), paste0("Creativity", 1:3), paste0("Adaptability", 1:3))
PUB_LOGIT <- c(-0.37, 0.16, -0.10, 0.12, -0.05, -0.02, -0.25, 0.23, 0.28)   # Table 3, items 1..9
PUB_FREQ  <- c(19, 142, 398, 429, 610, 441, 130)                            # Table 4, scale 1..7
TOL <- 0.01   # logits published to 2 dp

src <- irw:::.irw_resolve_source(source = "core")
counts <- function(tb) {
  ref <- irw:::.fetch_redivis_table(tb, source = src)$qualified_reference
  q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                     "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp, COUNT(*) AS n",
                     "FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                     "GROUP BY item, resp"), ref)
  x <- as.data.frame(irw:::.irw_query_tibble(q)); x$resp <- as.numeric(x$resp); x$n <- as.numeric(x$n); x
}
live <- do.call(rbind, lapply(SIBS, counts))
ok <- TRUE

tot <- sapply(ITEM_ORDER, function(it) { d <- live[live$item == it, ]; sum(d$resp * d$n) })
nn  <- sapply(ITEM_ORDER, function(it) sum(live$n[live$item == it]))
cat("== Route 1: live per-item totals vs Table 3 Rasch logits (claimed assignment) ==\n")
fit <- lm(PUB_LOGIT ~ tot)
cat(sprintf("%-4s %-14s %5s %7s %8s %9s %8s\n", "no.", "item", "n", "total", "mean", "pub logit", "resid"))
for (i in 1:9) cat(sprintf("%-4d %-14s %5d %7d %8.3f %9.2f %8.4f\n", i, ITEM_ORDER[i], nn[i], tot[i],
                           tot[i] / nn[i], PUB_LOGIT[i], resid(fit)[i]))
sp <- cor(tot, PUB_LOGIT, method = "spearman")
mr <- max(abs(resid(fit)))
cat(sprintf("Spearman(total, logit) = %.3f; linear fit slope %.5f logit/point; max |resid| = %.4f (tol %.2f)\n",
            sp, coef(fit)[2], mr, TOL))
cat("(Table 3's logits run in the easiness direction here -- higher logit = higher total -- despite the\n",
    " caption 'item difficulty'; a difficulty orientation would force a full reversal of the Table 2\n",
    " numbering across all three subscales, contradicting the subscale-named columns.)\n", sep = "")
if (!(sp == 1 && mr <= TOL)) ok <- FALSE

cat("\nAll 6 assignments of Table 2 Quickness rows 1-3 (Table 3 items 1-3) to the live codes:\n")
perms <- list(c(1,2,3), c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
fits <- 0
for (p in perms) {
  t2 <- tot; t2[1:3] <- tot[1:3][p]
  r <- max(abs(resid(lm(PUB_LOGIT ~ t2))))
  good <- r <= TOL; fits <- fits + good
  cat(sprintf("  rows 1,2,3 -> Quickness%d,%d,%d : max |resid| %.4f  spearman %.2f %s\n",
              p[1], p[2], p[3], r, cor(t2, PUB_LOGIT, method = "spearman"), if (good) "FIT" else ""))
}
if (fits != 1) ok <- FALSE

cat("\nUniqueness over all 9 items (claimed fit's line): published logit -> items whose predicted logit is within tol:\n")
pred <- predict(fit)
for (i in 1:9) {
  hit <- ITEM_ORDER[abs(pred - PUB_LOGIT[i]) <= TOL]
  cat(sprintf("  item %d (%.2f): %s\n", i, PUB_LOGIT[i], paste(hit, collapse = ", ")))
  if (!identical(hit, ITEM_ORDER[i])) ok <- FALSE
}

cat("\n== Route 9: pooled live category counts (9 items) vs Table 4 ==\n")
lf <- sapply(1:7, function(k) sum(live$n[live$resp == k & live$item %in% ITEM_ORDER]))
cat(sprintf("  resp %d: live %4d  pub %4d\n", 1:7, lf, PUB_FREQ), sep = "")
if (!all(lf == PUB_FREQ)) ok <- FALSE
cat(sprintf("  reversed coding would give live 1..7 = %s\n", paste(rev(lf), collapse = "/")))

cat("\n== Bridge: live Quickness counts vs figshare xlsx columns ==\n")
xl <- tempfile(fileext = ".xlsx")
got <- tryCatch({ utils::download.file("https://ndownloader.figshare.com/files/48672955", xl,
                                       mode = "wb", quiet = TRUE); TRUE }, error = function(e) FALSE)
if (got && requireNamespace("readxl", quietly = TRUE)) {
  fx <- as.data.frame(readxl::read_excel(xl))
  for (it in paste0("Quickness", 1:3)) {
    s <- sapply(1:7, function(k) sum(fx[[it]] == k)); l <- sapply(1:7, function(k) sum(live$n[live$item == it & live$resp == k]))
    cat(sprintf("  %-14s xlsx %s | live %s %s\n", it, paste(s, collapse = "/"), paste(l, collapse = "/"),
                if (all(s == l)) "match" else "MISMATCH"))
    if (!all(s == l)) ok <- FALSE
  }
} else cat("  figshare download unavailable -- bridge skipped (routes 1 and 9 above do not depend on it)\n")

cat("\nESTABLISHED: deposit columns Quickness1/2/3 = Table 3 items 1/2/3; resp 1..7 = Table 4 categories 1..7.\n",
    "NOT established: (a) which Table 2 wording is item 1, 2 or 3 -- Table 2 is UNNUMBERED, so Table 3's\n",
    "item number -> wording tie rests on listed row order, which no statistic here can test (ledger PARTIAL);\n",
    "(b) the Korean wording coaches actually read (unpublished).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

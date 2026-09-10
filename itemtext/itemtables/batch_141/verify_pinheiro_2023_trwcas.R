# verify_pinheiro_2023_trwcas.R -- batch_141
#
# READ THE CONTRACT BEFORE READING THE VERDICT.
#
# pinheiro_2023_trwcas is BLOCKED: no pinheiro_2023_trwcas__items.csv was written.
# The round's recorded claim is NOT "the shipped mapping is right" -- nothing shipped.
# The claim is the negative one:
#
#     the hypothesis that this deposit's item codes ct_1..ct_38 are item numbers
#     1..38 of the 40-item TRWCAS/EACTDR pool is CONTRADICTED by the live data.
#
# So this script PASSES when that contradiction reproduces, and would FAIL if a
# future irw::irw_fetch() showed the block structure the hypothesis predicts --
# which would mean the round's blocking decision was wrong and the table should
# be re-opened. Read the printed numbers, not just the last line.
#
# Sources for the hypothesis being tested (both cached under
# itemtext/.cache/pinheiro_2023_trwcas/):
#   - Cunha et al., Psico-USF 29:e272895 (2024), doi:10.1590/1413-8271202429e272895,
#     CC BY 4.0. Table 2 = EFA of the EACTDR, item numbers -> wording -> factor.
#   - Rodrigues, UVA technical report (ebook_ptp_0125), whose visible R code gives
#     the code -> factor assignment in exactly this ct1..ct40 naming, and whose
#     Tabelas 15.4-15.6 give the administered Portuguese wording and per-item M/SD
#     in the developers' own basic-education sample.
#
# This fetches the whole table (5,405 rows) because it needs the correlation
# matrix; set-only checks would use irw_table_sets() instead.

suppressMessages({library(irw); library(dplyr); library(tidyr)})

TABLE <- "pinheiro_2023_trwcas"

# --- the hypothesis -----------------------------------------------------------
# EACTDR factor membership by pool item number, restricted to the codes that
# actually exist in this table. From the UVA report's across(c(...)) calls.
G <- list(
  organizacao = c("ct_1","ct_4","ct_12","ct_13","ct_17","ct_19","ct_22","ct_23","ct_37"),
  condicoes   = c("ct_16","ct_20","ct_33","ct_36","ct_38"),
  relacoes    = c("ct_6","ct_15","ct_27","ct_29","ct_32")
)

# Per-item means published for the same pool numbers in the developers' own
# basic-education sample (UVA report, Tabelas 15.4 / 15.5 / 15.6).
REF <- c(ct_1=2.89, ct_4=2.52, ct_12=3.91, ct_13=3.69, ct_17=2.70, ct_19=3.62,
         ct_22=2.67, ct_23=3.17, ct_37=3.24,
         ct_16=2.46, ct_20=2.95, ct_33=2.20, ct_36=2.63, ct_38=2.85,
         ct_6=1.60,  ct_15=2.04, ct_27=1.62, ct_29=1.66, ct_32=1.63)

# Content pairs the hypothesis makes strong predictions about.
SYNONYMS <- list(
  c("ct_6","ct_32","no autonomy over class CONTENT vs over teaching METHODS"),
  c("ct_33","ct_36","noisy workspace vs uncomfortable workspace"),
  c("ct_15","ct_27","teachers excluded from decisions vs no manager support")
)
UNRELATED <- list(
  c("ct_31","ct_32","borrowed computer vs no autonomy over methods"),
  c("ct_27","ct_31","no manager support vs borrowed computer"),
  c("ct_1","ct_2","no rest breaks vs no integration with other teachers"),
  c("ct_23","ct_29","remote hinders student interaction vs conflicts among teachers")
)

# --- data ---------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
stopifnot(nrow(d) > 0)
w <- d |> select(id, item, resp) |> pivot_wider(names_from = item, values_from = resp)
X <- as.matrix(w[, setdiff(names(w), "id")])
m <- cor(X, use = "pairwise.complete.obs")
mu <- colMeans(X, na.rm = TRUE)
cat(sprintf("n = %d respondents, %d items\n\n", nrow(X), ncol(X)))

blk <- function(a, b) {
  v <- m[a, b, drop = FALSE]
  if (identical(a, b)) mean(v[upper.tri(v)]) else mean(v)
}

# --- test 1: block structure --------------------------------------------------
cat("--- TEST 1: does the published 3-factor block structure appear? ---\n")
for (i in names(G)) cat(sprintf("  within %-12s mean r = %.3f  (%d items)\n", i, blk(G[[i]], G[[i]]), length(G[[i]])))
within  <- mean(vapply(names(G), function(i) blk(G[[i]], G[[i]]), 0))
between <- mean(c(blk(G$organizacao, G$condicoes),
                  blk(G$organizacao, G$relacoes),
                  blk(G$condicoes,  G$relacoes)))
cat(sprintf("  mean WITHIN-factor r  = %.3f\n", within))
cat(sprintf("  mean BETWEEN-factor r = %.3f\n", between))
cat(sprintf("  separation (within - between) = %+.3f   [hypothesis predicts clearly positive]\n\n", within - between))

# --- test 2: content pairs ----------------------------------------------------
cat("--- TEST 2: do near-synonymous items cohere, and unrelated ones not? ---\n")
syn <- vapply(SYNONYMS, function(p) m[p[1], p[2]], 0)
unr <- vapply(UNRELATED, function(p) m[p[1], p[2]], 0)
for (k in seq_along(SYNONYMS)) cat(sprintf("  SYNONYM   %-6s x %-6s r = %.3f   %s\n", SYNONYMS[[k]][1], SYNONYMS[[k]][2], syn[k], SYNONYMS[[k]][3]))
for (k in seq_along(UNRELATED)) cat(sprintf("  UNRELATED %-6s x %-6s r = %.3f   %s\n", UNRELATED[[k]][1], UNRELATED[[k]][2], unr[k], UNRELATED[[k]][3]))
cat(sprintf("  max synonym r = %.3f ; min unrelated r = %.3f  [hypothesis predicts synonyms far above]\n\n",
            max(syn), min(unr)))

# --- test 3: published per-item means -----------------------------------------
cat("--- TEST 3: per-item means vs the developers' own sample (same pool numbers) ---\n")
cat(sprintf("  %-7s %8s %8s %8s\n", "item", "IRW", "report", "diff"))
for (k in names(REF)) cat(sprintf("  %-7s %8.2f %8.2f %+8.2f\n", k, mu[[k]], REF[[k]], mu[[k]] - REF[[k]]))
rho <- cor(mu[names(REF)], REF, method = "spearman")
cat(sprintf("  Spearman rank correlation over %d shared items = %.3f  [hypothesis predicts high]\n\n",
            length(REF), rho))

# --- verdict ------------------------------------------------------------------
# The hypothesis is contradicted if the block structure is absent AND the synonym
# pairs fail to separate from the unrelated ones AND the item-mean rank agreement
# is weak. All three must reproduce for the block to stand.
no_blocks   <- (within - between) < 0.05
no_semantic <- max(syn) < min(unr)
no_means    <- rho < 0.50

cat("contradiction components:\n")
cat(sprintf("  no block structure (within-between < 0.05)      : %s\n", no_blocks))
cat(sprintf("  synonyms weaker than unrelated pairs            : %s\n", no_semantic))
cat(sprintf("  item-mean rank agreement weak (rho < 0.50)      : %s\n", no_means))
cat("\nWhat this does NOT establish: what ct_N actually refers to. These routes only\n",
    "rule out the one candidate mapping, which is why the verification row reads\n",
    "NO_ROUTE and no item text was shipped. Deciding it needs the university\n",
    "adaptation's own paper (Psicologia em Pesquisa v.20, 2026, e44013), which\n",
    "returns HTTP 401 from this environment.\n", sep = "")

cat(if (no_blocks && no_semantic && no_means) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

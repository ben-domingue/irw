# Verification for hao_2025_metacognitive_regulation (batch_456).
#
# CLAIM. The IRW code IS the deposit's column name (data/hao_2025_foreign_language_anxiety.py
# melts MR1..MR7 by name), but the deposit (figshare 10.6084/m9.figshare.30397234, one
# .xlsx, header row only) carries no item wording, and Hao et al.'s preprint
# (Research Square rs-7750527/v1) prints only one example item. The wording comes from the
# instrument's source, Guo & Li (2022) Front Psychol 13:1046340, Appendix 1 (Table_1.docx),
# whose retained metacognitive-resilience items are original items 9-15 in that order.
# Mapping assumed: MRk = Guo & Li item (8 + k). This is a paper_order inference.
#
# Route (cross-sample item-mean profile): Guo & Li Table 1 publishes per-item means for
# items 9-15 (N=313 Chinese college EFL students, 7-point). If MR1..MR7 follow that order,
# the live per-item means (N=650 junior-high students, 1-5) should rank the items the same
# way. The route is PARTIAL by construction: different samples and scales, and two live
# means tie exactly, so it cannot separate every item from every other.
#
# Also printed (sibling corroboration of the block-order convention, same deposit): ER1-4
# vs Guo & Li items 1,2,3,6 and SR1-8 vs items 17-24, computed from the deposit xlsx if
# cached (not part of the verdict).
suppressMessages(library(irw))
TABLE <- "hao_2025_metacognitive_regulation"
GUO_MR <- c(4.92, 4.71, 4.80, 5.04, 4.98, 4.73, 4.84)   # Guo & Li 2022 Table 1, items 9..15
names(GUO_MR) <- paste0("MR", 1:7)

d <- as.data.frame(irw::irw_fetch(TABLE))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
obs <- tapply(d$resp, as.character(d$item), mean)[names(GUO_MR)]
n   <- tapply(d$resp, as.character(d$item), length)[names(GUO_MR)]

cat(sprintf("%-5s %-8s %8s %10s %6s %9s\n", "item", "GuoItem", "Guo_M", "live_M", "n", "live_rank"))
rk <- rank(-obs)
for (i in 1:7) cat(sprintf("%-5s %-8d %8.2f %10.3f %6d %9.1f\n", names(obs)[i], 8 + i,
                           GUO_MR[i], obs[i], n[i], rk[i]))
rho <- cor(GUO_MR, obs, method = "spearman")
r   <- cor(GUO_MR, obs)
cat(sprintf("\nSpearman rho (Guo means vs live means, assumed mapping) = %.3f; Pearson r = %.3f\n", rho, r))

# exact permutation distribution: how many of the 5040 orderings do at least as well?
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:7)
rhos <- vapply(P, function(p) cor(GUO_MR, obs[p], method = "spearman"), 0)
p_perm <- mean(rhos >= rho - 1e-12)
cat(sprintf("share of all 5040 item orderings with rho >= observed: %.4f (%d)\n",
            p_perm, sum(rhos >= rho - 1e-12)))
cat(sprintf("top-3 by Guo (items 12,13,9 = MR4,MR5,MR1): live top-3 = %s\n",
            paste(names(sort(obs, decreasing = TRUE))[1:3], collapse = ",")))
cat(sprintf("lowest by Guo (item 10 = MR2): live lowest = %s\n", names(which.min(obs))))

x <- ".cache/hao_2025_metacognitive_regulation/data.xlsx"
if (file.exists(x) && requireNamespace("readxl", quietly = TRUE)) {
  s <- as.data.frame(readxl::read_excel(x))
  s <- s[!is.na(suppressWarnings(as.numeric(s$NAME))), ]
  er <- colMeans(s[paste0("ER", 1:4)]); sr <- colMeans(s[paste0("SR", 1:8)])
  cat(sprintf("\n[corroboration] ER1-4 vs Guo items 1,2,3,6 (4.86,4.57,5.60,6.29): rho = %.3f\n",
              cor(c(4.86, 4.57, 5.60, 6.29), er, method = "spearman")))
  cat(sprintf("[corroboration] SR1-8 vs Guo items 17-24: rho = %.3f\n",
              cor(c(4.73, 4.42, 4.82, 5.07, 4.87, 4.84, 4.64, 4.58), sr, method = "spearman")))
  mr <- colMeans(s[paste0("MR", 1:7)])
  cat(sprintf("[derivation] max |deposit column mean - live mean| over MR1..MR7 = %.2e\n",
              max(abs(mr - obs))))
}

cat("\nNOT ESTABLISHED: this is a cross-sample rank comparison, not a match of this study's own\n",
    "statistics (Hao et al. publish no per-item means or wording). MR6 and MR7 tie in the live\n",
    "data (3.398), so their order is not pinned; MR3 vs MR6/MR7 rank differently across samples.\n",
    "Status: PARTIAL. PASS below means the assumed order is strongly supported, not proven.\n", sep = "")
cat(if (rho >= 0.75 && p_perm <= 0.05) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

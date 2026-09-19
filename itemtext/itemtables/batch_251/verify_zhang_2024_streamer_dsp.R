# verify_zhang_2024_streamer_dsp.R -- Step 5b mapping check for zhang_2024_streamer_dsp.
#
# Claim: live SDSP1..SDSP4 carry the S1 Appendix 'Streamer's deceptive
# self-presentation' items 1..4 respectively (mapping_basis=paper_order).
#
# Route: paper Table 2 (Zhang & Liu 2024, PLOS ONE e0296908) prints standardized CFA
# loadings SDSP1=0.766, SDSP2=0.797, SDSP3=0.815, SDSP4=0.859 from the six-construct,
# 23-item CFA. We (a) refit that CFA on the study's S1 dataset (.s002 xlsx) and compare
# loadings, checking every non-identity permutation of the four fits worse, and
# (b) check each live IRW SDSP<k> is the S1 column of the same name, id-for-id, so the
# Table-2 loadings attach to the live codes.
#
# Informational (c): the paper says SDSP was reverse-scored "in the analysis stage".
# The S1 SDSP composite reproduces Table 3's analysis-stage mean/SD (3.681/1.027) with
# no transformation, so S1 (and IRW) store the post-reversal values. Whether that means
# resp 5 = agreement or disagreement with the appendix's English statements depends on
# what wording was administered (not released), so option_text is left blank. (c) is
# printed, not gated.
#
# What this does NOT establish: the tie between Table 2's code SDSP<k> and the S1
# Appendix's k-th numbered wording. The appendix prints the items as a numbered list
# under a construct heading without codes, and the four items differ only in their
# last word (misleading/deceptive/deceitful/dishonest), so no statistic can pin it.
# That step is presentation order and untestable from data. Hence status PARTIAL.

suppressMessages({library(irw); library(readxl); library(lavaan)})

TABLE <- "zhang_2024_streamer_dsp"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0296908.s002"
PUBLISHED <- c(SDSP1 = 0.766, SDSP2 = 0.797, SDSP3 = 0.815, SDSP4 = 0.859)
TOL <- 0.01

tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "Mozilla/5.0"))
s1 <- as.data.frame(read_excel(tf))

m <- "ATR=~ATR1+ATR2+ATR3+ATR4
EXP=~EXP1+EXP2+EXP3
PSI=~PSI1+PSI2+PSI3
VDSP=~VDSP1+VDSP2+VDSP3+VDSP4+VDSP5+VDSP6
SDSP=~SDSP1+SDSP2+SDSP3+SDSP4
INT=~INT1+INT2+INT3"
fit <- cfa(m, data = s1)
ss <- standardizedSolution(fit)
ss <- ss[ss$op == "=~" & ss$lhs == "SDSP", ]
obs <- setNames(ss$est.std, ss$rhs)[names(PUBLISHED)]

cat("(a) Table 2 loadings vs refit on S1 dataset\n")
cat(sprintf("%-6s %10s %10s %8s\n", "item", "published", "refit", "diff"))
for (k in names(PUBLISHED))
  cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", k, PUBLISHED[k], obs[k], obs[k] - PUBLISHED[k]))
worst <- max(abs(obs - PUBLISHED))
perm_all <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perm_all(v[-i]), function(p) c(v[i], p))))
perms <- Filter(function(p) !identical(p, 1:4), perm_all(1:4))
best_other <- min(sapply(perms, function(p) max(abs(obs[p] - PUBLISHED))))
cat(sprintf("largest deviation (identity): %.3f; best of %d non-identity permutations: %.3f\n",
            worst, length(perms), best_other))

cat("\n(b) live IRW SDSP<k> vs S1 column SDSP<k>, id-for-id\n")
d <- irw::irw_fetch(TABLE)
ok_b <- TRUE
for (k in names(PUBLISHED)) {
  lv <- d[d$item == k, c("id", "resp")]
  agree <- sapply(names(PUBLISHED), function(j) {
    s <- s1[match(lv$id, s1$Number), j]
    sum(s == lv$resp, na.rm = TRUE)
  })
  cat(sprintf("live %s: n=%d; agreement with S1 SDSP1/2/3/4 = %s\n",
              k, nrow(lv), paste(agree, collapse = "/")))
  if (agree[k] != nrow(lv) || any(agree[names(agree) != k] == nrow(lv))) ok_b <- FALSE
}

cat("\n(c) informational: storage direction\n")
comp <- rowMeans(s1[, names(PUBLISHED)])
cat(sprintf("S1 SDSP composite mean/SD as stored: %.3f/%.3f (Table 3: 3.681/1.027); if reversed: %.3f\n",
            mean(comp), sd(comp), mean(6 - comp)))
atr <- rowMeans(s1[, paste0("ATR", 1:4)]); psi <- rowMeans(s1[, paste0("PSI", 1:3)])
cat(sprintf("r(SDSP, ATR) = %.3f (Table 3: .115); r(SDSP, PSI) = %.3f (Table 3: .139)\n",
            cor(comp, atr), cor(comp, psi)))

cat("\nNot established: Table-2 code SDSP<k> <-> S1 Appendix item k (presentation order);\n")
cat("nor the anchor direction of resp relative to the appendix wording (option_text left blank).\n")
pass <- worst <= TOL && best_other > TOL && ok_b
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_zhang_2024_viewer_dsp.R -- Step 5b mapping check for zhang_2024_viewer_dsp.
#
# Claim: live VDSP1..VDSP6 carry the S1 Appendix "Viewer's deceptive self-presentation"
# items 1..6 respectively (mapping_basis=paper_order).
#
# Route: (a) the live IRW VDSP<k> are the S1 Dataset (pone.0296908.s002) columns of the
# same name, id-for-id, and no other column; (b) refitting the paper's six-construct,
# 23-item CFA on the S1 dataset reproduces Table 2's VDSP loadings per code, and the
# VDSP composite reproduces Table 3's mean/SD (items stored raw, 1=Strongly disagree).
# Together these pin each live code to the paper's own code VDSP<k>.
#
# What this does NOT establish: the tie between the paper's code VDSP<k> and the S1
# Appendix's k-th numbered wording. The appendix lists six same-polarity items under a
# construct heading without printing codes, and the paper publishes no statistic keyed
# to wording; that step is presentation order (paper_order), untestable from data.
# Hence status PARTIAL.

suppressMessages({library(irw); library(readxl); library(lavaan)})

TABLE <- "zhang_2024_viewer_dsp"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0296908.s002"
CODES <- paste0("VDSP", 1:6)
PUBLISHED <- c(VDSP1 = 0.791, VDSP2 = 0.904, VDSP3 = 0.853,
               VDSP4 = 0.804, VDSP5 = 0.823, VDSP6 = 0.797)   # Table 2
PUB_MEAN <- 3.450; PUB_SD <- 1.052                               # Table 3
TOL <- 0.002   # Table 2 is printed to 3 dp

tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, mode = "wb", quiet = TRUE)
s1 <- as.data.frame(read_excel(tf))

cat("(a) live IRW VDSP<k> vs S1 columns VDSP1..VDSP6, id-for-id agreement\n")
d <- irw::irw_fetch(TABLE)
ok_a <- TRUE
for (k in CODES) {
  lv <- d[d$item == k, c("id", "resp")]
  agree <- sapply(CODES, function(j) sum(s1[match(lv$id, s1$Number), j] == lv$resp, na.rm = TRUE))
  cat(sprintf("live %s: n=%d; agreement with S1 VDSP1..6 = %s\n", k, nrow(lv), paste(agree, collapse = "/")))
  if (agree[k] != nrow(lv) || any(agree[names(agree) != k] == nrow(lv))) ok_a <- FALSE
}

cat("\n(b) Table 2 loadings vs six-construct CFA refit on S1 dataset\n")
m <- "ATR=~ATR1+ATR2+ATR3+ATR4
EXP=~EXP1+EXP2+EXP3
PSI=~PSI1+PSI2+PSI3
VDSP=~VDSP1+VDSP2+VDSP3+VDSP4+VDSP5+VDSP6
SDSP=~SDSP1+SDSP2+SDSP3+SDSP4
INT=~INT1+INT2+INT3"
ss <- standardizedSolution(cfa(m, data = s1))
ss <- ss[ss$op == "=~" & ss$lhs == "VDSP", ]
obs <- setNames(ss$est.std, ss$rhs)[CODES]
cat(sprintf("%-6s %10s %10s %8s\n", "item", "published", "refit", "diff"))
for (k in CODES) cat(sprintf("%-6s %10.3f %10.3f %8.4f\n", k, PUBLISHED[k], obs[k], obs[k] - PUBLISHED[k]))
worst <- max(abs(obs - PUBLISHED))
perm <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perm(v[-i]), function(p) c(v[i], p))))
P <- perm(1:6); P <- P[!sapply(P, function(p) all(p == 1:6))]
best_other <- min(sapply(P, function(p) max(abs(obs[p] - PUBLISHED))))
cat(sprintf("largest deviation (identity): %.4f; best of %d non-identity permutations: %.4f\n",
            worst, length(P), best_other))

comp <- rowMeans(s1[, CODES])
cat(sprintf("\nVDSP composite mean/SD from S1: %.3f/%.3f vs Table 3 %.3f/%.3f\n",
            mean(comp), sd(comp), PUB_MEAN, PUB_SD))
ok_c <- abs(mean(comp) - PUB_MEAN) < 0.001 && abs(sd(comp) - PUB_SD) < 0.001

cat("\nNot established: paper code VDSP<k> <-> S1 Appendix item k (presentation order only).\n")
pass <- ok_a && worst <= TOL && best_other > TOL && ok_c
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_depue_2023_gds15.R -- Step 5b mapping check for depue_2023_gds15 (batch_521).
#
# Claim: IRW codes GDS1..GDS15 (the deposit's own column names, melted by name in
# data/depue_2023_covid_older_adults.py) are canonical GDS-15 items 1..15 in the
# Sheikh & Yesavage order, stored key-scored (1 = the depressive answer: NO for
# items 1,5,7,11,13, YES for the rest). The deposit has no labels, so this is
# RECONSTRUCTED from the instrument numbering and checked here against:
#   (A) every published GDS-15 total mean/SD and alpha in both papers -> the
#       stored values are key-scored sums, i.e. the shipped YES/NO direction;
#   (B) marker item 10 ("more problems with memory than most"): must be the GDS
#       item most associated with the study's own memory measures (CFQ total,
#       subjective "problems remembering"/"problems recalling" during COVID-19);
#   (C) semantic coherence at T1 (May-June 2020 lockdown): items 2 (dropped
#       activities) and 9 (prefer to stay at home) are the two most endorsed.
# What this does NOT establish: the order among the other 12 items. No per-item
# statistics are published, so items 1,3-8,11-15 are only shown to be
# consistently keyed, not individually placed. Status: PARTIAL.

suppressMessages(library(irw))
TABLE <- "depue_2023_gds15"
ok <- TRUE
d <- as.data.frame(irw::irw_fetch(TABLE))
G <- paste0("GDS", 1:15)
wide <- function(x) { w <- reshape(x[, c("id", "item", "resp")], idvar = "id",
                                   timevar = "item", direction = "wide")
                      names(w) <- sub("^resp\\.", "", names(w)); w[, c("id", G)] }
alpha <- function(X) { X <- X[complete.cases(X), ]; k <- ncol(X)
  k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }

# (A) published totals. De Pue et al. 2021 Sci Rep 11:4636 Table 1 (N=640, T1):
# 3.00 (3.01), alpha .81. De Pue et al. 2023 Sci Rep 13:9708 Table 2 (n=371):
# T1 2.60 (2.66), T2 2.59 (2.80), T3 2.77 (2.80), alphas .78/.80/.80;
# supplementary Table 4: T1 drop-outs n=269 3.56 (3.37).
w1 <- wide(d[d$wave == 1, ]); ids3 <- unique(d$id[d$wave == 3])
t1 <- rowSums(w1[, G], na.rm = TRUE)
cmp <- list(
  list("2021 T1 all (N=640)", t1, 3.00, 3.01, alpha(w1[, G]), 0.81),
  list("2023 T1 completers", t1[w1$id %in% ids3], 2.60, 2.66, alpha(w1[w1$id %in% ids3, G]), 0.78),
  list("2023 T1 drop-outs", t1[!w1$id %in% ids3], 3.56, 3.37, NA, NA))
for (w in 2:3) { ww <- wide(d[d$wave == w, ])
  cmp[[length(cmp) + 1]] <- list(sprintf("2023 T%d completers", w), rowSums(ww[, G]),
                                 c(NA, 2.59, 2.77)[w], 2.80, alpha(ww[, G]), 0.80) }
cat("(A) published GDS-15 totals vs live key-scored sums\n")
cat(sprintf("%-22s %4s %14s %14s %12s\n", "subset", "n", "pub M (SD)", "live M (SD)", "alpha p/l"))
for (c in cmp) {
  m <- mean(c[[2]]); s <- sd(c[[2]])
  cat(sprintf("%-22s %4d %6.2f (%4.2f) %6.2f (%4.2f) %5s/%5s\n", c[[1]], length(c[[2]]),
              c[[3]], c[[4]], m, s, ifelse(is.na(c[[6]]), "-", sprintf("%.2f", c[[6]])),
              ifelse(is.na(c[[5]]), "-", sprintf("%.2f", c[[5]]))))
  if (abs(m - c[[3]]) > 0.006 || abs(s - c[[4]]) > 0.006) ok <- FALSE
  if (!is.na(c[[6]]) && abs(c[[5]] - c[[6]]) > 0.01) ok <- FALSE
}
cat("  (the published totals are sums of these stored columns, 'higher = more depressive\n",
    "   symptoms'; this pins that the stored 0/1 is the authors' key score, not raw YES=1)\n", sep = "")
X <- w1[, G]; tt <- rowSums(X, na.rm = TRUE)
ir <- sapply(G, function(g) cor(X[[g]], tt - X[[g]], use = "pairwise"))
cat("  item-rest r at T1:", paste(sprintf("%s %.2f", G, ir), collapse = "; "), "\n")
cat("  (raw YES=1 storage would make items 1,5,7,11,13 correlate negatively)\n\n")
if (any(ir <= 0)) ok <- FALSE

# (B) marker item 10, against the study's own T1 file (osf.io/re7sm, CC BY 4.0).
raw <- read.csv2(url("https://osf.io/download/8bgnt/"), na.strings = c(" ", ""),
                 check.names = FALSE)
names(raw)[names(raw) == "Participant"] <- "id"
m <- merge(w1, raw[, c("id", paste0(G), "CFQ_total", "Remembering", "Recalling")],
           by = "id", suffixes = c("", ".raw"))
same <- sum(sapply(G, function(g) all(m[[g]] == m[[paste0(g, ".raw")]], na.rm = TRUE)))
cat(sprintf("(B) deposit T1 columns GDSk identical to live wave-1 item GDSk: %d/15 (n=%d)\n", same, nrow(m)))
if (same != 15) ok <- FALSE
cat(sprintf("%-6s %9s %11s %9s\n", "item", "CFQ_tot", "Remembering", "Recalling"))
R <- sapply(c("CFQ_total", "Remembering", "Recalling"), function(e)
  sapply(G, function(g) abs(cor(m[[g]], m[[e]], use = "pairwise"))))
for (g in G) cat(sprintf("%-6s %9.2f %11.2f %9.2f\n", g, R[g, 1], R[g, 2], R[g, 3]))
top <- apply(R, 2, function(v) names(which.max(v)))
cat("  item with largest |r| per memory measure:", paste(top, collapse = ", "), "\n")
cat(sprintf("  GDS10 margin over runner-up: %s\n", paste(sprintf("%.2f",
    apply(R, 2, function(v) diff(sort(v, decreasing = TRUE)[2:1]))), collapse = ", ")))
if (!all(top == "GDS10")) ok <- FALSE

# (C) endorsement at T1
p <- sort(colMeans(w1[, G], na.rm = TRUE), decreasing = TRUE)
cat("\n(C) T1 endorsement (proportion scored 1), N=640:\n")
cat(paste(sprintf("%s %.3f", names(p), p), collapse = "; "), "\n")
if (!setequal(names(p)[1:2], c("GDS2", "GDS9"))) ok <- FALSE
cat("\nNot established: the order among items 1,3-8,11-15 (no per-item statistics published).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

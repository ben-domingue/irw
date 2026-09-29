# verify_armour_2017_pcl5.R -- Step 5b check for armour_2017_pcl5 (batch_731).
#
# Claim: IRW item pcl5_n carries PCL-5 item n (DSM-5 B1-B5, C1-C2, D1-D7, E1-E6 in
# form order). Two links make that claim:
#   (a) data/armour_2017_pcl5.py renames OSF mj5wa PTSD_data.sav columns
#       Q28_01_MONTH..Q28_20_MONTH to pcl5_1..pcl5_20 (number-preserving). The .sav
#       has NO variable or value labels on these columns.
#   (b) The authors' own PTSD_code.R (same OSF node) names those 20 columns, in file
#       order, B1..E6 / "IntT","NgtM","FshB",...,"sDis", and the paper's results
#       state findings in those labels.
# Check 1 proves (a) exactly. Checks 2-4 test (b) against the paper's own
# reported results and against content-driven signatures. What this does NOT
# establish: it does not separate every item from every other (e.g. B4 vs B5,
# D2 vs D5 are not distinguished by any check), so the status is PARTIAL.

suppressMessages(library(irw))
TABLE <- "armour_2017_pcl5"
ok <- TRUE

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[order(as.numeric(w$id)), ]
X <- w[, paste0("pcl5_", 1:20)]

# ---- 1. live pcl5_n == deposit Q28_nn, column for column --------------------
tf <- tempfile(fileext = ".sav")
got <- tryCatch({download.file("https://osf.io/download/vuf6m/", tf, mode = "wb", quiet = TRUE); TRUE},
                error = function(e) FALSE)
if (got) {
  s <- haven::read_sav(tf)
  src <- sprintf("Q28_%02d_MONTH", 1:20)
  M <- sapply(1:20, function(j) sapply(1:20, function(k) isTRUE(all(as.numeric(s[[src[j]]]) == X[[k]]))))
  hit <- apply(M, 2, function(v) paste(which(v), collapse = "/"))
  cat("1. deposit column Q28_nn matches live pcl5_k exactly (id order, 221 values):\n")
  cat("   ", paste0("Q28_", sprintf("%02d", 1:20), "->", hit), "\n")
  c1 <- all(hit == as.character(1:20))
  cat("   identity mapping 20/20:", c1, "\n")
  ok <- ok && c1
} else {
  cat("1. could not download OSF PTSD_data.sav -- check skipped\n")
}

# ---- 2. paper's named strongest edges ---------------------------------------
# Paper 3.2: "especially strong connections emerged between nightmares (B2) and
# flashbacks (B3), blame of self or others (D3) and negative trauma-related
# emotions (D4), detachment (D6) and restricted affect (D7), and hypervigilance
# (E3) and exaggerated startle response (E4)."  -> pairs 2-3, 10-11, 13-14, 17-18
P <- -cov2cor(solve(cor(X))); diag(P) <- NA
ut <- which(upper.tri(P), arr.ind = TRUE)
e <- data.frame(a = ut[, 1], b = ut[, 2], pc = P[ut]); e <- e[order(-e$pc), ]
e$pair <- paste0(e$a, "-", e$b)
cat("\n2. top 6 unregularised partial correlations (of 190 pairs):\n")
print(head(e[, c("pair", "pc")], 6), row.names = FALSE, digits = 2)
want <- c("2-3", "10-11", "13-14", "17-18")
rk <- match(want, e$pair)
cat("   ranks of paper's strongest edges", paste(want, collapse = ","), ":", rk, "\n")
c2 <- all(rk <= 5); ok <- ok && c2

# ---- 3. paper's least-central nodes C1 (6) and D1 (8) -----------------------
st <- colSums(abs(P), na.rm = TRUE)
ord <- order(st)
cat("\n3. five weakest nodes by sum|partial r|:", paste0("pcl5_", ord[1:5], "(", round(st[ord[1:5]], 2), ")"), "\n")
c3 <- all(c(6, 8) %in% ord[1:5]); cat("   C1=pcl5_6 and D1=pcl5_8 both in bottom 5:", c3, "\n"); ok <- ok && c3

# ---- 4. marker item E2 "Taking too many risks..." = pcl5_16 ------------------
m <- colMeans(X); fl <- colMeans(X == 0)
cat("\n4. lowest mean item:", names(which.min(m)), round(min(m), 2),
    "(next lowest", names(sort(m))[2], round(sort(m)[2], 2), "); floor %:", round(100 * fl[16], 1), "\n")
c4 <- which.min(m) == 16 && which.max(fl) == 16
if (got) {
  r <- cor(as.matrix(X), as.numeric(s$Active_SI_FINAL), method = "spearman")[, 1]
  cat("   Spearman r with deposit Active_SI_FINAL, top 3:", paste0(names(sort(-r))[1:3], "=", round(sort(r, decreasing = TRUE)[1:3], 3)), "\n")
  cat("   (paper: E2 self-destructive behaviour has the SI edge, partial r 0.25)\n")
  c4 <- c4 && which.max(r) == 16
}
cat("   E2 marker holds:", c4, "\n"); ok <- ok && c4

cat("\nNOT established: order within blocks where no check reaches (e.g. pcl5_4 vs pcl5_5,\n",
    "pcl5_9 vs pcl5_12, pcl5_19 vs pcl5_20 are not individually pinned).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_enders_2022_vaccine_hesitancy.R -- Step 5b re-runnable check (batch_572)
#
# CLAIM. VAXHES_1..10 carry the S1 Appendix statements labelled "(Item 1)".."(Item 10)"
# (Enders, Uscinski, Klofstad & Stoler 2022, PLOS ONE e0276082, pone.0276082.s001), i.e.
# VAXHES_N = appendix "Item N"; and resp 1 = "strongly disagree", resp 5 = "strongly agree"
# (the REVERSE of the appendix's printed "(1=strongly agree, 5=strongly disagree)").
#
# DERIVATION. data/enders_2022_conspiracy_vaccine.py keeps the Qualtrics column names
# VAXHES_1..10 as `item`; Raw Data.csv has no question-text row and no codebook.
#
# ROUTE A (item mapping). The article's Table 2 prints, for "Vaccine Hesitancy Item 1..10",
# two unrotated iterated-principal-factor loadings and a uniqueness from a 21-item EFA
# (Analyses.do line 525: factor vaxhes_1-vaxhes_10 cpurpose-tracking covvaxinfo_1-covvaxinfo_5,
# ipf factor(2), after lines 154-156 reverse vaxhes_5/9/10). Re-run that EFA on live data
# and match every Table 2 row to the code whose (F1,F2,U) is nearest; the claim needs row N ->
# VAXHES_N for all 10, each with a clear margin over the runner-up.
# The link from Table 2's "Item N" to the appendix's "(Item N)" wording is the paper's own
# label. The same EFA's CTM rows show those labels are a consistent paper-internal key: Table 2's
# COVID-conspiracy rows 1..6 land on COVCONS_3,2,4,7,6,5 -- exactly the Table 1 "(Item N)" labels
# that batch_569 pinned independently from % agree. Printed below as a check on the key.
#
# ROUTE B (independent corroboration, partial). Keying polarity {5,9,10} (appendix "reversed")
# must be the negatively-correlated class; the two CDC items (4, 6) must be the two with the
# highest correlation with trust in public health officials (TRUST_PHO, raw column), with 6
# ("information ... from the CDC is reliable and trustworthy") the highest.
#
# ROUTE C (resp direction). Positive-worded items must be majority-agreed under 5=strongly agree
# and must correlate POSITIVELY with COVVAX (1 = vaccinated / will be; Analyses.do line 115).

suppressMessages(library(irw))

wide <- function(tab) {
  d <- as.data.frame(irw::irw_fetch(tab))[, c("id", "item", "resp")]
  w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
  names(w) <- sub("^resp\\.", "", names(w)); w
}
V  <- paste0("VAXHES_", 1:10)
wv <- wide("enders_2022_vaccine_hesitancy")
wc <- wide("enders_2022_covid_conspiracy")[, c("id", paste0("COVCONS_", 2:7))]
wm <- wide("enders_2022_covid_vax_misinfo")[, c("id", paste0("COVVAXINFO_", 1:5))]
m  <- merge(merge(wv[, c("id", V)], wc, by = "id"), wm, by = "id")
X  <- m[, -1]
for (k in c(5, 9, 10)) X[[V[k]]] <- 6 - X[[V[k]]]
X <- X[complete.cases(X), ]
cat("listwise n for EFA:", nrow(X), "\n")

ipf <- function(R, nf, iter = 2000, tol = 1e-9) {
  h <- 1 - 1 / diag(solve(R))
  for (i in 1:iter) {
    Rr <- R; diag(Rr) <- h; e <- eigen(Rr, symmetric = TRUE)
    L <- e$vectors[, 1:nf] %*% diag(sqrt(pmax(e$values[1:nf], 0)))
    hn <- rowSums(L^2); if (max(abs(hn - h)) < tol) break; h <- hn
  }
  list(L = L, u = 1 - rowSums(L^2), ev = e$values[1:nf])
}
f <- ipf(cor(X), 2); L <- f$L
if (mean(L[1:10, 1]) > 0) L[, 1] <- -L[, 1]
if (sum(L[1:10, 2]) < 0) L[, 2] <- -L[, 2]
Lv <- cbind(L[, 1], L[, 2], f$u); rownames(Lv) <- names(X)

# Table 2, Vaccine Hesitancy rows (F1, F2, uniqueness)
P <- rbind(c(-.737, .441, .263), c(-.731, .359, .337), c(-.759, .398, .266), c(-.680, .421, .361),
           c(-.565, -.101, .671), c(-.682, .366, .401), c(-.741, .413, .281), c(-.612, .426, .445),
           c(-.537, -.076, .706), c(-.620, -.032, .614))
ok <- TRUE
cat("\nROUTE A: Table 2 VHS row -> nearest live code (max |diff| over F1,F2,U)\n")
for (j in 1:10) {
  dv <- apply(abs(sweep(Lv[V, ], 2, P[j, ])), 1, max); o <- order(dv)
  cat(sprintf("Item %2d pub(%.3f %.3f %.3f) -> %-9s live(%.3f %.3f %.3f) dev %.4f | next %-9s dev %.4f\n",
              j, P[j, 1], P[j, 2], P[j, 3], V[o[1]], Lv[V[o[1]], 1], Lv[V[o[1]], 2], Lv[V[o[1]], 3],
              dv[o[1]], V[o[2]], dv[o[2]]))
  if (V[o[1]] != V[j] || dv[o[1]] > 0.01 || dv[o[2]] < 3 * dv[o[1]]) ok <- FALSE
}
cat(sprintf("eigenvalues %.3f %.3f (published 10.682 1.775)\n", f$ev[1], f$ev[2]))

Pc <- rbind(c(.664, .139, .540), c(.695, .198, .478), c(.824, .194, .284), c(.765, .302, .323),
            c(.720, .279, .404), c(.613, .339, .510))
CC <- paste0("COVCONS_", 2:7)
got <- sapply(1:6, function(j) CC[which.min(apply(abs(sweep(Lv[CC, ], 2, Pc[j, ])), 1, max))])
cat("\nKey check: Table 2 COVID-conspiracy rows 1..6 ->", got, "\n")
cat("  batch_569 Table 1 labels (from % agree):  COVCONS_3 COVCONS_2 COVCONS_4 COVCONS_7 COVCONS_6 COVCONS_5\n")
if (!identical(got, paste0("COVCONS_", c(3, 2, 4, 7, 6, 5)))) ok <- FALSE

cat("\nROUTE B: polarity (mean r with the 7 positive items) and r with TRUST_PHO\n")
R <- cor(wv[, V], use = "pairwise")
pos <- V[-c(5, 9, 10)]
mr <- sapply(V, function(v) mean(R[v, setdiff(pos, v)]))
print(round(mr, 3))
if (!all(mr[c(5, 9, 10)] < 0) || !all(mr[-c(5, 9, 10)] > 0)) ok <- FALSE
cand <- c(file.path(c(".", "..", "../.."), ".cache", "enders_2022_vaccine_hesitancy", "raw.csv"),
          file.path("itemtext", ".cache", "enders_2022_vaccine_hesitancy", "raw.csv"))
cand <- cand[file.exists(cand)]
raw <- if (length(cand)) read.csv(cand[1], check.names = FALSE) else NULL
if (!is.null(raw)) {
  raw$id <- seq_len(nrow(raw))   # processing script: id = row index + 1
  mm <- merge(wv, raw[, c("id", "TRUST_PHO", "COVVAX")], by = "id")
  rp <- sapply(V, function(v) cor(mm[[v]], mm$TRUST_PHO, use = "pairwise"))
  cat("r with TRUST_PHO:\n"); print(round(rp, 3))
  if (!identical(names(sort(rp[pos], decreasing = TRUE))[1:2], c("VAXHES_6", "VAXHES_4"))) ok <- FALSE
  rv <- sapply(V, function(v) cor(mm[[v]], mm$COVVAX, use = "pairwise"))
  cat("\nROUTE C: r with COVVAX (1 = vaccinated):\n"); print(round(rv, 3))
  if (!all(rv[pos] > 0.3)) ok <- FALSE
} else cat("raw.csv (OSF 6a7et Raw Data.csv) not cached -- routes B(trust)/C(COVVAX) skipped\n")
pa <- sapply(pos, function(v) mean(wv[[v]] >= 4, na.rm = TRUE))
cat("% resp>=4 on positive items:", round(100 * pa, 1), "\n")
if (!all(pa > 0.5)) ok <- FALSE

cat("\nNot established: that the authors' appendix '(Item N)' labels and Table 2 'Item N' labels\n",
    "denote the same statement is the paper's own labelling (shown consistent on the CTM block);\n",
    "route B independently pins only the reversed class {5,9,10} and the CDC pair {4,6}; the order\n",
    "within {1,2,3,7} and position 8 rest on Route A via that label.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_adamczyk_2022_cesd.R -- Step 5b check for adamczyk_2022_cesd (batch_520).
#
# Claim being checked: the live codes CESD1..CESD20 (a number-preserving rename of the
# OSF val2 .sav columns CESD1t1..CESD20t1; CSED16t1 typo fixed) are Radloff (1977)
# CES-D items 1..20 in canonical order, and the four positively worded items
# (4 just as good, 8 hopeful, 12 happy, 16 enjoyed life) are STORED ALREADY REVERSED,
# which is why the shipped anchors run descending for exactly those four codes.
#
# The .sav has no variable or value labels (both levels checked), so there is no
# data_labels route. Three falsifiable checks:
#   A. Storage direction: every item correlates POSITIVELY with the rest-score. A raw
#      positively-worded CES-D item correlates negatively, so a positive sign on all 20
#      means none is stored raw-positive -> the positive items were reversed.
#   B. The depositors' own 'Depression' column in the .sav equals the per-person MEAN
#      of the 20 live items exactly, with no further reversal -- i.e. the authors
#      scored the stored values as-is, which only makes sense if they are already
#      depression-direction.
#   C. After removing the general factor (first principal component), CESD8, CESD12 and
#      CESD16 are each other's two strongest residual partners -- a positive-affect
#      method cluster sitting at the canonical positions 8/12/16.
#
# What this does NOT establish: the order among the 16 negatively worded items, or the
# position of item 4 (CESD4 does not join the 8/12/16 residual cluster; its top residual
# partner is CESD19 at 0.05). It pins a polarity class and the 8/12/16 block only, so the
# status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "adamczyk_2022_cesd"
SAV   <- "https://osf.io/download/frg9k/?view_only=53083d2e2869472490beece1b35b7294"

d <- as.data.frame(irw::irw_fetch(TABLE))
items <- paste0("CESD", 1:20)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", items)]
cat("live respondents:", nrow(w), "\n\n")

ok <- TRUE

# ---- A. storage direction ---------------------------------------------------
X <- as.matrix(w[, items])
rs <- sapply(items, function(i) cor(X[, i], rowSums(X[, setdiff(items, i)]),
                                    use = "pairwise.complete.obs"))
cat("A. item-rest correlations (a raw positive CES-D item would be negative):\n")
print(round(rs, 2))
cat(sprintf("   positive items 4/8/12/16: %s\n",
            paste(round(rs[c("CESD4", "CESD8", "CESD12", "CESD16")], 2), collapse = " / ")))
A <- all(rs > 0)
cat("   all 20 positive:", A, "\n\n")
ok <- ok && A

# ---- B. depositors' score = mean of stored items ---------------------------
tf <- tempfile(fileext = ".sav")
dl <- try(download.file(SAV, tf, mode = "wb", quiet = TRUE), silent = TRUE)
if (inherits(dl, "try-error")) {
  cat("B. could not download the OSF .sav -- check B not run\n")
  ok <- FALSE
} else {
  s <- haven::read_sav(tf)
  s$id <- paste0("val2_", seq_len(nrow(s)))
  m <- merge(w, data.frame(id = s$id, Depression = as.numeric(s$Depression)), by = "id")
  live_mean <- rowMeans(as.matrix(m[, items]))
  rev <- as.matrix(m[, items])
  rev[, c("CESD4", "CESD8", "CESD12", "CESD16")] <- 3 - rev[, c("CESD4", "CESD8", "CESD12", "CESD16")]
  hit_asis <- sum(abs(live_mean - m$Depression) < 1e-6)
  hit_rev  <- sum(abs(rowMeans(rev) - m$Depression) < 1e-6)
  cat(sprintf("B. .sav 'Depression' vs mean of live items: as stored %d/%d match; with 4/8/12/16 re-reversed %d/%d\n",
              hit_asis, nrow(m), hit_rev, nrow(m)))
  cat(sprintf("   Depression mean %.4f, live item-mean mean %.4f\n\n",
              mean(m$Depression), mean(live_mean)))
  B <- hit_asis == nrow(m) && nrow(m) == nrow(w)
  ok <- ok && B
}

# ---- C. positive-affect residual cluster ----------------------------------
R <- cor(X, use = "pairwise.complete.obs")
e <- eigen(R)
l <- e$vectors[, 1] * sqrt(e$values[1])
Res <- R - outer(l, l); diag(Res) <- NA
dimnames(Res) <- list(items, items)
cat("C. top-2 residual partners after removing the first principal component:\n")
C <- TRUE
for (i in c("CESD4", "CESD8", "CESD12", "CESD16")) {
  o <- sort(Res[i, ], decreasing = TRUE)[1:3]
  cat(sprintf("   %-7s %s\n", i, paste(sprintf("%s=%.2f", names(o), o), collapse = "  ")))
}
for (i in c("CESD8", "CESD12", "CESD16")) {
  top2 <- names(sort(Res[i, ], decreasing = TRUE)[1:2])
  C <- C && setequal(top2, setdiff(c("CESD8", "CESD12", "CESD16"), i))
}
cat("   8/12/16 are mutually each other's top-2 residual partners:", C, "\n\n")
ok <- ok && C

cat("Does NOT establish: order among the 16 negative items, or CESD4's position\n",
    "(it joins no residual cluster). Pins polarity class + the 8/12/16 block -> PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_pierro_2018_assessment_s3.R
#
# CLAIM UNDER TEST (mapping_basis = reconstructed):
#   The 12 live item codes assr1, ass2, ass3, ass4, assr5, ass6, ass7, ass8,
#   ass9, ass10, assr11, ass12 are the Assessment subscale of the Regulatory
#   Mode Questionnaire (Kruglanski et al., 2000) in canonical subscale order,
#   i.e. subscale positions 1..12 correspond to RMQ 30-item positions
#   2(R), 6, 7, 9, 10(R), 11, 15, 19, 20, 22, 27(R), 30.
#
#   The falsifiable prediction that anchors the order is the placement of the
#   reverse-keyed items: the RMQ Assessment scale has exactly three reversed
#   items (30-item nos. 2, 10, 27), which fall at subscale positions 1, 5, 11 --
#   exactly the three codes the deposit marks with "r". If the data are stored
#   raw, those three and only those three must show non-positive item-rest
#   correlations.
#
#   Supporting numbers: (a) Cronbach's alpha after reversing those three must
#   reproduce the .71 the source paper reports for the Study 3 Assessment scale;
#   (b) the per-item reliability profile should track the Swedish RMQ validation's
#   published per-item standardized loadings (Garcia et al., 2017, PeerJ 5:e3986,
#   Table 3), which are keyed to the same 30-item numbering.
#
#   WHAT THIS DOES NOT ESTABLISH: routes (1) and (a) pin the reverse triple as a
#   CLASS and the item set, not the order within the 9 non-reverse codes, nor the
#   order within the reverse triple. Route (b) is cross-language and cross-sample
#   and is corroborative only.

suppressMessages(library(irw))

TABLE <- "pierro_2018_assessment_s3"
ITEMS <- c("assr1","ass2","ass3","ass4","assr5","ass6","ass7","ass8",
           "ass9","ass10","assr11","ass12")
REV   <- c("assr1","assr5","assr11")

# Garcia et al. (2017) PeerJ 5:e3986 Table 3, standardized loadings (N = 650),
# in canonical Assessment subscale order (their items 2R,6,7,9,10R,11,15,19,20,22,27R,30).
SWED  <- c(.26, .46, .53, .55, .07, .63, .49, .66, .64, .48, .42, .44)

# Pierro et al. (2018) PLoS ONE 13(3):e0193357, Study 3: "the Cronbach's alpha
# for the assessment scale was .71".
PUB_ALPHA <- 0.71

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- stats::reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
                    direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[stats::complete.cases(w[, ITEMS]), ITEMS, drop = FALSE]
cat(sprintf("complete cases: %d respondents x %d items\n\n", nrow(w), ncol(w)))

itemrest <- function(m) {
  tot <- rowSums(m)
  sapply(colnames(m), function(i) stats::cor(m[[i]], tot - m[[i]]))
}

raw <- itemrest(w)
cat("ROUTE 1 -- keying polarity on RAW stored responses\n")
cat(sprintf("%-8s %-8s %12s\n", "item", "keyed", "item-rest r"))
for (i in ITEMS)
  cat(sprintf("%-8s %-8s %12.3f\n", i, if (i %in% REV) "REVERSE" else "positive", raw[[i]]))
worst_rev <- max(raw[REV])
best_pos  <- min(raw[setdiff(ITEMS, REV)])
cat(sprintf("\nhighest reverse-keyed r = %.3f (%s); lowest positive-keyed r = %.3f (%s)\n",
            worst_rev, names(which.max(raw[REV])),
            best_pos,  names(which.min(raw[setdiff(ITEMS, REV)]))))
ok_polarity <- worst_rev < best_pos
cat(sprintf("separation clean: %s\n\n", ok_polarity))

r <- w
for (i in REV) r[[i]] <- 7 - r[[i]]
k <- ncol(r)
alpha <- k/(k-1) * (1 - sum(sapply(r, stats::var)) / stats::var(rowSums(r)))
cat(sprintf("ROUTE (a) -- Cronbach's alpha after reversing %s\n", paste(REV, collapse=", ")))
cat(sprintf("  raw (unreversed) alpha = %.3f\n", {
  kk <- ncol(w); kk/(kk-1) * (1 - sum(sapply(w, stats::var)) / stats::var(rowSums(w))) }))
cat(sprintf("  reversed alpha         = %.3f   published (paper, Study 3) = %.2f\n", alpha, PUB_ALPHA))
ok_alpha <- abs(alpha - PUB_ALPHA) <= 0.01
cat(sprintf("  match within 0.01: %s\n\n", ok_alpha))

ir2 <- itemrest(r)
rho <- suppressWarnings(stats::cor(as.numeric(ir2[ITEMS]), SWED, method = "spearman"))
cat("ROUTE (b) -- item profile vs Swedish RMQ validation loadings (corroborative)\n")
cat(sprintf("%-8s %14s %10s\n", "item", "IT item-rest r", "SE loading"))
for (j in seq_along(ITEMS))
  cat(sprintf("%-8s %14.3f %10.2f\n", ITEMS[j], ir2[[ITEMS[j]]], SWED[j]))
cat(sprintf("\nSpearman rho = %.3f\n", rho))
set.seed(1)
nr <- setdiff(seq_along(ITEMS), match(REV, ITEMS))
perm <- replicate(5000, {
  s <- SWED; s[nr] <- sample(s[nr])
  suppressWarnings(stats::cor(as.numeric(ir2[ITEMS]), s, method = "spearman"))
})
cat(sprintf("permutation of the 9 non-reverse assignments: %.3f of 5000 draws reach rho >= observed\n",
            mean(perm >= rho)))
cat("  -> suggestive, NOT decisive; the 9 non-reverse positions rest on canonical order.\n\n")

cat("VERDICT: ", if (ok_polarity && ok_alpha) "PASS" else "FAIL", "\n", sep = "")

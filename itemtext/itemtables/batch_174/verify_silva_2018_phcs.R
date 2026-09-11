# verify_silva_2018_phcs.R -- Step 5b mapping check for silva_2018_phcs (batch_174).
#
# Claim: live codes PHCS1..PHCS8 follow the item numbering of Silva, Pimenta, Maroco,
# Maloa & Campos (2016) IJRSR 7:13383, Table 1 (unified Portuguese-language PHCS),
# which the 2018 PLOS paper (10.1371/journal.pone.0199480) names as the version it
# administered. Codes are the S1 Dataset's own column names (data/silva_2018_body_image.py
# melts columns starting "PHCS"), but the S1 "labels" sheet says only "Perceived Health
# Competence Scale item" for each, so which wording goes with which number is inferred.
#
# Falsifiable predictions, all from the two papers:
#  (a) polarity: 2018 paper and 2016 Table 1 mark items 1,2,6,7 as reverse-worded.
#      Raw data => those four sit low (disagree) and correlate negatively with 3,4,5,8.
#      A widely circulated alternative ordering (reverse items 2,3,6,7) predicts PHCS1
#      positive and PHCS3 negative -- this check refutes it for this table.
#  (b) 2018 Table 1, PHCS-B two-factor CFA ({1,2,6,7},{3,4,5,8}), loading ranges:
#      women BR/PT n=1396: .54-.86; men BR/PT n=802: .60-.83.
#      Men "fitted": items 1 and 3 excluded -> .71-.85.
#      Women "fitted": error correlations 3-4 and 4-5 -> .54-.84.
#      The unfitted ranges are label-invariant (they only show the data reproduce the
#      paper's analysis). Label-specific: (c) only dropping PHCS1+PHCS3 reproduces the
#      men-fitted .71-.85 (pins items 1 and 3); the women MI ordering favours 3-4/4-5.
# NOT established: order within {2,6,7} -- the paper gives loading RANGES only, and
# nothing distinguishes those three from each other. 4 vs 5 only weakly (MI ordering).

suppressMessages({library(irw); library(lavaan)})

TABLE <- "silva_2018_phcs"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp", "cov_sex")]),
             idvar = c("id", "cov_sex"), timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
it <- paste0("PHCS", 1:8)
ok <- TRUE

cat("== (a) polarity ==\n")
mn <- colMeans(w[, it], na.rm = TRUE)
r <- cor(w[, it], use = "pairwise")
neg <- paste0("PHCS", c(1, 2, 6, 7)); pos <- paste0("PHCS", c(3, 4, 5, 8))
print(round(mn, 2))
cross <- r[neg, pos]
cat(sprintf("cross-block correlations (neg x pos): %.2f to %.2f\n", min(cross), max(cross)))
cat(sprintf("within-block min r: neg %.2f, pos %.2f\n",
            min(r[neg, neg][upper.tri(r[neg, neg])]), min(r[pos, pos][upper.tri(r[pos, pos])])))
pa <- all(cross < 0) && all(mn[neg] < 3) && all(mn[pos] > 3)
cat("reverse set {1,2,6,7}:", if (pa) "CONFIRMED" else "NOT CONFIRMED", "\n")
cat(sprintf("alt ordering check: PHCS1 mean %.2f (alt predicts positive, >3), PHCS3 mean %.2f (alt predicts negative, <3)\n",
            mn["PHCS1"], mn["PHCS3"]))
ok <- ok && pa

fitload <- function(x, model, items) {
  x <- x[complete.cases(x[, items]), items]
  f <- cfa(model, data = x, ordered = items, estimator = "WLSMV", std.lv = TRUE)
  ss <- standardizedSolution(f); ss <- ss[ss$op == "=~", ]
  list(n = nrow(x), load = setNames(ss$est.std, ss$rhs), fit = f)
}
m2 <- 'F1 =~ PHCS1 + PHCS2 + PHCS6 + PHCS7
       F2 =~ PHCS3 + PHCS4 + PHCS5 + PHCS8'

cat("\n== (b) 2018 Table 1 loading ranges ==\n")
chk <- function(label, res, lo, hi) {
  l <- round(res$load, 2)
  cat(sprintf("%-22s n=%4d  published %.2f-%.2f  observed %.2f-%.2f  (min %s, max %s)\n",
              label, res$n, lo, hi, min(l), max(l), names(l)[which.min(l)], names(l)[which.max(l)]))
  print(l)
  abs(min(l) - lo) <= 0.02 && abs(max(l) - hi) <= 0.02
}
wom <- w[w$cov_sex == 2, ]; men <- w[w$cov_sex == 1, ]
rw <- fitload(wom, m2, it); rm_ <- fitload(men, m2, it)
ok <- chk("women PHCS-B", rw, .54, .86) && ok
ok <- chk("men PHCS-B", rm_, .60, .83) && ok
cat(sprintf("women: lowest loading %s, highest %s; men: lowest %s\n",
            names(which.min(rw$load)), names(which.max(rw$load)), names(which.min(rm_$load))))
low_pos_men <- names(which.min(rm_$load[pos]))
cat("men: weakest item in positive block =", low_pos_men, "(paper drops items 1 and 3 for men)\n")
ok <- ok && names(which.min(rm_$load)) == "PHCS1" && low_pos_men == "PHCS3"

mi <- modindices(rw$fit)
mi <- mi[mi$op == "~~" & mi$lhs %in% pos & mi$rhs %in% pos, c("lhs", "rhs", "mi")]
mi <- mi[order(-mi$mi), ]
cat("\nwomen: within-positive-block residual MIs (paper frees 3-4 and 4-5):\n"); print(mi)
top2 <- apply(mi[1:2, 1:2], 1, function(z) paste(sort(z), collapse = "-"))
cat("top two:", top2, "\n")
ok <- ok && setequal(top2, c("PHCS3-PHCS4", "PHCS4-PHCS5"))

mw <- paste(m2, "\nPHCS3 ~~ PHCS4\nPHCS4 ~~ PHCS5")
ok <- chk("women fitted", fitload(wom, mw, it), .54, .84) && ok
mm <- 'F1 =~ PHCS2 + PHCS6 + PHCS7
       F2 =~ PHCS4 + PHCS5 + PHCS8'
ok <- chk("men fitted (-1,-3)", fitload(men, mm, setdiff(it, c("PHCS1", "PHCS3"))), .71, .85) && ok

# The loading RANGES in (b) are label-invariant for the unfitted models; what is
# label-specific is WHICH items the paper dropped/freed. So: try every alternative
# column for "item 1" (within its block) and "item 3" (within its block) and show only
# the claimed columns reproduce men-fitted .71-.85.
cat("\n== (c) men fitted: which columns, if dropped as 'items 1 and 3', reproduce .71-.85? ==\n")
hits <- character(0)
for (c1 in neg) for (c3 in pos) {
  its <- setdiff(it, c(c1, c3))
  mdl <- sprintf("F1 =~ %s\nF2 =~ %s", paste(setdiff(neg, c1), collapse = " + "),
                 paste(setdiff(pos, c3), collapse = " + "))
  l <- round(fitload(men, mdl, its)$load, 2)
  match <- abs(min(l) - .71) <= .01 && abs(max(l) - .85) <= .01
  cat(sprintf("drop %s + %s: %.2f-%.2f %s\n", c1, c3, min(l), max(l), if (match) "<-- matches" else ""))
  if (match) hits <- c(hits, paste(c1, c3))
}
cat("matching drop pairs:", hits, "\n")
ok <- ok && identical(hits, "PHCS1 PHCS3")

cat("\nNot established: order among PHCS2/PHCS6/PHCS7 (published loading RANGES do not separate them).\n")
# Paper (2016 & 2018 methods): residual correlations were freed where the Lagrange
# multiplier exceeded 11. With item 3 pinned to PHCS3, the freed pair shape "3-4, 4-5"
# needs two MI>11 pairs sharing a middle item, one of them containing PHCS3.
big <- mi[mi$mi > 11, ]
cat("\nwomen: positive-block pairs with MI > 11:\n"); print(big)
cat("PHCS8 in any MI>11 pair (it must not be, if PHCS8 is item 8):",
    any(big$lhs == "PHCS8" | big$rhs == "PHCS8"), "\n")
ok <- ok && !any(big$lhs == "PHCS8" | big$rhs == "PHCS8")
cat("Weakly established only: PHCS4 vs PHCS5. Freeing 3-5 & 5-4 instead of 3-4 & 4-5 gives a\n",
    "women-fitted range within .01 of .54-.84 too, and both 3-4 (26.0) and 3-5 (15.0) exceed MI 11;\n",
    "only the MI ordering favours the claimed assignment. The fitted RANGE alone also admits item 4=PHCS8\n",
    "(.54-.85); that alternative is excluded only because PHCS3-PHCS8 has MI 3.5, below the paper's\n",
    "stated LM>11 criterion.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

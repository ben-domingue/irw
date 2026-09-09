# verify_lorenz_2016_hope.R
#
# Claim under test: hopeK in the IRW table is item K of Snyder et al.'s (1996)
# 6-item State Hope Scale, in the instrument's own published numbering
#   1 pathways / 2 agency / 3 pathways / 4 agency / 5 pathways / 6 agency.
#
# data/lorenz_2016_psycap.py is a pure melt of the PLOS S1 Dataset preserving the
# deposit's column names (hope1..hope6), so the mapping question is entirely
# about which SHS item each deposit column is. The deposit is therefore the object
# checked here; the live table is touched only via irw_table_sets() (server-side,
# spends no export quota).
#
# Three checks:
#   (A) instrument identity        -- Lorenz et al. (2016) Table 1
#   (B) the agency/pathways split  -- SHS's published 2-factor structure, all 10 splits
#   (C) which columns are SHS1/SHS4/SHS5, and in what order
#                                  -- Lorenz et al. Table 2 (CFA fit) + Fig 1 (loadings)
#
# NOT ESTABLISHED: hope2 vs hope6. Both are agency items and neither entered the
# CPC-12, so no published number in this paper distinguishes them; swapping them
# leaves every figure below unchanged. Hence PARTIAL, not VERIFIED.

suppressMessages({library(lavaan); library(irw)})

TABLE <- "lorenz_2016_hope"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0152892.s002")

d <- read.csv(SI, sep = ";")
hv <- paste0("hope", 1:6)
alpha <- function(x) { k <- ncol(x); k/(k-1) * (1 - sum(apply(x,2,var))/var(rowSums(x))) }
ok <- TRUE

## ---- sanity: deposit columns are the live item codes -------------------------
sets <- try(irw::irw_table_sets(TABLE), silent = TRUE)
if (!inherits(sets, "try-error"))
  cat("live item codes == deposit hope columns: ",
      identical(sort(as.character(sets$items)), sort(hv)), "\n\n", sep = "")

## ---- (A) instrument identity -------------------------------------------------
cat("(A) Lorenz et al. (2016) Table 1, 'Hope' row\n")
mH <- mean(rowMeans(d[hv])); aH <- alpha(d[hv])
cat(sprintf("    %-10s pub %6.2f   obs %7.4f\n", "M",     4.25, mH))
cat(sprintf("    %-10s pub %6.2f   obs %7.4f\n", "alpha",  .84, aH))
okA <- abs(mH - 4.25) < .005 && abs(aH - .84) < .005
cat("    -> the six hope columns are the paper's Hope scale: ", okA, "\n\n", sep = "")
ok <- ok && okA

## ---- (B) agency / pathways --------------------------------------------------
# Snyder et al. (1996): pathways = items 1, 3, 5; agency = items 2, 4, 6.
# Test every 3-3 split of the six columns; only the canonical one should fit.
cat("(B) two-factor structure -- all 10 possible 3-3 splits, ranked\n")
h <- d[hv]; names(h) <- paste0("h", 1:6); C <- cor(h)
sp <- Filter(function(p) 1 %in% p, combn(6, 3, simplify = FALSE))
res <- do.call(rbind, lapply(sp, function(p) {
  q <- setdiff(1:6, p)
  m <- paste0("F1 =~ ", paste0("h", p, collapse = " + "),
              "\nF2 =~ ", paste0("h", q, collapse = " + "))
  f <- try(cfa(m, data = h, estimator = "MLM"), silent = TRUE)
  fm <- if (inherits(f, "try-error")) c(NA, NA, NA) else
        unname(fitMeasures(f, c("chisq.scaled", "cfi.scaled", "rmsea.scaled")))
  wi <- mean(c(C[p,p][upper.tri(diag(3))], C[q,q][upper.tri(diag(3))]))
  data.frame(split = paste0(paste(p, collapse = ""), "|", paste(q, collapse = "")),
             chisq = fm[1], cfi = fm[2], rmsea = fm[3],
             gap = wi - mean(C[p, q]))
}))
res <- res[order(-res$gap), ]
print(res, digits = 4, row.names = FALSE)
best <- res$split[1]
okB <- identical(best, "135|246")
cat("    best split: ", best, "  (canonical SHS pathways 1,3,5 / agency 2,4,6: ", okB, ")\n",
    "    next-best gap ", sprintf("%.4f", res$gap[2]), " vs ", sprintf("%.4f", res$gap[1]),
    "; next-best CFI ", sprintf("%.3f", res$cfi[2]), " vs ", sprintf("%.3f", res$cfi[1]), "\n\n", sep = "")
ok <- ok && okB

## ---- (C) SHS1 / SHS4 / SHS5, individually -----------------------------------
# S1 Appendix: CPC-12 items 1-3 are SHS1, SHS4, SHS5. Table 2 publishes the
# CPC-12 4+g CFA (chisq 77.727 / df 50 / TLI .950 / CFI .962 / RMSEA .042) and
# Fig 1 the standardized loadings, boxes in the order SHS1 .60, SHS4 .67, SHS5 .81.
FIXED <- c("optimism1.1","optimism1.5","optimism2.10",
           "resilience10","resilience11","resilience13",
           "efficacy1.4","efficacy1.6","efficacy1.10")
MOD <- 'H =~ h1 + h2 + h3
O =~ o1 + o2 + o3
R =~ r1 + r2 + r3
E =~ e1 + e2 + e3
G =~ H + O + R + E'
fitTriple <- function(tri) {
  dd <- d[, c(paste0("hope", tri), FIXED)]
  names(dd) <- c("h1","h2","h3","o1","o2","o3","r1","r2","r3","e1","e2","e3")
  f <- try(cfa(MOD, data = dd, estimator = "MLM"), silent = TRUE)
  if (inherits(f, "try-error")) return(NULL)
  f
}
cat("(C1) which three hope columns are the CPC-12's SHS1/SHS4/SHS5\n")
cat("     published: chisq 77.727  df 50  TLI .950  CFI .962  RMSEA .042\n")
tab <- do.call(rbind, lapply(combn(6, 3, simplify = FALSE), function(tri) {
  f <- fitTriple(tri); if (is.null(f)) return(NULL)
  fm <- unname(fitMeasures(f, c("chisq.scaled","tli.scaled","cfi.scaled","rmsea.scaled")))
  data.frame(triple = paste(tri, collapse = ","), chisq = fm[1], tli = fm[2],
             cfi = fm[3], rmsea = fm[4], d = abs(fm[1] - 77.727))
}))
tab <- tab[order(tab$d), ]
print(head(tab, 5), digits = 6, row.names = FALSE)
okC1 <- identical(tab$triple[1], "1,4,5") && tab$d[1] < .005 &&
        abs(tab$tli[1] - .950) < .0005 && abs(tab$cfi[1] - .962) < .0005
cat("     -> {hope1, hope4, hope5} = {SHS1, SHS4, SHS5} as a set: ", okC1, "\n\n", sep = "")

cat("(C2) Fig 1 standardized loadings pin the ORDER within that triple\n")
f <- fitTriple(c(1, 4, 5))
s <- standardizedSolution(f); s <- s[s$op == "=~" & s$lhs == "H", ]
r <- standardizedSolution(f); r <- r[r$op == "~~" & r$lhs == r$rhs & r$lhs %in% c("h1","h2","h3"), ]
PUB_L <- c(0.60, 0.67, 0.81); PUB_R <- c(0.64, 0.56, 0.34)
nm <- c("hope1 -> SHS1", "hope4 -> SHS4", "hope5 -> SHS5")
cat(sprintf("     %-16s %9s %9s %9s %9s\n", "", "pub load", "obs load", "pub resid", "obs resid"))
for (i in 1:3)
  cat(sprintf("     %-16s %9.2f %9.3f %9.2f %9.3f\n",
              nm[i], PUB_L[i], s$est.std[i], PUB_R[i], r$est.std[i]))
okC2 <- max(abs(round(s$est.std, 2) - PUB_L)) < .0051 &&
        max(abs(round(r$est.std, 2) - PUB_R)) < .0051
cat("     loadings differ by .60 vs .81, so a hope1<->hope5 swap would read .81/.67/.60\n")
cat("     against Fig 1's .60/.67/.81 -- the two pathways items are separated: ", okC2, "\n\n", sep = "")
ok <- ok && okC1 && okC2

cat("Established individually: hope1=SHS1, hope4=SHS4, hope5=SHS5 (C1+C2);\n")
cat("hope3=SHS3 by elimination (B puts it in pathways {1,3,5}, C1 excludes it from the CPC-12 pair).\n")
cat("NOT established: hope2 vs hope6 -- both agency, neither in the CPC-12; interchanging\n")
cat("them leaves (A), (B) and (C) numerically identical. That is why the status is PARTIAL.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_lorenz_2016_optimism2.R
#
# Claim under test: optimism2.k in the IRW table is item k of the German LOT-R
# (Glaesmer, Hoyer, Klotsche & Herzberg 2008), in the canonical Scheier/Carver
# item numbering -- so items 2, 5, 6, 8 are the fillers, 1, 4, 10 the optimism
# items and 3, 7, 9 the pessimism items -- AND that the three pessimism items
# are stored ALREADY REVERSE-CODED, which is why option_text runs the other way
# for those three.
#
# data/lorenz_2016_psycap.py is a pure melt of the PLOS S1 Dataset preserving
# the source column NAMES, so the mapping question is entirely about which
# LOT-R item each deposit column is. The deposit is therefore the object
# checked; the live table is touched only via irw_table_sets(), which is
# server-side and spends no export quota.
#
# Five checks: (A) instrument identity, (B) which six columns are scored,
# (C) the optimism/pessimism partition, (D) which column is LOT-R item 10,
# (E) the stored polarity of items 3, 7, 9.

suppressMessages({library(lavaan); library(irw)})

TABLE <- "lorenz_2016_optimism2"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0152892.s002")

d <- read.csv(SI, sep = ";")
o1 <- paste0("optimism1.", 1:5)
o2 <- paste0("optimism2.", 1:10)

alpha <- function(x) { k <- ncol(x); k/(k-1) * (1 - sum(apply(x,2,var))/var(rowSums(x))) }
ok <- TRUE

## ---- sanity: deposit columns are the live item codes -------------------------
sets <- try(irw::irw_table_sets(TABLE), silent = TRUE)
if (!inherits(sets, "try-error"))
  cat("live item codes == deposit optimism2 columns: ",
      identical(sort(as.character(sets$items)), sort(o2)), "\n\n", sep = "")

## ---- (A) instrument identity -------------------------------------------------
# Lorenz et al. (2016) Table 1 reports TWO optimism scales: AFF (M 4.83, alpha .82)
# and LOT-R (M 4.41, alpha .74). The LOT-R total is by definition the six
# non-filler items; the AFF is all five of its own.
cat("(A) Lorenz et al. (2016) Table 1, the two optimism scales\n")
cat(sprintf("%-34s %8s %8s %10s %10s\n", "", "pub M", "obs M", "pub alpha", "obs alpha"))
aA <- mean(rowMeans(d[o1])); cA <- alpha(d[o1])
sc <- c(1,3,4,7,9,10)
aL <- mean(rowMeans(d[o2[sc]])); cL <- alpha(d[o2[sc]])
cat(sprintf("%-34s %8.2f %8.3f %10.2f %10.3f\n", "Optimism (AFF)  = optimism1.1-.5",  4.83, aA, .82, cA))
cat(sprintf("%-34s %8.2f %8.3f %10.2f %10.3f\n", "Optimism (LOT-R) = optimism2 1,3,4,7,9,10", 4.41, aL, .74, cL))
okA <- abs(aL - 4.41) < .01 && abs(cL - .74) < .01
cat("  -> optimism2 (10 cols) is the LOT-R, optimism1 (5 cols) the AFF: ", okA, "\n\n", sep = "")
ok <- ok && okA

## ---- (B) which six of the ten columns are the scored items -------------------
# Glaesmer et al. (2008) Anhang: "Die Items 2, 5, 6 und 8 sind Fuellitems und
# werden nicht ausgewertet." So the published LOT-R M/alpha is a prediction about
# ONE of the 210 possible six-column subsets.
cb <- combn(10, 6)
tb <- data.frame(set = apply(cb, 2, paste, collapse = ","),
                 M = apply(cb, 2, function(s) mean(rowMeans(d[o2[s]]))),
                 a = apply(cb, 2, function(s) alpha(d[o2[s]])))
tb$dev <- abs(tb$M - 4.41) + abs(tb$a - 0.74)
tb <- tb[order(tb$dev), ]
cat("(B) all 210 six-column subsets, ranked by |M-4.41| + |alpha-.74|\n")
cat(sprintf("%-22s %8s %8s %8s\n", "columns", "M", "alpha", "dev"))
for (i in 1:5) cat(sprintf("%-22s %8.3f %8.3f %8.4f\n", tb$set[i], tb$M[i], tb$a[i], tb$dev[i]))
okB <- tb$set[1] == "1,3,4,7,9,10" && tb$dev[2] > 5 * tb$dev[1]
cat("  -> best subset = ", tb$set[1], ", ", sprintf("%.1f", tb$dev[2]/tb$dev[1]),
    "x better than the runner-up: ", okB, "\n\n", sep = "")
ok <- ok && okB

## ---- (C) the optimism / pessimism partition of those six ---------------------
# Glaesmer et al.: optimism = 1, 4, 10; pessimism = 3, 7, 9. With the pessimism
# items stored reverse-coded (see E) all six correlate positively, so the split
# shows up as block cohesion rather than as a sign flip.
cm <- cor(d[o2[sc]])
pp <- combn(6, 3); seen <- character(0); rows <- data.frame()
for (j in 1:ncol(pp)) {
  a <- pp[, j]; b <- setdiff(1:6, a)
  key <- paste(sort(c(paste(a, collapse = ""), paste(b, collapse = ""))), collapse = "|")
  if (key %in% seen) next
  seen <- c(seen, key)
  w <- mean(c(cm[a,a][upper.tri(diag(3))], cm[b,b][upper.tri(diag(3))]))
  x <- mean(cm[a, b])
  rows <- rbind(rows, data.frame(part = paste0("{", paste(sc[a], collapse=","), "} / {",
                                               paste(sc[b], collapse=","), "}"),
                                 within = w, cross = x, gap = w - x))
}
rows <- rows[order(-rows$gap), ]
cat("(C) all 10 ways to split the six scored items into two triples\n")
cat(sprintf("%-26s %9s %9s %9s\n", "partition", "within r", "cross r", "gap"))
for (i in 1:4) cat(sprintf("%-26s %9.3f %9.3f %9.3f\n", rows$part[i], rows$within[i], rows$cross[i], rows$gap[i]))
okC <- rows$part[1] == "{1,4,10} / {3,7,9}"
cat("  -> best partition = ", rows$part[1], " (gap ", sprintf("%.3f", rows$gap[1]),
    " vs ", sprintf("%.3f", rows$gap[2]), " for the next): ", okC, "\n\n", sep = "")
ok <- ok && okC

## ---- (D) which column is LOT-R item 10 --------------------------------------
# S1 Appendix: CPC-12 item 6 is "LOT-R10", printed as "Alles in allem erwarte ich,
# dass mir mehr gute als schlechte Dinge widerfahren." -- verbatim item 10 of the
# Glaesmer et al. Anhang. Table 2 publishes the CPC-12 4+g CFA (chisq 77.727,
# df 50, TLI .950, CFI .962, RMSEA .042); only the right column reproduces it.
base <- c("hope1","hope4","hope5","optimism1.1","optimism1.5",
          "resilience10","resilience11","resilience13",
          "efficacy1.4","efficacy1.6","efficacy1.10")
mod <- 'H =~ h1 + h2 + h3
        O =~ o1 + o2 + o3
        R =~ r1 + r2 + r3
        E =~ e1 + e2 + e3
        G =~ H + O + R + E'
cat("(D) Lorenz et al. Table 2 CPC-12 CFA, one fit per candidate for LOT-R item 10\n")
cat(sprintf("%-14s %9s %8s %8s %8s\n", "optimism2 col", "chisq", "TLI", "CFI", "RMSEA"))
fits <- data.frame()
for (k in 1:10) {
  dd <- d[, c(base[1:5], paste0("optimism2.", k), base[6:11])]
  names(dd) <- c("h1","h2","h3","o1","o2","o3","r1","r2","r3","e1","e2","e3")
  fm <- fitMeasures(cfa(mod, data = dd, estimator = "MLM"),
                    c("chisq.scaled","tli.scaled","cfi.scaled","rmsea.scaled"))
  fits <- rbind(fits, data.frame(k = k, chi = unname(fm[1]), tli = unname(fm[2]),
                                 cfi = unname(fm[3]), rmsea = unname(fm[4])))
}
fits <- fits[order(fits$chi), ]
for (i in 1:4) cat(sprintf("%-14s %9.3f %8.3f %8.3f %8.3f",
                           paste0("optimism2.", fits$k[i]), fits$chi[i], fits$tli[i],
                           fits$cfi[i], fits$rmsea[i]), if (i == 1) "  <- best\n" else "\n")
okD <- fits$k[1] == 10 && abs(fits$chi[1] - 77.727) < 0.05
cat("  -> best column = optimism2.", fits$k[1], "; published chisq 77.727 reproduced: ",
    okD, "\n\n", sep = "")
ok <- ok && okD

## ---- (E) stored polarity of the pessimism items ------------------------------
# Glaesmer et al.: "Die Items 3, 7 und 9 muessen zur Berechnung des Gesamtscores
# umkodiert werden." If the deposit stored them RAW, the published total-scale
# alpha of .74 would be unreachable without recoding first.
rr <- function(x) 7 - x
asis <- alpha(d[o2[sc]])
flip <- alpha(cbind(d[o2[c(1,4,10)]], rr(d[o2[c(3,7,9)]])))
cat("(E) is the deposit storing items 3/7/9 raw or already reverse-coded?\n")
cat(sprintf("  alpha of the 6 scored columns AS STORED            : %8.3f\n", asis))
cat(sprintf("  alpha after recoding 3/7/9 (7-x) as the manual says: %8.3f\n", flip))
cat(sprintf("  published (Table 1)                                : %8.2f\n", 0.74))
cat(sprintf("  mean r(pessimism col, optimism col) as stored      : %8.3f\n",
            mean(cor(d[o2[c(3,7,9)]], d[o2[c(1,4,10)]]))))
okE <- abs(asis - .74) < .01 && flip < .2
cat("  -> stored already reverse-coded, so resp 6 on optimism2.3/.7/.9 means the\n",
    "     respondent DISagreed; option_text is inverted for those three: ", okE, "\n\n", sep = "")
ok <- ok && okE

## ---- what none of this establishes ------------------------------------------
cat("NOT established by any route above:\n")
cat(" - optimism2.1 vs optimism2.4. Both are optimism items, both survive (B) and\n")
cat("   (C) identically, and neither Glaesmer et al. (2008) nor Lorenz et al. (2016)\n")
cat("   publishes per-item statistics for the LOT-R, so nothing separates them.\n")
cat(" - the order WITHIN {3,7,9}: any permutation of those three leaves (A)-(E)\n")
cat("   numerically unchanged.\n")
cat(" - the order within the fillers {2,6,8}. optimism2.5 is separated from them by\n")
cat("   its mean (5.10, the highest of the ten, matching the only filler that is a\n")
cat("   straightforwardly endorsable statement about one's friends); 2, 6 and 8 sit\n")
cat("   at 3.61 / 3.71 / 3.90 and are not distinguished from each other.\n")
cat(" - option_text<->resp beyond the direction settled in (E): the German anchors of\n")
cat("   this study's 6-point format are published nowhere, so option_text carries only\n")
cat("   the paper's own English endpoint labels.\n\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

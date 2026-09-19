# verify_lorenz_2016_efficacy1.R
#
# Claim under test: efficacy1.k in the IRW table is item k of the German
# General Self-Efficacy Scale (SWE; Jerusalem & Schwarzer), in the numbering
# used on the authors' own scale page userpage.fu-berlin.de/~health/germscal.htm.
#
# data/lorenz_2016_psycap.py is a pure melt of the PLOS S1 Dataset with the
# source column NAMES preserved (efficacy1.1..efficacy1.10), so the mapping
# question is entirely about which SWE item each deposit column is -- it is not
# about the melt. The deposit is therefore the object checked here; the live
# table is touched only through irw_table_sets(), which is server-side and does
# not spend export quota.
#
# Three independent checks:
#   (A) instrument identity   -- Lorenz et al. Table 1
#   (B) the GSE4/GSE6/GSE10 subset -- Lorenz et al. S1 Appendix + Table 2 CFA
#   (C) the full 1..10 ordering    -- Schwarzer & Jerusalem (1999) item statistics

suppressMessages({library(lavaan); library(irw)})

TABLE <- "lorenz_2016_efficacy1"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0152892.s002")

d <- read.csv(SI, sep = ";")
eff1 <- paste0("efficacy1.", 1:10)
eff2 <- paste0("efficacy2.", 1:8)

alpha <- function(x) { k <- ncol(x); k/(k-1) * (1 - sum(apply(x,2,var))/var(rowSums(x))) }

ok <- TRUE

## ---- sanity: the deposit columns are the live table's item codes -------------
sets <- try(irw::irw_table_sets(TABLE), silent = TRUE)
if (!inherits(sets, "try-error")) {
  live <- sort(as.character(sets$items))
  cat("live item codes == deposit efficacy1 columns: ",
      identical(live, sort(eff1)),
      " | live n_rows ", sets$n_rows, " == 321 respondents x 10 items: ",
      identical(as.integer(sets$n_rows), 3210L), "\n\n", sep = "")
}

## ---- (A) instrument identity -------------------------------------------------
cat("(A) Lorenz et al. (2016) Table 1, scale descriptives\n")
cat(sprintf("%-28s %10s %10s %10s %10s\n", "", "pub M", "obs M", "pub alpha", "obs alpha"))
a1 <- mean(rowMeans(d[eff1])); c1 <- alpha(d[eff1])
a2 <- mean(rowMeans(d[eff2])); c2 <- alpha(d[eff2])
cat(sprintf("%-28s %10.2f %10.3f %10.2f %10.3f\n", "General Self-Efficacy",      4.22, a1, .88, c1))
cat(sprintf("%-28s %10.2f %10.3f %10.2f %10.3f\n", "Occupational Self-Efficacy", 4.29, a2, .85, c2))
okA <- abs(a1 - 4.22) < .005 && abs(c1 - .88) < .005
cat("  -> efficacy1 (10 cols) is the GSE, not the OSE: ", okA, "\n\n", sep = "")
ok <- ok && okA

## ---- (B) which three efficacy1 columns are GSE4, GSE6, GSE10 ------------------
# S1 Appendix: CPC-12 items 10/11/12 are GSE4, GSE10, GSE6.  Table 2 publishes
# the CPC-12 4+g CFA: chisq 77.727 / df 50 / SRMR .046 / TLI .950 / CFI .962 /
# RMSEA .042.  Only the correct triple reproduces it.
base <- c("hope1","hope4","hope5","optimism1.1","optimism1.5","optimism2.10",
          "resilience10","resilience11","resilience13")
mod <- 'H =~ h1 + h2 + h3
        O =~ o1 + o2 + o3
        R =~ r1 + r2 + r3
        E =~ e1 + e2 + e3
        G =~ H + O + R + E'
cands <- list(c(3,4,8), c(3,4,10), c(4,5,6), c(4,6,8), c(4,6,10))
cat("(B) Lorenz et al. Table 2, CPC-12 4+g CFA: published chisq=77.727 df=50 TLI=.950 CFI=.962 RMSEA=.042\n")
cat("    (candidates = every efficacy1 triple whose CPC-12 mean rounds to the published 4.44)\n")
cat(sprintf("%-34s %9s %9s %8s %8s %8s\n", "efficacy1 triple", "CPC-12 M", "chisq", "TLI", "CFI", "RMSEA"))
best <- NULL
for (cc in cands) {
  dd <- d[, c(base, paste0("efficacy1.", cc))]
  names(dd) <- c("h1","h2","h3","o1","o2","o3","r1","r2","r3","e1","e2","e3")
  fm <- fitMeasures(cfa(mod, data = dd, estimator = "MLM"),
                    c("chisq.scaled","tli.scaled","cfi.scaled","rmsea.scaled"))
  cat(sprintf("%-34s %9.4f %9.3f %8.3f %8.3f %8.3f\n",
              paste(cc, collapse = ","), mean(rowMeans(dd)), fm[1], fm[2], fm[3], fm[4]))
  if (is.null(best) || abs(fm[1] - 77.727) < abs(best$chi - 77.727))
    best <- list(cc = cc, chi = unname(fm[1]))
}
okB <- identical(best$cc, c(4,6,10)) && abs(best$chi - 77.727) < 0.01
cat("  -> best-fitting triple = ", paste(best$cc, collapse = ","),
    " (chisq ", sprintf("%.3f", best$chi), "); expected 4,6,10: ", okB, "\n\n", sep = "")
ok <- ok && okB

## ---- (C) the full 1..10 ordering ---------------------------------------------
# Schwarzer & Jerusalem (1999), Skalen zur Erfassung von Lehrer- und
# Schuelermerkmalen, "Allgemeine Selbstwirksamkeitserwartung (WIRKALL_r)",
# Itemkennwerte MZP1 (N = 3078), items 1..10 in the SWE's own numbering.
REF   <- c(3.10, 3.07, 2.93, 2.72, 2.97, 2.72, 3.09, 2.93, 2.91, 2.96)
REFRIT<- c(.41, .41, .42, .40, .35, .50, .47, .53, .46, .49)
obs <- colMeans(d[eff1])
tot <- rowSums(d[eff1])
rit <- sapply(eff1, function(cn) cor(d[[cn]], tot - d[[cn]]))
cat("(C) Schwarzer & Jerusalem (1999) per-item statistics vs this sample\n")
cat(sprintf("%-14s %9s %9s %9s %9s\n", "SWE item", "1999 M", "obs M", "1999 rit", "obs rit"))
for (i in 1:10) cat(sprintf("%-14s %9.2f %9.3f %9.2f %9.3f\n", eff1[i], REF[i], obs[i], REFRIT[i], rit[i]))
r0 <- cor(REF, obs)
set.seed(1)
perm <- replicate(200000, cor(REF[sample(10)], obs))
pct <- mean(perm < r0) * 100
cat(sprintf("\n  identity mapping r = %.4f (Spearman %.4f); %.3f%% of 200,000 random permutations do worse\n",
            r0, cor(REF, obs, method = "spearman"), pct))
okC <- r0 > 0.80 && pct > 99
cat("  -> ordering corroborated: ", okC, "\n\n", sep = "")
ok <- ok && okC

## ---- what this does NOT establish --------------------------------------------
cat("NOT established by any route above:\n")
cat(" - (C) does not separate items whose 1999 means tie or nearly tie. Swapping\n")
cat("   3<->8 changes r by 0.0000, 5<->10 by 0.0008, 1<->2 by -0.0221 (i.e. the swap\n")
cat("   fits marginally BETTER), so the profile corroborates the ordering as a whole\n")
cat("   rather than pinning every item against every other.\n")
cat(" - (B) fixes {4,6,10} as a SET. Within it, item 10 is separated from 4 and 6 by\n")
cat("   the 1999 means (2.96 vs 2.72/2.72) and 4 from 6 only by the weaker rit\n")
cat("   contrast (1999 .40 vs .50; observed ", sprintf("%.3f vs %.3f", rit[4], rit[6]), ").\n", sep="")
cat(" - Nothing here checks option_text<->resp: the German anchors of the study's\n")
cat("   6-point format are published nowhere, so option_text carries the paper's own\n")
cat("   English endpoint labels only.\n\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

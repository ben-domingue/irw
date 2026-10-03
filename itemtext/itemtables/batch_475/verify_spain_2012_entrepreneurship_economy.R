# verify_spain_2012_entrepreneurship_economy.R -- Step 5b, mapping_basis=paper_explicit.
# Claim: IRW item p4 is CIS questionnaire P.4 ("... actual ... que hace un año", retrospective)
# and p5 is P.5 ("... dentro de un año ...", prospective); resp 1/2/3 = Mejor/Igual/Peor.
# Falsifiable prediction: per-item x per-level counts in the live table equal the CIS published
# marginals for PREGUNTA 4 and PREGUNTA 5 (Es2938pdf.pdf, N=1437; N.S./N.C. dropped by the .do).
# A p4<->p5 swap, or any permutation of the 1/2/3 levels, breaks every cell.
suppressMessages(library(irw))
TABLE <- "spain_2012_entrepreneurship_economy"
PUBLISHED <- rbind(
  p4 = c(Mejor = 42,  Igual = 506, Peor = 854),   # PREGUNTA 4, retrospective (N.S. 35)
  p5 = c(Mejor = 240, Igual = 523, Peor = 554))   # PREGUNTA 5, prospective (N.S. 119, N.C. 1)
d <- irw::irw_fetch(TABLE)
obs <- unclass(table(factor(d$item, levels = c("p4","p5")), factor(d$resp, levels = 1:3)))
cat(sprintf("%-4s %-6s %10s %10s\n", "item", "level", "published", "live"))
for (i in rownames(PUBLISHED)) for (j in 1:3)
  cat(sprintf("%-4s %-6s %10d %10d\n", i, colnames(PUBLISHED)[j], PUBLISHED[i, j], obs[i, j]))
ok <- all(obs == PUBLISHED)
swapped <- all(obs[c("p5","p4"), ] == PUBLISHED)
cat(sprintf("\nall 6 cells match: %s; would a p4<->p5 swap also match: %s\n", ok, swapped))
cat("Two items with clearly different marginal distributions (Peor 854 vs 554, Mejor 42 vs 240),\n",
    "so this route distinguishes the two items from each other and fixes the direction of 1/2/3.\n", sep = "")
cat(if (ok && !swapped) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

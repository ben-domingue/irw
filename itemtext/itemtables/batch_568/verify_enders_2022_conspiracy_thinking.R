# verify_enders_2022_conspiracy_thinking.R -- Step 5b re-runnable check (batch_568)
#
# CLAIM. CTSCALE_1..CTSCALE_4 carry the four ACTS statements in this order:
#   CTSCALE_1 "Even though we live in a democracy, a few people will always run things anyway."
#   CTSCALE_2 "The people who really 'run' the country, are not known to the voters."
#   CTSCALE_3 "Big events like wars, the current recession, ... working in secret against the rest of us."
#   CTSCALE_4 "Much of our lives are being controlled by plots hatched in secret places."
# This is NOT the order the study's own S1 Appendix prints (plots, few, not known, big
# events); it is the order Uscinski et al. (2022, PLOS ONE 17:e0270429, same team) print
# in their main text, and the order of Kay & Slovic's labelled Qualtrics block.
#
# DERIVATION. data/enders_2022_conspiracy_vaccine.py keeps the Qualtrics export's own column
# names (CTSCALE_1..4) as `item`. The deposit (OSF 6a7et) has no question-text row, no
# codebook, and .dta labels that only repeat the names, so nothing in the study's files
# ties a column to a statement. The S1 Appendix numbers the items 1-4 but never names a code.
#
# ROUTE. Cross-sample structural match against the only ACTS data with labelled codes we
# hold: Kay & Slovic 2025 (IRW act_kay_2025; OSF uzrgk data_deidentified.csv, whose columns
# act_xxx_01_x..04_x are tied to wording by the study's own Qualtrics printouts, batch_405).
# Signature compared: per-item mean rank, % agreeing, first-factor loadings, and the six
# inter-item correlations. All 24 assignments of the four statements to CTSCALE_1..4 are
# scored; the claim passes only if it is the unique best and the appendix order is not.
# Klofstad et al. 2019 (Palgrave Commun 5:36) loadings are printed as a third sample.

suppressMessages(library(irw))

d <- irw::irw_fetch("enders_2022_conspiracy_thinking")   # served from the local irw cache
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
E <- w[, paste0("CTSCALE_", 1:4)]; E <- E[complete.cases(E), ]

p <- file.path(tempdir(), "kay_data.csv")
if (!file.exists(p))
  download.file("https://osf.io/download/z28r4/?view_only=aca403a5146240bda740e1e6d640751f",
                p, quiet = TRUE, mode = "wb")
K <- read.csv(p)
lab <- c("few people run things", "not known to voters", "big events/small groups", "plots hatched")
kay <- function(pfx) { x <- K[, paste0(pfx, sprintf("act_xxx_%02d_x", 1:4))]; x[complete.cases(x), ] }
K1 <- kay(""); K2 <- kay("t2_")

sig <- function(x, agree_cut) {
  x <- as.matrix(x)
  list(mean = colMeans(x), agree = colMeans(x >= agree_cut),
       load = as.numeric(factanal(x, 1)$loadings[, 1]), r = cor(x))
}
sE <- sig(E, 4); s1 <- sig(K1, 1); s2 <- sig(K2, 1)   # 4/5 = agree on 1-5; >=1 = agree on -3..3

cat(sprintf("n: Enders %d, Kay wave1 %d, Kay wave2 %d\n\n", nrow(E), nrow(K1), nrow(K2)))
cat(sprintf("%-10s %-24s %6s %6s %6s | %6s %6s %6s | %5s %5s %5s | %5s\n", "Enders", "Kay statement (claim)",
            "E%agr", "K1%", "K2%", "Eload", "K1ld", "K2ld", "Emean", "", "", "Klof19"))
KLOF <- c(.66, .75, .77, .79)   # Klofstad 2019 loadings: few, not known, big events, plots
for (i in 1:4)
  cat(sprintf("CTSCALE_%d  %-24s %6.1f %6.1f %6.1f | %6.2f %6.2f %6.2f | %5.2f %11s | %5.2f\n", i, lab[i],
              100 * sE$agree[i], 100 * s1$agree[i], 100 * s2$agree[i],
              sE$load[i], s1$load[i], s2$load[i], sE$mean[i], "", KLOF[i]))

off <- function(r) r[lower.tri(r)]
cat("\ninter-item r (pairs 21,31,41,32,42,43):\n")
cat("  Enders ", sprintf("%.2f", off(sE$r)), "\n")
cat("  Kay w1 ", sprintf("%.2f", off(s1$r)), "\n")
cat("  Kay w2 ", sprintf("%.2f", off(s2$r)), "\n")

# score an assignment perm: CTSCALE_i carries Kay statement perm[i]
score <- function(perm, s) {
  a <- cor(sE$agree, s$agree[perm], method = "spearman")
  l <- cor(sE$load, s$load[perm])
  r <- cor(off(sE$r), off(s$r[perm, perm]))
  c(agree_rho = a, load_r = l, interr_r = r, total = a + l + r)
}
perms <- as.matrix(expand.grid(1:4, 1:4, 1:4, 1:4)); perms <- perms[apply(perms, 1, function(z) length(unique(z)) == 4), ]
tot <- apply(perms, 1, function(pm) score(pm, s1)["total"] + score(pm, s2)["total"])
ord <- order(-tot)
cat("\nall 24 assignments, top 5 by summed fit over both Kay waves (max 6.00):\n")
for (k in ord[1:5]) cat(sprintf("  %s  %.3f\n", paste(perms[k, ], collapse = ""), tot[k]))
claim <- c(1, 2, 3, 4); appendix <- c(4, 1, 2, 3)   # appendix: CT1=plots, CT2=few, CT3=not known, CT4=big
ic <- which(apply(perms, 1, function(z) all(z == claim))); ia <- which(apply(perms, 1, function(z) all(z == appendix)))
cat(sprintf("\nclaim 1234: wave1 %s | wave2 %s | total %.3f (rank %d of 24)\n",
            paste(sprintf("%.2f", score(claim, s1)[1:3]), collapse = "/"),
            paste(sprintf("%.2f", score(claim, s2)[1:3]), collapse = "/"), tot[ic], which(ord == ic)))
cat(sprintf("S1-Appendix order 4123: wave1 %s | wave2 %s | total %.3f (rank %d of 24)\n",
            paste(sprintf("%.2f", score(appendix, s1)[1:3]), collapse = "/"),
            paste(sprintf("%.2f", score(appendix, s2)[1:3]), collapse = "/"), tot[ia], which(ord == ia)))
gap <- tot[ord[1]] - tot[ord[2]]
cat(sprintf("margin of best over runner-up: %.3f (runner-up %s)\n", gap, paste(perms[ord[2], ], collapse = "")))
cat("NOT established: this is a cross-sample inference (Enders July 2021 Qualtrics panel vs Kay\n",
    "US sample), not a label in Enders' own files. Positions 1 and 2 are pinned by wide margins;\n",
    "3 vs 4 rests on smaller differences (Enders means 2.86 vs 2.75; loadings .86 vs .84), and\n",
    "Klofstad 2019's loadings (.77 big events, .79 plots) lean the other way on that pair.\n", sep = "")

ok <- which(ord == ic) == 1 && which(ord == ia) > 1 && gap > 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

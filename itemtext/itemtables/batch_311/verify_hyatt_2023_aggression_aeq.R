# verify_hyatt_2023_aggression_aeq.R -- batch_311
#
# Claim being verified: the item text shipped for hyatt_2023_aggression_aeq is tied to the
# right item codes. Codes come from data/hyatt_2023_aggression.py:
#   prelim1_aeN[_r]  = column AEN[_R] of OSF "Preliminary Study 1" .sav  <- text: "AEQ - Study 1.docx" item N.
#   prelim2_aeN      = column AEN of "Preliminary Study 2" .sav           <- text: "AEQ - Study 2.docx" item N.
#   s1_aeN           = column AEN of "Study 1" .sav                        <- text: "AEQ - Study 3.docx" item N.
#   aeqNN            = AE_N of "Study 2" .sav (no labels) pooled with AEQN of "Study 3" .sav
#                      (variable labels = the shipped text)               <- text: "AEQ - Study 4.docx" / appendix.
# None of the prelim/s1/s2 .sav files carry variable labels, so the tie is "doc item number
# N == column number N" (paper_order). Checks below test that against the data.
#
# Published values are hard-coded from Hyatt et al. (2023) Aggressive Behavior 49:521-535,
# pre-copyedit manuscript on OSF (osf.io/fuz6h, file h4qxe): Table 2 (Study 1 EFA) and
# Table 3 (Study 2 / Study 3 CFA lambdas).

suppressMessages({ library(irw); library(dplyr); library(tidyr); library(psych); library(lavaan) })
TABLE <- "hyatt_2023_aggression_aeq"
d <- irw::irw_fetch(TABLE)
fails <- character(0)
chk <- function(ok, what) { cat(if (ok) "  ok:   " else "  FAIL: ", what, "\n", sep = ""); if (!ok) fails <<- c(fails, what) }
W <- function(st, items = NULL) {
  x <- d %>% filter(cov_study == st) %>% mutate(idw = paste(id, wave)) %>% select(idw, item, resp) %>%
    pivot_wider(names_from = item, values_from = resp)
  x <- as.data.frame(x[, -1]); if (!is.null(items)) x <- x[, items]; x }
lt <- lower.tri(diag(16))

# ---- 1. Study 1: reproduce paper Table 2 (4-factor PAF, oblimin) from s1 columns picked by doc numbering
cat("\n[1] Study 1 EFA vs paper Table 2 (own-factor loading), s1 items chosen by doc number\n")
s1_final <- c(1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 21, 22, 24, 26)  # doc: happy,right,justice,feel good | dominant,mess,capable,afraid | vulnerable,hurt,watch back,trouble | suffer,seriously,QoL,reputation
tab2 <- c(.57, .86, .69, .46, .72, .77, .67, .51, .81, .57, .76, .54, .58, .60, .68, .51)
f <- fa(W("s1", paste0("s1_ae", s1_final)), 4, fm = "pa", rotate = "oblimin")
own <- apply(abs(unclass(f$loadings)), 1, max)
print(data.frame(item = names(own), published = tab2, observed = round(own, 2)), row.names = FALSE)
chk(max(abs(own - tab2)) <= 0.03, sprintf("Table 2 reproduced, max |diff| = %.3f (tol .03)", max(abs(own - tab2))))
alt <- s1_final; alt[13] <- 29   # 'cause the other person pain' instead of 'really suffer'
own2 <- apply(abs(unclass(fa(W("s1", paste0("s1_ae", alt)), 4, fm = "pa", rotate = "oblimin")$loadings)), 1, max)
cat(sprintf("  (contrast: substituting s1_ae29 for s1_ae21 gives max |diff| %.3f)\n", max(abs(own2 - tab2))))

# ---- 2. Studies 2 and 3: CFA lambdas vs paper Table 3, positions 1-8 (whose row text agrees with the labels)
cat("\n[2] Study 2 / Study 3 CFA (WLSMV, continuous) vs paper Table 3\n")
mod <- 'A =~ aeq01+aeq02+aeq03+aeq04
B =~ aeq05+aeq06+aeq07+aeq08
C =~ aeq09+aeq10+aeq11+aeq12
D =~ aeq13+aeq14+aeq15+aeq16'
pub <- list(s2 = c(.64, .78, .80, .65, .64, .77, .84, .52, .73, .68, .71, .70, .80, .45, .70, .72),
            s3 = c(.75, .61, .70, .72, .71, .73, .76, .77, .63, .70, .68, .69, .75, .65, .64, .72)) # Table 3 rows 1..16 in printed order
for (st in c("s2", "s3")) {
  fit <- cfa(mod, data = W(st, sprintf("aeq%02d", 1:16)), estimator = "WLSMV", ordered = FALSE, std.lv = TRUE)
  s <- standardizedSolution(fit); l <- s$est.std[s$op == "=~"]
  cat(" ", st, "observed :", sprintf("%.2f", l), "\n  ", st, "Table 3  :", sprintf("%.2f", pub[[st]]), "\n")
  chk(max(abs(l[1:8] - pub[[st]][1:8])) <= 0.02, sprintf("%s positions 1-8 max |diff| %.3f (tol .02)", st, max(abs(l[1:8] - pub[[st]][1:8]))))
  cat(sprintf("  info: %s positions 9-16 max |diff| %.3f (Table 3 rows are in column order; their row TEXT is Table 2's order, see [3])\n",
              st, max(abs(l[9:16] - pub[[st]][9:16]))))
}

# ---- 3. Positions 9-16: which text order? Study-3 labels/appendix order vs Table 3's printed row labels.
# Compare each study's 16x16 correlation matrix with Study 1's matrix for the same TEXTS.
cat("\n[3] Correlation-structure congruence with Study 1 under two text orders for aeq09-aeq16\n")
R1 <- cor(W("s1", paste0("s1_ae", 1:31)), use = "pair")
doc   <- c(1, 2, 4, 5, 6, 7, 8, 9, 15, 11, 12, 14, 29, 22, 26, 24)  # shipped: trouble,vulnerable,hurt,watch | pain,seriously,reputation,QoL
paper <- c(1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 21, 22, 24, 26)  # Table 3 printed labels
for (st in c("s2", "s3")) {
  R <- cor(W(st, sprintf("aeq%02d", 1:16)), use = "pair")
  a <- cor(R[lt], R1[doc, doc][lt]); b <- cor(R[lt], R1[paper, paper][lt])
  set.seed(1); nul <- replicate(1000, { p <- sample(31, 16); cor(R[lt], R1[p, p][lt]) })
  cat(sprintf("  %s: shipped order r = %.3f | Table-3-label order r = %.3f | random 16 s1 items 99th pct = %.3f\n", st, a, b, quantile(nul, .99)))
  chk(a > b + 0.02, paste(st, "shipped (label) order beats Table 3 label order"))
}

# ---- 4. Cross-study means of the same wording (all four MTurk samples) along the doc links
cat("\n[4] Same-wording item means across studies (links printed in the version docs)\n")
m <- tapply(d$resp, d$item, mean); ms2 <- with(d[d$cov_study == "s2", ], tapply(resp, item, mean))
p2link <- c(`2`=18,`3`=44,`4`=66,`5`=4,`6`=6,`7`=7,`8`=67,`9`=2,`10`=1,`12`=21,`14`=71,`15`=32,`17`=73,`18`=63,`19`=69,`20`=39,
            `21`=51,`23`=68,`24`=23,`25`=11,`28`=13,`32`=81,`33`=10,`34`=24)          # prelim2 item -> prelim1 item (present in both files)
s1link <- c(`1`=2,`2`=3,`3`=5,`4`=6,`6`=9,`7`=10,`8`=12,`9`=14,`10`=17,`11`=18,`13`=20,`14`=21,`15`=23,`17`=25,`18`=28,`19`=29,
            `20`=32,`21`=33,`22`=34,`23`=39,`24`=40)                                  # s1 item -> prelim2 item (s1 #3 doc says (4); text is prelim2 #5)
chains <- list(
  p1_p2 = data.frame(a = m[paste0("prelim2_ae", names(p2link))], b = m[paste0("prelim1_ae", p2link)]),
  p2_s1 = data.frame(a = m[paste0("s1_ae", names(s1link))], b = m[paste0("prelim2_ae", s1link)]),
  s1_s2 = data.frame(a = ms2[sprintf("aeq%02d", 1:16)], b = m[paste0("s1_ae", doc)]))
for (nm in names(chains)) { x <- chains[[nm]]; r <- cor(x$a, x$b)
  set.seed(2); nul <- replicate(2000, cor(x$a, sample(x$b)))
  cat(sprintf("  %s: %d pairs, r = %.3f, mean |diff| = %.2f, permutation 99th pct = %.3f\n", nm, nrow(x), r, mean(abs(x$a - x$b)), quantile(nul, .99)))
  chk(r >= 0.85, paste(nm, "linked means r >= .85")) }

# ---- 5. Valence class per item (positive vs negative expectancy) from the correlation matrix
cat("\n[5] Valence class: mean r with positive-class items minus mean r with negative-class items\n")
pos1 <- c(1,15,28,40,52,64, 2,16,29,41,53,65, 3,17,30,54,66,74, 4,18,31,42,55,75, 5,19,32,43,67,76, 6,20,33,44,56,77, 7,21,34,45,57,78) # Study 1 doc theme table
cls <- list(prelim1 = function(n) n %in% pos1, prelim2 = function(n) n <= 16, s1 = function(n) n <= 9)
num <- function(x) as.integer(sub("^.*_ae([0-9]+).*$", "\\1", x))
sc_all <- list()
for (st in names(cls)) { w <- W(st); R <- cor(w, use = "pair"); n <- num(names(w)); pv <- cls[[st]](n)
  sc <- sapply(seq_along(n), function(i) mean(R[i, pv & seq_along(n) != i]) - mean(R[i, !pv & seq_along(n) != i]))
  names(sc) <- names(w); sc_all[[st]] <- sc
  ok <- sign(sc) == ifelse(pv, 1, -1)
  cat(sprintf("  %s: %d/%d items on the predicted side; off-side: %s\n", st, sum(ok), length(ok),
              paste(sprintf("%s (%.2f)", names(w)[!ok], sc[!ok]), collapse = ", ")))
  chk(mean(ok) >= 0.95, paste(st, "valence agreement >= 95%")) }
cat("  (prelim1_ae71 'They'll be afraid of me in the future.' sits in a negative THEME row of the design table but\n",
    "   is positive in content, and prelim2 moved it to its positive factor, so its off-side score is expected.)\n", sep = "")

# ---- 6. Reverse-scoring status of the reverse-worded items (drives the reversed option_text on *_r items)
cat("\n[6] Reverse-worded items\n")
sp1 <- sc_all$prelim1
cat(sprintf("  prelim1 _r scores: %s\n", paste(sprintf("%s %.2f", grep("_r$", names(sp1), value = TRUE), sp1[grep("_r$", names(sp1))]), collapse = "; ")))
chk(sp1["prelim1_ae17_r"] > 0 && sp1["prelim1_ae19_r"] > 0 && sp1["prelim1_ae47_r"] < 0 && sp1["prelim1_ae48_r"] < 0,
    "prelim1 17_r/19_r (positive themes) load positive and 47_r/48_r (negative themes) negative => stored reversed")
cat(sprintf("  raw-wording 'won't actually help me accomplish any of my goals': prelim2_ae29 %.2f, s1_ae19 %.2f (negative side => stored raw)\n",
            sc_all$prelim2["prelim2_ae29"], sc_all$s1["s1_ae19"]))
chk(sc_all$prelim2["prelim2_ae29"] < 0 && sc_all$s1["s1_ae19"] < 0, "prelim2_ae29 and s1_ae19 stored raw")
cat(sprintf("  prelim2_ae29 mean %.2f vs 6 - prelim1_ae19_r mean %.2f\n", m["prelim2_ae29"], 6 - m["prelim1_ae19_r"]))
chk(abs(m["prelim2_ae29"] - (6 - m["prelim1_ae19_r"])) < 0.5, "same item, opposite storage direction, means agree after reflection")

cat("\nNOT established: order WITHIN a block of similar items is pinned only where published loadings exist\n",
    "(the 16 s1 items of Table 2; aeq01-aeq08 via Table 3). For aeq09-aeq16 the Study-3 .sav labels are the tie for\n",
    "Study 3 respondents; for Study 2 respondents [3] shows the label order fits better than the paper's printed order\n",
    "but does not separate every within-block permutation. The remaining prelim1/prelim2/s1 items are supported only\n",
    "globally ([4] linked means, [5] valence class), not item-by-item.\n", sep = "")
cat(if (length(fails) == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

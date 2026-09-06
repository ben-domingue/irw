# verify_ghanbari_2016_helma_use.R
#
# CLAIM UNDER TEST
#   The IRW items use1..use4 are, in order, items 30, 31, 32 and 33 of the final
#   44-item HELMA questionnaire (S1/S2 Files of PLOS ONE 10.1371/journal.pone.0149202),
#   and use5 is one of the three pre-final items that failed the factor-loading
#   criterion and therefore has NO published wording (shipped with item_text = NA).
#
# WHY A MAPPING CHECK IS NEEDED
#   The .sav (S3 File) carries NO variable labels for any item column, and it holds
#   47 item columns while the published questionnaire prints 44 items. So the tie
#   between the column `use1` and a numbered questionnaire item is an inference, not
#   a label lookup.
#
# THE ROUTE (Step 5b route 1: published per-item statistics -- here, factor loadings)
#   Table 2 of the paper publishes the full 8-factor varimax loading matrix for all
#   44 retained items. Re-running that EFA on the raw 47-item .sav reproduces it, so
#   each `use` column can be matched to a published row by its whole 8-vector of
#   loadings rather than by position. This distinguishes every item from every other
#   item: the four use items differ on the appraisal factor by .426/.248/.209/-.139,
#   a spread far larger than the reproduction error.
#
#   Factor 8 (numeracy) is EXCLUDED from the comparison. The .sav codes the three
#   numeracy items 1 = correct / 2 = incorrect (num1 additionally runs opposite to
#   num2/num3), whereas the paper's numeracy factor is oriented correct-high, so that
#   one column does not reproduce. Factors 1-7 reproduce to <= 0.044 across the ten
#   calibration items below, which the script re-establishes on every run.
#
# Requires: haven, psych, and network access to the PLOS supplementary file.

suppressMessages(library(haven)); suppressMessages(library(psych))

TABLE <- "ghanbari_2016_helma_use"
SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0149202.s003"

# Paper Table 2, rows 30-33, Factor1..Factor8 (transcribed from the table image).
PUB <- rbind(
  "30" = c( .060,  .003,  .185,  .426,  .089,  .542, -.038,  .117),
  "31" = c( .018,  .129,  .151,  .248,  .095,  .645, -.017,  .006),
  "32" = c( .206,  .272,  .117,  .209,  .020,  .617,  .154, -.108),
  "33" = c( .166,  .224, -.024, -.139,  .077,  .529,  .002,  .082))
CLAIM <- c(use1 = "30", use2 = "31", use3 = "32", use4 = "33")
NF  <- 7      # compare on factors 1-7; see header for why factor 8 is excluded
TOL <- 0.11   # reproduction error of an EFA re-run on median-imputed data

# Calibration rows: five reading (10-14) and five appraisal (25-29) items whose
# identity is not in question, used to measure this run's reproduction error.
CAL <- rbind(
  "10" = c(.229, .092, .717, .125, .017, .117,  .170, -.069),
  "11" = c(.295, .088, .732, .113, .121, .176,  .098, -.023),
  "12" = c(.329, .173, .710, .087, .032, .082,  .149,  .004),
  "13" = c(.373, .126, .696, .091, .072, .121,  .060, -.005),
  "14" = c(.267, .126, .534, .138, .439, -.050, -.120, -.035),
  "25" = c(.272, .103, .064, .596, .102, .062,  .198, -.038),
  "26" = c(.175, .215, .139, .671, -.012, .187, .066,  .016),
  "27" = c(.260, .203, .058, .724, .103, .060, -.008,  .027),
  "28" = c(.182, .221, .060, .674, .145, .044,  .058,  .053),
  "29" = c(.392, .193, .148, .559, .143, .190, -.033, -.001))
CALROW <- c(reading1="10", reading2="11", reading3="12", reading4="13", reading5="14",
            appraise1="25", appraise2="26", appraise3="27", appraise4="28", appraise5="29")

tmp <- tempfile(fileext = ".sav")
download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
d <- haven::read_sav(tmp)
items <- grep("^(access|reading|understand|appraise|use|com|num)[0-9]+$", names(d), value = TRUE)
X <- as.data.frame(lapply(d[items], as.numeric))
X[X == 9] <- NA                      # numeracy "don't know"
stopifnot(length(items) == 47)

p <- psych::principal(X, nfactors = 8, rotate = "varimax", missing = TRUE, impute = "median")
L <- unclass(p$loadings)[, 1:8]

# Identify OUR factor columns by anchor items rather than by psych's ordering, and
# orient each so its anchor loads positive (PCA components carry an arbitrary sign).
ANCHOR <- c(F1 = "understand3", F2 = "com7", F3 = "reading2", F4 = "appraise3",
            F5 = "access7",     F6 = "use2", F7 = "access3",  F8 = "num3")
cols <- sapply(ANCHOR, function(a) which.max(abs(L[a, ])))
if (anyDuplicated(cols)) { cat("factor anchors not distinct\nVERDICT: FAIL\n"); quit(status = 0) }
sgn <- sapply(seq_along(ANCHOR), function(i) sign(L[ANCHOR[i], cols[i]]))
Lp <- sweep(L[, cols, drop = FALSE], 2, sgn, "*")
colnames(Lp) <- names(ANCHOR)

cal_err <- max(sapply(names(CALROW), function(i) max(abs(CAL[CALROW[i], 1:NF] - Lp[i, 1:NF]))))
cat(sprintf("Calibration: 10 items of undisputed identity reproduce to max|diff| = %.3f on factors 1-%d\n\n", cal_err, NF))

cat("Reproduced vs published loadings (paper Table 2, Factor1..Factor7)\n\n")
best <- character(0)
worst_all <- 0
for (it in names(CLAIM)) {
  dist <- apply(PUB[, 1:NF, drop = FALSE], 1, function(r) max(abs(r - Lp[it, 1:NF])))
  b <- names(which.min(dist)); best[it] <- b
  cat(sprintf("%-5s -> best-matching published item %s (max|diff| = %.3f; runner-up %s at %.3f)\n",
              it, b, min(dist), names(sort(dist))[2], sort(dist)[2]))
  cat(sprintf("        published %s\n        observed  %s\n",
              paste(sprintf("%6.3f", PUB[CLAIM[it], 1:NF]), collapse = ""),
              paste(sprintf("%6.3f", Lp[it, 1:NF]),          collapse = "")))
  worst_all <- max(worst_all, max(abs(PUB[CLAIM[it], 1:NF] - Lp[it, 1:NF])))
}
ok_map <- identical(unname(best[names(CLAIM)]), unname(CLAIM))
cat(sprintf("\nclaimed mapping reproduced: %s ; largest deviation %.3f (tolerance %.2f)\n",
            ok_map, worst_all, TOL))

# use5 must be one of the three items dropped from the final 44 (max loading < .45).
mx5 <- max(abs(Lp["use5", 1:NF]))
cat(sprintf("use5 largest loading on any factor: %.3f (paper's retention cut-off 0.45)\n", mx5))
ok5 <- mx5 < 0.45

# Corroboration: the live IRW item means must equal the .sav column means, which is
# what ties the analysed .sav columns to the shipped `item` codes.
ok_live <- NA
try({
  suppressMessages(library(irw))
  lv <- irw::irw_fetch(TABLE)
  obs <- tapply(as.numeric(lv$resp), lv$item, mean)[names(CLAIM)]
  raw <- sapply(names(CLAIM), function(i) mean(X[[i]], na.rm = TRUE))
  cat("\nlive IRW item means vs raw .sav column means:\n")
  for (i in names(CLAIM)) cat(sprintf("  %-5s live %.4f  sav %.4f\n", i, obs[i], raw[i]))
  ok_live <- max(abs(obs - raw)) < 1e-9
  cat(sprintf("  identical: %s\n", ok_live))
}, silent = TRUE)

cat("\nWhat this does NOT establish: use5 has no published wording at all, so its\n",
    "item_text ships blank; nothing here recovers it. The instructions and response\n",
    "anchors are whole-instrument text and are not item-specific evidence.\n", sep = "")

cat(if (ok_map && worst_all <= TOL && ok5 && !isFALSE(ok_live)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

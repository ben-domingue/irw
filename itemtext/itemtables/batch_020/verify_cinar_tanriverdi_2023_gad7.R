# verify_cinar_tanriverdi_2023_gad7.R
#
# Claim under test: GAD1..GAD7 in the IRW table carry the canonical GAD-7 item
# numbering, so item_text for GADk is the Turkish (Konkan et al. 2013) rendering
# of GAD-7 item k; and resp 0..3 ascends "hic" -> "hemen hemen her gun".
#
# The item codes are the .sav's own column names (data/cinar_tanriverdi_2023_pmss_gad7.py
# melts GAD1..GAD7 verbatim), and the .sav carries NO variable or value labels --
# so the code->text tie rests on the numbering, and that is what is checked here.
#
# Two falsifiable predictions:
#  (A) resp direction. Cinar Tanriverdi et al. 2023 (PLOS ONE 18(8):e0288769)
#      report a GAD-7 total of 11.0 +/- 5.5 in this sample. Summing the live 0-3
#      responses must reproduce that; the reversed coding (3 = "hic") would give
#      21 - 11.0 = 10.0.
#  (B) item ordering. Konkan et al. 2013 (Noropsikiyatri Arsivi 50:53-58, Table 1)
#      publish per-item means for the same Turkish form in a non-clinical control
#      group (n=134). The live student sample is more anxious overall, so absolute
#      means differ, but the item PROFILE should track: item 6 highest, item 5
#      lowest, item 7 second-lowest.

suppressMessages(library(irw))
TABLE <- "cinar_tanriverdi_2023_gad7"

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
its <- paste0("GAD", 1:7)

## ---- (A) resp direction, via the published total ----------------------------
w   <- reshape(d[, c("id", "item", "resp")], idvar = "id",
               timevar = "item", direction = "wide")
X   <- as.matrix(w[, paste0("resp.", its)])
tot <- rowSums(X)
PUB_TOT_M  <- 11.0; PUB_TOT_SD <- 5.5
cat("--- (A) resp direction ---\n")
cat(sprintf("published total  : %.1f +/- %.1f  (paper abstract & Results)\n",
            PUB_TOT_M, PUB_TOT_SD))
cat(sprintf("observed  as-is  : %.2f +/- %.2f   (n=%d, range %d-%d)\n",
            mean(tot), sd(tot), length(tot), min(tot), max(tot)))
cat(sprintf("observed reversed: %.2f            (21 - as-is; the rival coding)\n",
            mean(21 - tot)))
okA <- abs(mean(tot) - PUB_TOT_M) < 0.3 &&
       abs(mean(tot) - PUB_TOT_M) < abs(mean(21 - tot) - PUB_TOT_M)

## ---- (B) item profile vs Konkan et al. 2013 Table 1 control group -----------
KONKAN_CTRL <- c(1.14, 0.79, 0.85, 0.85, 0.63, 1.16, 0.68)   # items 1..7, n=134
obs  <- tapply(d$resp, d$item, mean)[its]
flr  <- tapply(d$resp, d$item, function(x) mean(x == 0))[its]
cat("\n--- (B) item profile ---\n")
cat(sprintf("%-6s %10s %10s %8s %8s\n",
            "item", "live mean", "Konkan", "rank(l)", "floor%"))
for (i in seq_along(obs))
  cat(sprintf("%-6s %10.2f %10.2f %8.1f %7.1f%%\n",
              its[i], obs[i], KONKAN_CTRL[i],
              rank(-obs)[i], 100 * flr[i]))
rho <- suppressWarnings(cor(as.numeric(obs), KONKAN_CTRL, method = "spearman"))
cat(sprintf("\nSpearman(live, Konkan control) over 7 items: %.2f\n", rho))
cat(sprintf("lowest-mean item : %s (live)   %s (Konkan)\n",
            its[which.min(obs)], its[which.min(KONKAN_CTRL)]))
cat(sprintf("highest-mean item: %s (live)   %s (Konkan)\n",
            its[which.max(obs)], its[which.max(KONKAN_CTRL)]))
okB <- its[which.min(obs)]  == "GAD5" &&
       its[which.max(obs)]  == "GAD6" &&
       its[order(obs)][2]   == "GAD7" &&
       rho > 0.6

cat("\nNot established by (B): GAD1..GAD4 sit within 0.20 of one another",
    "(1.58, 1.59, 1.79, 1.63) and their live rank order (3>4>2>1) does not",
    "match Konkan's control order (1>3=4>2), so this route does NOT separate",
    "items 1-4 from each other. It pins the extremes only -- hence PARTIAL,",
    "not VERIFIED, in verification_cinar_tanriverdi_2023_gad7.csv.\n", sep = "\n")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_li_2024_bdyz.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST. li_2024_bdyz holds the four-item Expressive Suppression (ES)
# subscale of the ERQ (Gross & John 2003), NOT the "body-image scale subset" the
# IRW dictionary Description calls it, and its resp runs 1 = Strongly Disagree ..
# 7 = Strongly Agree with NO reverse scoring. The source columns BDYZ1/2/6/9 map
# to IRW codes bdyz_1/2/6/9 by a number-preserving rename in
# data/li_2024_socialavoidance.py (regex extract of the trailing digits).
#
# The falsifiable predictions come from Li et al. (2024) PeerJ 12:e17910:
#   - ES total: mean 14.66, SD 5.61, N = 1,151          (Results, descriptives)
#   - Cronbach's alpha for the ES subscale = 0.834       (Methods)
#   - Table 2: r(expressive suppression, social physique anxiety) = 0.219
# The SPA total needed for that correlation is itself checked (published 43.21 /
# 10.52) so the comparison cannot pass on a mis-scored companion scale.
#
# Fetches the source deposit (Europe PMC supplementary zip, peerj-12-17910-s001.xlsx).
# It does NOT export the IRW table: the source->IRW tie is a mechanical rename,
# already read out of the processing script.

suppressWarnings(suppressMessages({library(readxl); library(utils)}))

URL <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11332389/supplementaryFiles"
tmp <- tempfile(fileext = ".zip"); dir <- tempfile(); dir.create(dir)
download.file(URL, tmp, quiet = TRUE, mode = "wb")
unzip(tmp, exdir = dir)
xl <- list.files(dir, pattern = "s001\\.xlsx$", full.names = TRUE)[1]
d <- as.data.frame(read_excel(xl))

B <- c("BDYZ1", "BDYZ2", "BDYZ6", "BDYZ9")
es <- rowSums(d[, B])

cat(sprintf("N = %d (published 1,151)\n", sum(!is.na(es))))
cat(sprintf("ES total  mean %.2f (published 14.66)   SD %.2f (published 5.61)\n",
            mean(es), sd(es)))

# Cronbach's alpha
k <- length(B)
alpha <- k / (k - 1) * (1 - sum(apply(d[, B], 2, var)) / var(es))
cat(sprintf("Cronbach's alpha %.4f (published 0.834)\n", alpha))

# SPA total, reverse-scoring items 1,3,7,11,13,14 per supplement S2 (peerj-12-17910-s002.docx)
SPA <- paste0("SPA", 1:15)
S <- d[, SPA]
for (i in c(1, 3, 7, 11, 13, 14)) S[[paste0("SPA", i)]] <- 6 - S[[paste0("SPA", i)]]
spa <- rowSums(S)
cat(sprintf("SPA total mean %.2f (published 43.21)   SD %.2f (published 10.52)\n",
            mean(spa), sd(spa)))
r <- cor(es, spa)
cat(sprintf("r(ES, SPA) = %.3f (published Table 2: 0.219)\n", r))

# Which item is which: corrected item-total correlations.
cat("\ncorrected item-total correlations (all four behave as suppression items):\n")
for (b in B) cat(sprintf("  %-6s r = %.3f\n", b, cor(d[[b]], rowSums(d[, setdiff(B, b)]))))

cat("\nWhat this does NOT establish: which ERQ item each column is. The ERQ's\n",
    "suppression items are numbered 2, 4, 6, 9; the deposit ships 1, 2, 6, 9, so\n",
    "the column labelled BDYZ1 is assigned ERQ item 4 by elimination (it is a\n",
    "suppression item -- item-total r = 0.63 -- and item 4 is the only suppression\n",
    "item otherwise unaccounted for). Nothing here separates item 2 from item 6\n",
    "either. Verification status is PARTIAL for that reason.\n", sep = "")

ok <- abs(mean(es) - 14.66) < 0.01 && abs(sd(es) - 5.61) < 0.01 &&
      abs(alpha - 0.834) < 0.002 && abs(r - 0.219) < 0.002
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

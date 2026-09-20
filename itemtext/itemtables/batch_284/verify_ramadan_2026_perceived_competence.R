# Step 5b mapping verification: ramadan_2026_perceived_competence (batch_284)
#
# Route 9 (response-frequency matching), run live-vs-raw-deposit-column.
# The claim under test: each live item code PCi carries the wording that
# codebook.csv prints against the variable name PCi. data/ramadan_2026_genai_competency.py
# melts the columns matching 'PC\d+' straight out of the deposit CSV, so that claim is
# false iff the live PCi does not hold the raw column PCi. This checks it by fingerprint:
# every live item's 1-5 response-count vector must reproduce the raw column of the SAME
# name and NO other PC column (a 6x6 identity match matrix). If any two items' item_text
# were swapped, one of the off-diagonal cells would be TRUE and a diagonal cell FALSE.
#
# Raw counts are hard-coded from arabic_genai_competency_data.csv,
# sha256 0e47f8175e08088caec313c2c81ab006b8e2266ab5696f5d6c33243ee9c0efad
# (Mendeley Data 10.17632/xd27t4g547 V1, CC BY 4.0) so the script needs only the live fetch.
suppressMessages(library(irw))

TABLE <- "ramadan_2026_perceived_competence"
ITEMS <- paste0("PC", 1:6)

# raw deposit per-item response counts for resp = 1,2,3,4,5
RAW <- rbind(
  PC1 = c(14, 27, 42, 50, 10),
  PC2 = c( 9, 31, 45, 48,  9),
  PC3 = c( 4, 14, 43, 63, 19),
  PC4 = c( 6, 10, 32, 46, 49),
  PC5 = c( 5, 27, 53, 42, 16),
  PC6 = c( 3, 25, 60, 40, 16)
)

d <- irw::irw_fetch(TABLE)
LIVE <- t(sapply(ITEMS, function(it)
  as.integer(table(factor(d$resp[d$item == it], levels = 1:5)))))
dimnames(LIVE) <- list(ITEMS, 1:5)

cat(sprintf("%-5s %-20s %-20s %6s %6s\n", "item", "live 1/2/3/4/5", "raw 1/2/3/4/5", "n_live", "n_raw"))
for (it in ITEMS)
  cat(sprintf("%-5s %-20s %-20s %6d %6d\n", it,
              paste(LIVE[it, ], collapse = "/"), paste(RAW[it, ], collapse = "/"),
              sum(LIVE[it, ]), sum(RAW[it, ])))
cat(sprintf("\ntotal responses: live %d, raw %d (dictionary: 858)\n", sum(LIVE), sum(RAW)))

M <- outer(ITEMS, ITEMS, Vectorize(function(i, j) identical(unname(LIVE[i, ]), unname(as.integer(RAW[j, ])))))
dimnames(M) <- list(live = ITEMS, raw = ITEMS)
cat("\nlive (rows) vs raw (cols) fingerprint match matrix:\n"); print(M)

ok <- all(diag(M)) && sum(M) == length(ITEMS)
cat(sprintf("\ndiagonal all TRUE: %s; off-diagonal matches: %d (want 0)\n",
            all(diag(M)), sum(M) - sum(diag(M))))
cat("Does NOT establish the resp<->option_text direction: the deposit stores bare\n",
    "integers and publishes no per-label counts, so the 1..5 anchor order is taken\n",
    "from codebook.csv's coding string rather than checked against the data.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

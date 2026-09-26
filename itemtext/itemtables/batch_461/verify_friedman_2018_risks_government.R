# verify_friedman_2018_risks_government.R -- batch_461, Step 5b.
#
# Claim: live IRW item codes charm/climchoi/cprotect/iinterests/iprivacy/iprotect are the
# lowercased Qualtrics column names of Risk_Data_Base (Dataverse doi:10.7910/DVN/ZSJA25),
# and the codebook (Codebook.pdf pp.2-4) prints each statement under that exact column
# name. resp 1..6 = Strongly disagree .. Strongly agree (data/friedman_2018_risks.do
# `label define likert`, identical to the study's own Risk_Code_Respondents.do recode).
#
# Route 9 (response-frequency matching): each source column's label counts, recoded
# with the 1..6 map, must equal the live item's integer counts cell for cell -- this
# checks option<->resp direction AND that every live code holds its own column (the six
# count vectors are mutually distinct, so a swapped code would break the match).
# Route 6 (keying polarity): the three communitarian-worded statements (charm, climchoi,
# cprotect) must correlate positively with each other and negatively with the three
# individualist ones (iinterests, iprivacy, iprotect) --
# checks the codebook's wording against the data's content.
#
# NOT established: the statistics do not by themselves tie a statement to a column
# within a polarity class; that tie is the codebook's explicit per-variable entry
# (a label match, not an inference).

suppressMessages(library(irw))
TABLE <- "friedman_2018_risks_government"
ITEMS <- c("charm","climchoi","cprotect","iinterests","iprivacy","iprotect")
LEVELS <- c("Strongly disagree","Moderately disagree","Slightly disagree",
            "Slightly agree","Moderately agree","Strongly agree")

tab <- file.path(tempdir(), "Risk_Data_Base.tab")
if (!file.exists(tab))
  download.file("https://dataverse.harvard.edu/api/access/datafile/3214210", tab,
                mode = "wb", quiet = TRUE)
src <- read.delim(tab, stringsAsFactors = FALSE, check.names = FALSE)
names(src) <- tolower(names(src))

live <- as.data.frame(irw::irw_fetch(TABLE))

ok <- TRUE
cat("Route 9: per-item counts, source label (mapped 1..6) vs live resp\n")
srcmat <- matrix(NA, 6, 6, dimnames = list(ITEMS, 1:6))
for (it in ITEMS) {
  s <- as.integer(table(factor(match(src[[it]], LEVELS), levels = 1:6)))
  l <- as.integer(table(factor(live$resp[live$item == it], levels = 1:6)))
  unmapped <- sum(!is.na(src[[it]]) & src[[it]] != "" & is.na(match(src[[it]], LEVELS)))
  srcmat[it, ] <- s
  same <- identical(s, l) && unmapped == 0
  ok <- ok && same
  cat(sprintf("  %-10s src %s | live %s | unmapped %d | %s\n", it,
              paste(s, collapse = "/"), paste(l, collapse = "/"), unmapped,
              if (same) "MATCH" else "MISMATCH"))
}
distinct <- nrow(unique(srcmat)) == 6
cat(sprintf("  six source count vectors mutually distinct: %s\n", distinct))
ok <- ok && distinct

cat("\nRoute 6: polarity (communitarian charm/climchoi/cprotect vs individualist i*), live data\n")
w <- reshape(live[live$item %in% ITEMS, c("id","item","resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- cor(w[, ITEMS], use = "pairwise.complete.obs")
print(round(r, 2))
e <- ITEMS[1:3]; h <- ITEMS[4:6]
within <- c(r[e, e][upper.tri(r[e, e])], r[h, h][upper.tri(r[h, h])])
between <- as.vector(r[e, h])
cat(sprintf("  within-class r range %.2f..%.2f ; between-class r range %.2f..%.2f\n",
            min(within), max(within), min(between), max(between)))
pol <- all(within > 0) && all(between < 0)
cat(sprintf("  polarity pattern as codebook wording predicts: %s\n", pol))
ok <- ok && pol

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# Verification for disgust_berger2014 (#2228, batch_303).
#
# SOURCE. Harvard Dataverse doi:10.7910/DVN/27285 (CC0), which ships three
# things that together settle the mapping: the tab-delimited response file
# whose columns are Q1..Q27, the administered Hebrew questionnaire
# (DS-R_Hebrew.pdf, items numbered 1..27), and the study's own SPSS syntax.
#
# Route 1: the two catch items the DS-R designates (12 and 16) are exactly the
#   two Q-codes absent from the live table -- so Q-number == DS-R item number.
# Route 2: the deposit's own syntax reverse-codes Q1, Q6 and Q10, which are the
#   DS-R's three reverse-keyed items; and the live data are NOT reverse-coded,
#   so the shipped anchors apply in the printed direction.
# Route 3: the section split shipped here (1-14 agreement, 15-27 disgust rating)
#   is the split printed in the Hebrew PDF and in the DS-R master copy.
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

raw <- cached_source(".cache/batch_303/dv_2509243.bin",      # tab file
                     "https://dataverse.harvard.edu/api/access/datafile/2509243")
syn <- cached_source(".cache/batch_303/dv_2509396.bin",      # syntax in txt format
                     "https://dataverse.harvard.edu/api/access/datafile/2509396")

d <- as.data.frame(irw::irw_fetch("disgust_berger2014"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- shipped_items("disgust_berger2014", "itemtables/batch_303/disgust_berger2014__items.csv")

hdr <- strsplit(readLines(raw, n = 1, warn = FALSE), "\t")[[1]]
qcols <- grep("^Q", hdr, value = TRUE)

cat("=== Route 1: the catch items are the two missing codes ===\n")
cat(sprintf("  raw file Q-columns (%d): %s\n", length(qcols), paste(qcols, collapse = " ")))
catch <- grep("_Catch$", qcols, value = TRUE)
live <- sort(unique(d$item))
cat(sprintf("  columns flagged _Catch in the raw file: %s\n", paste(catch, collapse = ", ")))
cat(sprintf("  live item count: %d\n", length(live)))
r1 <- setequal(setdiff(sub("_Catch$", "", qcols), sub("_Catch$", "", catch)), live) &&
      setequal(sub("_Catch$", "", catch), c("Q12", "Q16"))
cat(sprintf("  -> live items are exactly Q1..Q27 minus Q12 and Q16: %s\n", r1))
cat("  Q12 ('I would rather eat a piece of fruit than a piece of paper') and\n")
cat("  Q16 ('You see a person eating an apple with a knife and fork') are the\n")
cat("  DS-R's two designated catch items. Their positions pin the numbering.\n")

cat("\n=== Route 2: reverse keying, and which direction the data are in ===\n")
rc <- grep("^RECODE Q", readLines(syn, warn = FALSE), value = TRUE)
rev_syntax <- sort(unique(sub("^RECODE (Q[0-9]+).*", "\\1", rc)))
cat(sprintf("  deposit syntax reverse-codes: %s\n", paste(rev_syntax, collapse = ", ")))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
rit <- sapply(colnames(m), function(c)
    stats::cor(m[, c], rowMeans(m[, setdiff(colnames(m), c), drop = FALSE], na.rm = TRUE),
               use = "pairwise.complete.obs"))
neg <- sort(names(rit)[rit < 0.1])
cat("  item-total correlations below 0.10 in the live data: ",
    paste(sprintf("%s (%.3f)", neg, rit[neg]), collapse = ", "), "\n")
r2 <- setequal(neg, rev_syntax) && setequal(rev_syntax, c("Q1", "Q6", "Q10"))
cat(sprintf("  -> the weakly/negatively keyed items are exactly the ones the\n"))
cat(sprintf("     deposit reverse-codes, i.e. the live table is UN-reversed: %s\n", r2))
cat("  This is the direction check for the shipped anchors: 0 = strongly\n")
cat("  disagree stands as printed, and is NOT the recoded value.\n")

cat("\n=== Route 3: the two administered sections ===\n")
s <- unique(items[, c("item", "section_id")])
n <- as.integer(sub("^Q", "", s$item))
sec1 <- sort(n[s$section_id == "disgust_berger2014_1"])
sec2 <- sort(n[s$section_id == "disgust_berger2014_2"])
cat(sprintf("  section 1 (agreement, 0-4): %s\n", paste(sec1, collapse = " ")))
cat(sprintf("  section 2 (disgust rating, 0-4): %s\n", paste(sec2, collapse = " ")))
r3 <- all(sec1 <= 14) && all(sec2 >= 15) && length(sec1) == 13 && length(sec2) == 12
cat(sprintf("  -> split at 14/15, as printed in the Hebrew PDF and the DS-R: %s\n", r3))
o1 <- unique(items$option_text[items$section_id == "disgust_berger2014_1"])
o2 <- unique(items$option_text[items$section_id == "disgust_berger2014_2"])
cat(sprintf("  distinct anchor sets: %d in section 1, %d in section 2\n", length(o1), length(o2)))
r3b <- length(o1) == 5 && length(o2) == 5 && !length(intersect(o1, o2))

cat("\n=== What this does NOT establish ===\n")
cat("  The Hebrew wording was read off a rendering of DS-R_Hebrew.pdf rather\n")
cat("  than its text layer: the PDF's text runs transpose characters across run\n")
cat("  boundaries (e.g. 'mi-la'avor' comes out as 'la-m' + ''avor'). Two source\n")
cat("  typos are shipped as printed: item 4 'tsiburim' for 'tsiburiyim', and\n")
cat("  item 13 'lo hayit' (2nd person) where the sentence is 1st person.\n")
cat("  The English is the DS-R master copy, not a translation of this Hebrew.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r3b) "PASS" else "FAIL", "\n")

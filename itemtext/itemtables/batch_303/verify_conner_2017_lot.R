# Verification for conner_2017_lot (#2228, batch_303).
#
# SOURCE. PLOS ONE 10.1371/journal.pone.0171206 supplementary S1 (.sav, CC BY).
# Item wording and anchors come from its SPSS variable and value labels, so the
# item mapping itself needs no inference: lot1..lot6 / rlot1..rlot6 -> item1..6.
# What DOES need verifying is the direction of the anchors, because the labels
# contradict themselves: three variables are labelled '(already reverse scored)'
# while carrying the same 1 = Strongly disagree value labels as the rest.
#
# Route 1: the label text shipped matches the .sav, code for code.
# Route 2: all six items correlate POSITIVELY with each other, which cannot
#   happen if the three pessimism-worded items are stored as raw agreement.
# Route 3: all six correlate NEGATIVELY with the same study's CES-D. A raw
#   'If something can go wrong for me, it will' must correlate positively with
#   depression; it does not, so it is stored reversed.
sav <- ".cache/batch_303/conner.sav"
if (!file.exists(sav)) stop("missing cached deposit file: ", sav)
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")

d <- as.data.frame(irw::irw_fetch("conner_2017_lot"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_303/conner_2017_lot__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

s <- haven::read_sav(sav)
lab <- sapply(paste0("lot", 1:6), function(c) attr(s[[c]], "label"))
core <- trimws(sub("^Life Orientation Test - ", "", lab))
flag <- grepl("already reverse", core)
core <- trimws(sub("\\s*\\(already reverse [a-z]+\\)$", "", core))

cat("=== Route 1: shipped text == .sav variable labels ===\n")
sh <- unique(items[, c("item", "item_text")])
sh <- sh[order(as.integer(sub("item", "", sh$item))), ]
r1 <- all(sh$item_text == unname(core))
for (i in 1:6) cat(sprintf("  item%-2d %-62s %s\n", i, substr(core[i], 1, 62),
                           if (flag[i]) "[labelled reverse-scored]" else ""))
cat(sprintf("  -> all six match: %s\n", r1))

cat("\n=== Route 2: inter-item correlations (baseline) ===\n")
b <- d[d$wave == 0, c("id", "item", "resp")]
w <- reshape(b, idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
m <- m[, order(colnames(m))]
cm <- stats::cor(m, use = "pairwise.complete.obs")
print(round(cm, 2))
r2 <- min(cm) > 0
cat(sprintf("  -> smallest correlation %.2f; all positive: %s\n", min(cm), r2))

cat("\n=== Route 3: against CES-D depression from the same trial ===\n")
cs <- as.data.frame(irw::irw_fetch("conner_2017_cesd"))
cs <- cs[cs$wave == 0, ]
if (!nrow(cs)) stop("irw_fetch(conner_2017_cesd) returned no rows")
agg <- stats::aggregate(resp ~ id, data = cs, FUN = mean)
names(agg)[2] <- "cesd"
j <- merge(data.frame(id = w$id, m, check.names = FALSE), agg, by = "id")
rc <- sapply(colnames(m), function(c) stats::cor(j[[c]], j$cesd, use = "pairwise.complete.obs"))
print(round(rc, 3))
r3 <- all(rc < 0)
cat(sprintf("  -> every item correlates negatively with depression: %s\n", r3))
cat("  items 2, 4 and 5 are the pessimism-worded ones; stored raw they would\n")
cat("  have to correlate positively here. The shipped anchors for those three\n")
cat("  are therefore inverted relative to the .sav value labels.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Only 1, 4 and 7 were labelled on the administered scale; 2, 3, 5 and 6\n")
cat("  ship with empty option_text because the source gives them none. The\n")
cat("  four unscored LOT-R filler items were never in the data file.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")

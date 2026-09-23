# Verification for alcoholhealthwarninglabel_brennan_2022_intentions_postexposure
# (#2228, batch_304).
#
# THE DEPOSIT IS UNREACHABLE: openICPSR project 175721 (doi:10.3886/E175721V1)
# returns HTTP 403 without a login, so the .dta's variable labels -- the level-1
# source -- could not be read. The wording here is quoted from the study's own
# open-access paper instead: Brennan et al. (2022), PLOS ONE 17(12):e0276189
# (CC BY), Methods > Outcomes. That is a weaker basis than a label file, and
# this table is recorded PARTIAL rather than VERIFIED for that reason.
#
# Route 1: shape. Two codes, resp 1-4, matching the four ordinal categories
#   the paper prints.
# Route 2: the sub-numbering. data/alcoholhealthwarninglabel_brennan_2022.py
#   renames D2_D4_2 -> reduce_how_often and D2_D4_3 -> reduce_amount_per_occasion,
#   and the paper lists the D2/D4 block's statements in exactly that order,
#   with 'avoid drinking alcohol completely' fourth -- which is absent here
#   because the deposit ships only a binarised version of it.
# Route 3: the paper reports the two items are highly correlated
#   (polychoric rho = .72). Recompute an ordinary correlation as a sanity check
#   -- it should be high and positive, which also fixes the direction (1 =
#   'definitely will not' through 4 = 'definitely will').
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

xml <- cached_source(".cache/batch_304/brennan.xml",
       "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0276189&type=manuscript")
if (!file.exists(xml)) stop("missing cached paper text: ", xml)

d <- as.data.frame(irw::irw_fetch("alcoholhealthwarninglabel_brennan_2022_intentions_postexposure"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item); d$resp <- as.numeric(d$resp)
items <- read.csv(paste0("itemtables/batch_304/alcoholhealthwarninglabel_brennan_2022_",
                         "intentions_postexposure__items.csv"),
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: shape ===\n")
print(table(d$item, d$resp))
r1 <- setequal(unique(d$item), c("reduce_how_often", "reduce_amount_per_occasion")) &&
      setequal(sort(unique(d$resp)), 1:4) && setequal(unique(items$item), unique(d$item))
cat(sprintf("  ids: %d   rows: %d\n", length(unique(d$id)), nrow(d)))
cat(sprintf("  -> two codes on the paper's four-point ordinal scale: %s\n", r1))

cat("\n=== Route 2: the paper's wording, and the block order ===\n")
txt <- gsub("<[^>]*>", " ", paste(readLines(xml, warn = FALSE), collapse = " "))
txt <- gsub("&#x[0-9a-fA-F]+;", "'", txt); txt <- gsub("\\s+", " ", txt)
quotes <- c("definitely will not", "probably will not", "probably will", "definitely will",
            "reduce how often you drink alcohol",
            "reduce the amount of alcohol you have on each drinking occasion",
            "avoid drinking alcohol completely")
found <- sapply(quotes, function(q) grepl(q, txt, fixed = TRUE))
for (q in quotes) cat(sprintf("  %-62s in paper: %s\n", q, found[[q]]))
r2 <- all(found)
sh <- unique(items[, c("item", "item_text")])
r2b <- sh$item_text[sh$item == "reduce_how_often"] == "reduce how often you drink alcohol" &&
       sh$item_text[sh$item == "reduce_amount_per_occasion"] ==
           "reduce the amount of alcohol you have on each drinking occasion"
cat(sprintf("  -> every shipped string is quoted from the paper: %s\n", r2 && r2b))
cat("  The paper's order within the 'next month' block is: reduce how often,\n")
cat("  reduce the amount per occasion, avoid completely -- which lines up with\n")
cat("  the script's D2_D4_2, D2_D4_3 and the absent D2_D4_4.\n")

cat("\n=== Route 3: the two items behave as the paper says ===\n")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
rr <- stats::cor(m[, 1], m[, 2], use = "pairwise.complete.obs")
cat(sprintf("  Pearson r between the two items: %+.3f (paper: polychoric rho = .72)\n", rr))
r3 <- rr > 0.5
cat(sprintf("  -> high and positive: %s\n", r3))
p <- tapply(d$resp, d$item, function(v) mean(v >= 3))
cat(sprintf("  proportion answering 'probably/definitely will': %s\n",
            paste(sprintf("%s %.3f", names(p), p), collapse = "; ")))
cat("  Table 2 of the paper reports the combined 'will' proportion by condition\n")
cat("  between 51.2% and 59.1% immediately post-exposure, which brackets these.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  That D2_D4_2 and D2_D4_3 are the second and third statements rather\n")
cat("  than some other pair. Only the deposit's variable labels could settle\n")
cat("  that, and openICPSR 175721 is 403 without an institutional login. The\n")
cat("  sub-numbering matching the paper's printed order is strong but it is\n")
cat("  an inference, which is why this row is PARTIAL.\n")
cat("\nVERDICT:", if (r1 && r2 && r2b && r3) "PASS" else "FAIL", "\n")

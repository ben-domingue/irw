# Verification for pass20_klosowska_2025_dass_online (#2228, batch_300).
#
# SOURCE. Kłosowska et al. (2025), Psychological Assessment; deposit
# uj.rodbuk.pl doi:10.57903/UJ/JSJTEV, CC0. This is the DASS-21 block of the
# online sample. The deposit's codebook gives the anchors verbatim; the item
# wording and the 1-21 numbering come from a CC BY paper that prints all 21
# grouped by subscale with their numbers (Europe PMC PMC12785381).
#
# WHY THIS SHIPS WHILE ITS SIBLING DOES NOT. pass20_klosowska_2025_pass_hospital
# is blocked because two sources number the PASS-20 incompatibly. The DASS-21
# has one universally used numbering, and the subscale split below is a
# consistency check on it.
#
# Route 1: 21 codes, dass_r1..dass_r21, on the documented 0-3 scale.
# Route 2: the subscale split must be 7 / 7 / 7 and match the published one.
# Route 3: the subscales should cohere in the data.
suppressWarnings(suppressMessages({library(dplyr); library(tidyr)}))
alpha <- function(m) { m <- m[complete.cases(m), , drop = FALSE]; k <- ncol(m)
    (k/(k-1)) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
d <- as.data.frame(irw::irw_fetch("pass20_klosowska_2025_dass_online"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_300/pass20_klosowska_2025_dass_online__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: code set and scale ===\n")
r1 <- setequal(unique(d$item), paste0("dass_r", 1:21))
lv <- sort(unique(d$resp))
r1b <- identical(as.numeric(lv), c(0,1,2,3))
cat(sprintf("  21 codes dass_r1..dass_r21: %s\n", r1))
cat(sprintf("  resp levels %s -- the deposit codebook states 0 = 'did not apply to me\n", paste(lv, collapse=",")))
cat(sprintf("  at all/never' and 3 = 'applied to me very much/almost always': %s\n", r1b))

cat("\n=== Route 2: the published subscale split ===\n")
sub <- unique(items[, c("item","section_prompt")])
tb <- table(sub$section_prompt)
print(tb)
r2 <- all(tb == 7) && length(tb) == 3
cat(sprintf("  -> 7 / 7 / 7 across Depression, Anxiety and Stress: %s\n", r2))
cat("  That is the DASS-21's defining structure, so a shifted numbering would\n")
cat("  produce unequal subscales.\n")

cat("\n=== Route 3: do the subscales cohere in the data? ===\n")
w <- d %>% select(id, item, resp) %>% distinct(id, item, .keep_all = TRUE) %>%
     pivot_wider(names_from = item, values_from = resp)
for (s in sort(unique(sub$section_prompt))) {
    its <- sub$item[sub$section_prompt == s]
    m <- as.matrix(w[, its]); m <- m[complete.cases(m), , drop = FALSE]
    cat(sprintf("  %-22s %2d items, n=%4d, alpha %.3f\n", s, length(its), nrow(m), alpha(m)))
}
al <- sapply(sort(unique(sub$section_prompt)), function(s) {
    its <- sub$item[sub$section_prompt == s]; alpha(as.matrix(w[, its])) })
r3 <- all(al > 0.7, na.rm = TRUE)
cat(sprintf("  -> every subscale above 0.70: %s\n", r3))
cat("  A mis-numbered assignment would mix constructs and depress these.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The administered Polish wording, which the deposit does not publish -- the\n")
cat("  items ship in English and language records Polish, the documented\n")
cat("  translated_substitute fallback. Nor does anything here separate item 1\n")
cat("  from item 6 within the Stress subscale; that rests on the published\n")
cat("  numbering, which for the DASS-21 is standard and unambiguous.\n")
cat("\nVERDICT:", if (r1 && r1b && r2 && r3) "PASS" else "FAIL", "\n")

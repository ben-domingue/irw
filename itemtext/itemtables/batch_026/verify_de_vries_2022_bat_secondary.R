# verify_de_vries_2022_bat_secondary.R
#
# Claim under test: the 10 BAT secondary-symptom item codes map to the canonical
# BAT item wording as follows -- batspan01..05 are the five "psychische
# spanningsklachten" (psychological distress) items in questionnaire order, and
# batsoma01..05 are the five "psychosomatische klachten" items in questionnaire
# order (BAT Nederlandse versie, work-related form, items 1-5 and 6-10 of the
# secondary block). mapping_basis = paper_order, so the alignment is inferred and
# must be checked against the data.
#
# Three falsifiable predictions from the item CONTENT (not from the codes):
#   A. Block structure. The two prefixes should behave as two subscales: most
#      items should correlate more with their own block than with the other.
#   B. Marker items. Within each block the item naming the clinically rarest
#      complaint must be the least endorsed in a general working sample --
#      batspan04 "angstig en/of paniekaanvallen" (anxiety/panic attacks) and
#      batsoma01 "hartkloppingen of pijn in de borststreek" (palpitations/chest
#      pain). If item texts inside a block were permuted, some ordinary complaint
#      (worry, headache, muscle pain) would sit at the floor instead.
#   C. Ceiling markers. The most ubiquitous complaint in each block must be the
#      most endorsed -- batspan02 "neiging om te piekeren" (worry) and batsoma04
#      "pijnlijke spieren ... nek, schouder of rug" (neck/shoulder/back pain).

suppressMessages(library(irw))

TABLE <- "de_vries_2022_bat_secondary"
SPAN <- paste0("batspan0", 1:5, "_1")
SOMA <- paste0("batsoma0", 1:5, "_1")

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, c(SPAN, SOMA)]

## ---- A. block structure -------------------------------------------------
r <- cor(w, use = "pairwise.complete.obs")
own_best <- 0
cat("--- A. subscale block structure (mean r with own block vs other block) ---\n")
cat(sprintf("%-12s %10s %10s %6s\n", "item", "own", "other", "ok"))
for (it in c(SPAN, SOMA)) {
    own_g <- if (it %in% SPAN) SPAN else SOMA
    oth_g <- if (it %in% SPAN) SOMA else SPAN
    own <- mean(r[it, setdiff(own_g, it)])
    oth <- mean(r[it, oth_g])
    ok <- own > oth
    own_best <- own_best + ok
    cat(sprintf("%-12s %10.2f %10.2f %6s\n", it, own, oth, if (ok) "yes" else "NO"))
}
cat(sprintf("%d/10 items load strongest on their own block\n\n", own_best))

## ---- B/C. marker items --------------------------------------------------
m <- tapply(d$resp, d$item, mean)
fl <- tapply(d$resp, d$item, function(x) 100 * mean(x == 1))
cat("--- B/C. per-item mean and %-at-floor ---\n")
cat(sprintf("%-12s %6s %8s  %s\n", "item", "mean", "floor%", "content"))
lab <- c(batspan01_1 = "trouble sleeping", batspan02_1 = "tend to worry",
         batspan03_1 = "tense and stressed", batspan04_1 = "anxious / panic attacks",
         batspan05_1 = "noise and crowds", batsoma01_1 = "palpitations / chest pain",
         batsoma02_1 = "stomach / intestinal", batsoma03_1 = "headaches",
         batsoma04_1 = "muscle pain neck/shoulder/back", batsoma05_1 = "often get sick")
for (it in c(SPAN, SOMA))
    cat(sprintf("%-12s %6.2f %8.1f  %s\n", it, m[it], fl[it], lab[it]))

min_span <- names(which.min(m[SPAN])); max_span <- names(which.max(m[SPAN]))
min_soma <- names(which.min(m[SOMA])); max_soma <- names(which.max(m[SOMA]))
cat(sprintf("\nlowest / highest batspan: %s / %s   (predicted batspan04_1 / batspan02_1)\n",
            min_span, max_span))
cat(sprintf("lowest / highest batsoma: %s / %s   (predicted batsoma01_1 / batsoma04_1)\n",
            min_soma, max_soma))

markers <- min_span == "batspan04_1" && max_span == "batspan02_1" &&
           min_soma == "batsoma01_1" && max_soma == "batsoma04_1"

cat("\nNote: this does NOT establish the order of the three middle psychological-\n",
    "distress items -- batspan01_1 (2.36), batspan03_1 (2.38) and batspan05_1 (2.37)\n",
    "have means within 0.02 of each other and no published per-item statistics exist\n",
    "for this sample, so a permutation among those three would be undetectable here.\n",
    "The status recorded for this table is therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (own_best >= 8 && markers) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

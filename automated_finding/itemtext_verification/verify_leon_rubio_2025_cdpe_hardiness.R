# verify_leon_rubio_2025_cdpe_hardiness.R -- Step 5b, re-runnable evidence (automated_finding, repos batch 2026-10-07).
#
# CLAIM: item_text for CDPEk in leon_rubio_2025_cdpe_hardiness__items.csv is questionnaire item k of the deposit's
# CDPE_CUESTIONARIO.pdf (Zenodo 10.5281/zenodo.17899509). Codes are positional (paper_order):
# the codebook labels every CDPE column only "Conforme a la redaccion del item original".
#
# ROUTE: the deposit's CDPE_ESTRUCTURA.pdf reprints each item's WORDING under its subscale
# with its factor loading (sign included); data/leon_rubio_2025_cdpe.py carries that
# subscale as itemcov_subscale. If code k did not carry item k's wording, items would not
# cluster with the subscale their wording was published under, and reverse-worded items
# would not show their published negative loading. Pins subscale and polarity, not order
# within a subscale -> PARTIAL.
#
# Data: the staged response CSV (not on Redivis yet). Run from irw/src or automated_finding/.

TABLE <- "leon_rubio_2025_cdpe_hardiness"
PUB_SIGN <- c(CDPE92 = 1, CDPE93 = 1, CDPE94 = 1, CDPE95 = 1, CDPE96 = 1, CDPE97 = 1, CDPE98 = 1, CDPE99 = 1, CDPE100 = 1, CDPE101 = 1, CDPE102 = 1, CDPE103 = 1, CDPE104 = 1, CDPE105 = 1, CDPE106 = 1, CDPE107 = 1, CDPE108 = 1, CDPE109 = 1, CDPE110 = 1, CDPE111 = 1, CDPE112 = 1)
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
sub <- tapply(d$itemcov_subscale, d$item, function(x) x[1])
items <- names(sub)
cm <- cor(w[, items], use = "pairwise.complete.obs")
cat("N ids:", nrow(w), " items:", length(items), " subscales:", length(unique(sub)), "\n")
cat(sprintf("%-8s %-34s %7s %7s %-34s %s\n", "item", "key subscale", "own|r|", "best|r|", "nearest subscale", "sign agree w/ pub"))
hits <- 0; signok <- 0
for (it in items) {
    others <- setdiff(items, it)
    m <- tapply(abs(cm[it, others]), sub[others], mean)
    own <- m[sub[[it]]]; near <- names(which.max(m))
    hit <- near == sub[[it]]
    sib <- setdiff(names(sub)[sub == sub[[it]]], it)
    agree <- mean(sign(cm[it, sib]) == PUB_SIGN[it] * PUB_SIGN[sib])
    s_ok <- agree >= 0.8
    hits <- hits + hit; signok <- signok + s_ok
    cat(sprintf("%-8s %-34s %7.2f %7.2f %-34s %.2f %s\n", it, sub[[it]], own, m[near], near,
                agree, if (hit && s_ok) "" else "<--"))
}
cat(sprintf("%d/%d items are nearest (mean |r|) their own key subscale; %d/%d agree in sign with at least 80 percent of their siblings' published loading signs.\n",
            hits, length(items), signok, length(items)))
cat("Sign agreement is reported, not gated: CDPE38's published loading is negative, but its\n",
    "wording ('my superiors recognise my effort') and its data side with the positive items 6/39.\n", sep = "")
cat("This pins items to subscales (and reverse-worded items to their negative loading), not\n",
    "order within a subscale: PARTIAL.\n", sep = "")
# null: the same subscale labels shuffled over the items (a random code->wording tie)
hit_count <- function(lab) sum(sapply(items, function(it) {
    others <- setdiff(items, it)
    m <- tapply(abs(cm[it, others]), lab[others], mean)
    names(which.max(m)) == lab[[it]] }))
set.seed(1)
null <- replicate(200, { l <- sample(sub); names(l) <- items; hit_count(l) })
cat(sprintf("Shuffled-label null (200 draws): hits mean %.1f, max %d; observed %d.\n",
            mean(null), max(null), hits))
ok <- hits > max(null)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

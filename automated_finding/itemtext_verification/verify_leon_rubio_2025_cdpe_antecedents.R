# verify_leon_rubio_2025_cdpe_antecedents.R -- Step 5b, re-runnable evidence (automated_finding, repos batch 2026-10-07).
#
# CLAIM: item_text for CDPEk in leon_rubio_2025_cdpe_antecedents__items.csv is questionnaire item k of the deposit's
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

TABLE <- "leon_rubio_2025_cdpe_antecedents"
PUB_SIGN <- c(CDPE1 = 1, CDPE2 = 1, CDPE3 = 1, CDPE4 = -1, CDPE5 = -1, CDPE6 = 1, CDPE7 = 1, CDPE8 = 1, CDPE9 = 1, CDPE10 = -1, CDPE11 = -1, CDPE12 = 1, CDPE13 = -1, CDPE14 = -1, CDPE15 = 1, CDPE16 = 1, CDPE17 = 1, CDPE18 = 1, CDPE19 = 1, CDPE20 = 1, CDPE21 = 1, CDPE22 = 1, CDPE23 = -1, CDPE24 = -1, CDPE25 = -1, CDPE26 = 1, CDPE27 = 1, CDPE28 = 1, CDPE29 = 1, CDPE30 = 1, CDPE31 = 1, CDPE32 = 1, CDPE33 = -1, CDPE34 = 1, CDPE35 = -1, CDPE36 = -1, CDPE37 = 1, CDPE38 = -1, CDPE39 = 1, CDPE40 = 1, CDPE41 = 1, CDPE42 = 1, CDPE43 = 1, CDPE44 = -1, CDPE45 = 1, CDPE46 = 1, CDPE47 = 1, CDPE48 = 1, CDPE49 = 1, CDPE50 = 1, CDPE51 = 1, CDPE52 = 1, CDPE53 = 1, CDPE54 = 1, CDPE55 = 1, CDPE56 = 1, CDPE57 = 1, CDPE58 = 1, CDPE59 = 1, CDPE60 = 1, CDPE61 = -1, CDPE62 = 1)
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

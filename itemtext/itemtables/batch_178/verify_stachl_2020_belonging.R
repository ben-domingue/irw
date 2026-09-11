# verify_stachl_2020_belonging.R -- Step 5b check for batch_178.
#
# Claim: item codes (the S2 .xlsx column descriptors, e.g. "Better Grades") map to the
# cartoon narratives transcribed from S1 Text Fig A1, per S1 Table A (GP n / Descriptor /
# Narrative); Low-SB items are stored already inversely scored (Table 1), so for them
# resp 4 = "Do Not Relate".
#
# Routes:
#  (1) Refit the paper's partial credit model (ConQuest, constraints=cases) with mirt and
#      compare each item's location with S1 Table D. Falsifiable: permuting codes, or
#      storing a Low-SB item raw, moves the locations far off.
#  (2) Every pairwise swap of Table D values must fit worse than the shipped mapping.
#  (3) Polarity: each Low-SB item's mean correlation with the High-SB items must be > 0
#      (only possible if the Low-SB items are already reversed).
#  (4) Shipped CSV: each descriptor's keyword occurs in its own item_text and in no
#      other item's; Low-SB items carry "Do Not Relate" at resp 4, High-SB at resp 0.
suppressMessages({library(irw); library(mirt)})
TABLE <- "stachl_2020_belonging"
ok <- TRUE

ord <- c("Better Grades","Smart Enough","Hardships","Social Support","Happy","Teaching",
         "Productive","Scholar","Group","Hall","Outsider","Value","Independent")
low <- c("Better Grades","Smart Enough","Hardships","Teaching","Productive","Outsider")
# S1 Text Table D, item difficulties (logits), GP 1..GP 13
tabD <- c(0.185, 0.188, -0.019, -0.345, -0.115, -1.283, 0.662, -0.289, -1.150, 0.490, -0.227, -0.308, 0.067)
names(tabD) <- ord

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id","item","resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, ord]

m <- mirt(X, 1, itemtype = "Rasch", verbose = FALSE)
cf <- coef(m, IRTpars = FALSE, simplify = TRUE)$items
loc <- -cf[ord, "d4"] / 4                       # PCM item location = mean step difficulty
loc <- loc - mean(loc) + mean(tabD)             # align origin
cat("(1) PCM item location vs S1 Table D\n")
cat(sprintf("%-15s %8s %8s %8s\n", "item", "TableD", "refit", "diff"))
for (i in ord) cat(sprintf("%-15s %8.3f %8.3f %8.3f\n", i, tabD[i], loc[i], loc[i] - tabD[i]))
worst <- max(abs(loc - tabD)); cat(sprintf("largest deviation %.4f (tol 0.02)\n", worst))
if (worst > 0.02) ok <- FALSE

ssd0 <- sum((loc - tabD)^2); nworse <- 0; minpen <- Inf; minpair <- ""
for (a in 1:12) for (b in (a+1):13) {
  t2 <- tabD; t2[c(a,b)] <- tabD[c(b,a)]
  s <- sum((loc - t2)^2)
  if (s > ssd0) nworse <- nworse + 1
  if (s - ssd0 < minpen) { minpen <- s - ssd0; minpair <- paste(ord[a], "<->", ord[b]) }
}
cat(sprintf("\n(2) %d of 78 pairwise swaps fit worse than shipped (SSD %.6f); weakest swap %s adds %.6f\n",
            nworse, ssd0, minpair, minpen))
if (nworse != 78) ok <- FALSE

R <- cor(X, use = "pairwise")
high <- setdiff(ord, low)
pol <- sapply(low, function(i) mean(R[i, high]))
cat("\n(3) mean r of each Low-SB item with the 7 High-SB items:\n"); print(round(pol, 3))
if (any(pol <= 0)) ok <- FALSE

f <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
csv <- file.path(dirname(normalizePath(f)), paste0(TABLE, "__items.csv"))
it <- read.csv(csv, stringsAsFactors = FALSE)
kw <- c("Better Grades"="better grades","Smart Enough"="smart enough","Hardships"="hardships",
        "Social Support"="supportive social network","Happy"="happy","Teaching"="teaching",
        "Productive"="productive and scientifically","Scholar"="scholar","Group"="rest of my group",
        "Hall"="across the hall","Outsider"="outsider","Value"="values my ideas","Independent"="independent")
txt <- tapply(it$item_text, it$item, `[`, 1)
cat("\n(4) descriptor keyword -> item_text hits (own / other items)\n")
for (i in ord) {
  own <- grepl(kw[i], txt[i], ignore.case = TRUE)
  other <- sum(grepl(kw[i], txt[setdiff(ord, i)], ignore.case = TRUE))
  cat(sprintf("%-15s %-30s own=%s other=%d\n", i, kw[i], own, other))
  if (!own || other > 0) ok <- FALSE
}
top <- sapply(ord, function(i) it$option_text[it$item == i & it$resp == 4])
exp4 <- ifelse(ord %in% low, "Do Not Relate", "Always Relate")
cat("resp=4 anchors match Table 1 direction:", sum(top == exp4), "of 13\n")
if (any(top != exp4)) ok <- FALSE

cat("Does NOT establish: route (1)/(2) separates Better Grades vs Smart Enough by only 0.003 logits;\n",
    "that pair is separated by the descriptor labels (route 4), not by the statistics.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

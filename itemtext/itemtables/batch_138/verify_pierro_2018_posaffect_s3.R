# Step 5b re-runnable evidence for pierro_2018_posaffect_s3 (mapping_basis = reconstructed).
#
# THE CLAIM: posaffect1..posaffect10 are the ten Positive Affect adjectives of the
# Watson, Clark & Tellegen (1988) PANAS, numbered in the instrument's canonical
# printed order -- interested, excited, strong, enthusiastic, proud, alert,
# inspired, determined, attentive, active (canonical 20-item positions
# 1,3,5,9,10,12,14,16,17,19).
#
# WHY IT NEEDS CHECKING: the deposit (S3 File, SPSS .sav) carries NO variable
# labels on any item column and only one value label in the whole file (gender),
# and the paper prints only three of the ten adjectives as examples. Nothing in
# the source ties posaffectN to an adjective.
#
# WHAT THESE CHECKS ESTABLISH
#   1/2. The ten codes ARE the Positive Affect subscale as the study itself scored
#        it, stored RAW (no item reverse-recoded): the deposit's own `posaffect`
#        composite is the plain unweighted mean of exactly these ten columns, and
#        that mean reproduces the paper's published M/SD/alpha for Study 3.
#   3.   The file numbers items WITHIN a valence block in canonical PANAS order.
#        Tested on the sibling negative block of the SAME .sav, where canonical
#        numbering makes two falsifiable extreme predictions for a self-committed
#        transgression recall: negaffect7 = "ashamed" must be the most endorsed
#        adjective and negaffect5 = "hostile" the least. The rival hypothesis
#        (the twenty adjectives numbered alphabetically in Italian) predicts the
#        opposite -- ostile 7th of 10 alphabetically would be the max and
#        vergognoso the last.
#
# WHAT THIS DOES **NOT** ESTABLISH: nothing here distinguishes one POSITIVE
# adjective from another. Swapping the text of posaffect1 (interested) and
# posaffect3 (strong) would leave every number below unchanged. Check 4 prints the
# within-block means and the one pattern that sits oddly under the canonical
# reading (alert 3.53 vs attentive 1.64, near-synonyms 1.9 apart); it is printed
# as a caveat, not as support, and does not enter the verdict.

suppressMessages(library(irw))

TABLE <- "pierro_2018_posaffect_s3"
POS <- paste0("posaffect", 1:10)
NEGADJ <- c("distressed","upset","guilty","scared","hostile","irritable",
            "ashamed","nervous","jittery","afraid")   # canonical NA order
POSADJ <- c("interested","excited","strong","enthusiastic","proud","alert",
            "inspired","determined","attentive","active")

# Published, Pierro et al. 2018 PLOS ONE 13(3):e0193357, Study 3 (Table 3 + Measures).
PUB_M <- 2.61; PUB_SD <- 0.72; PUB_ALPHA <- 0.83

## ---- source deposit: S3 File (.sav) ----------------------------------------
sav <- file.path(tempdir(), "pierro_s003.sav")
ok <- tryCatch({
  download.file("https://doi.org/10.1371/journal.pone.0193357.s003",
                sav, quiet = TRUE, mode = "wb"); TRUE
}, error = function(e) FALSE)
if (!ok || !file.exists(sav)) { cat("could not fetch S3 File\nVERDICT: FAIL\n"); quit(status = 0) }
src <- as.data.frame(haven::read_sav(sav))

alpha <- function(X) { k <- ncol(X); (k/(k-1)) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }

## ---- CHECK 1: the study's own composite, in the SOURCE file ----------------
pm <- rowMeans(src[, POS])
d1 <- max(abs(pm - src$posaffect))
a  <- alpha(src[, POS])
cat("CHECK 1 -- deposit's own `posaffect` composite vs plain mean of posaffect1..10\n")
cat(sprintf("  max |rowMeans(posaffect1..10) - posaffect| over %d cases : %.4f\n", nrow(src), d1))
cat(sprintf("  mean %.3f (paper %.2f) | SD %.3f (paper %.2f) | alpha %.3f (paper %.2f)\n",
            mean(pm), PUB_M, sd(pm), PUB_SD, a, PUB_ALPHA))
cat("  (an item stored reverse-recoded, or a wrong column in the block, breaks all three)\n")
c1 <- d1 < 1e-9 && abs(mean(pm) - PUB_M) < 0.01 && abs(sd(pm) - PUB_SD) < 0.01 &&
      abs(a - PUB_ALPHA) < 0.01

## ---- CHECK 2: same identity from the LIVE table's posaffect* codes ----------
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp[.]", "", names(w))
live <- data.frame(id = as.character(w$id), lm = rowMeans(w[, POS]))
ref  <- data.frame(id = as.character(as.integer(src$subject)), comp = src$posaffect)
mg <- merge(live, ref, by = "id"); mg <- mg[complete.cases(mg), ]
m2 <- sum(abs(mg$lm - mg$comp) < 1e-9)
cat("\nCHECK 2 -- LIVE posaffect1..10 reproduce the deposit's composite\n")
cat(sprintf("  matched respondents %d ; exact %d / %d\n", nrow(mg), m2, nrow(mg)))
c2 <- nrow(mg) > 70 && m2 >= nrow(mg) - 1   # one cell (posaffect9 = 6) is out of range and dropped

## ---- CHECK 3: numbering convention, tested on the sibling negative block ----
nm <- colMeans(src[, paste0("negaffect", 1:10)], na.rm = TRUE)
names(nm) <- NEGADJ
cat("\nCHECK 3 -- canonical numbering tested on the SAME file's negative block\n")
for (i in order(-nm)) cat(sprintf("  negaffect%-2d %-11s %.2f\n", i, NEGADJ[i], nm[i]))
top <- names(nm)[which.max(nm)]; bot <- names(nm)[which.min(nm)]
cat(sprintf("  predicted max 'ashamed'  -> observed max '%s' (%.2f)\n", top, max(nm)))
cat(sprintf("  predicted min 'hostile'  -> observed min '%s' (%.2f)\n", bot, min(nm)))
cat("  rival (alphabetical-Italian) hypothesis would put 'ostile' at the max: refuted\n")
c3 <- top == "ashamed" && bot == "hostile"

## ---- CHECK 4: within-positive-block means -- CAVEAT ONLY, not evidence ------
pmn <- colMeans(src[, POS], na.rm = TRUE); names(pmn) <- POSADJ
cat("\nCHECK 4 (caveat, not part of the verdict) -- positive-block means under the canonical reading\n")
for (i in order(-pmn)) cat(sprintf("  posaffect%-2d %-13s %.2f\n", i, POSADJ[i], pmn[i]))
cat("  NOTE: 'alert' 3.53 vs 'attentive' 1.64 -- near-synonyms 1.9 apart. Nothing in the\n")
cat("  source distinguishes the positive adjectives, so within-block order rests on the\n")
cat("  canonical printed order alone. Step 5b status is PARTIAL for exactly this reason.\n")

cat(sprintf("\nchecks: composite=%s live=%s convention=%s\n", c1, c2, c3))
cat(if (c1 && c2 && c3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

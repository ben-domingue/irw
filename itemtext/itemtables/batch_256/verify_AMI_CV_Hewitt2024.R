# verify_AMI_CV_Hewitt2024.R -- Step 5b check for the AMI_CV_Hewitt2024 item-text mapping.
#
# Claim: live item AMI_CV_N carries the wording of row N of Supplementary Table 1
# (Hewitt, Habicht et al. 2024, OSF dukhj AMI_CV_supplement_v2.docx), and row N's
# subscale (BA / SM / ES, the table's second column) is the subscale of AMI_CV_N.
#
# Route 3 (published subscale totals): the authors' deposited combined_data.csv
# (OSF zwsdq, https://osf.io/download/sbhdc/) carries their own computed
# AMICV_behavioural / _social / _emotional scores (Sample 1 = sums, Sample 2 = means).
# We (a) check the live IRW responses equal that file cell for cell, then (b) rebuild
# each subscale score from the LIVE items using Supplementary Table 1's subscale
# column and compare with the authors' scores.
#
# What this does NOT establish: order WITHIN a subscale. Swapping the text of two
# items in the same subscale (e.g. AMI_CV_9 and AMI_CV_12, both BA) would still pass.
# Within-subscale identity rests on Supplementary Table 1's 1-18 numbering (documentary).
suppressMessages(library(irw))
TABLE <- "AMI_CV_Hewitt2024"

SUBSCALE <- c(`1`="ES",`2`="SM",`3`="SM",`4`="SM",`5`="BA",`6`="ES",`7`="ES",`8`="SM",`9`="BA",
              `10`="BA",`11`="BA",`12`="BA",`13`="ES",`14`="SM",`15`="BA",`16`="ES",`17`="SM",`18`="ES")
SCORE <- c(BA="AMICV_behavioural", SM="AMICV_social", ES="AMICV_emotional")

src <- read.csv("https://osf.io/download/sbhdc/")
live <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(live[, c("id","item","resp")], idvar="id", timevar="item", direction="wide")
names(w) <- sub("^resp\\.", "", names(w))
m <- merge(w, src, by.x="id", by.y="userID", suffixes=c("", ".src"))
cat("persons live:", nrow(w), " matched to source userID:", nrow(m), "\n")

# (a) live == source, cell for cell
items <- paste0("AMI_CV_", 1:18)
cell_ok <- sum(sapply(items, function(i) {
  a <- m[[i]]; b <- m[[paste0(i, ".src")]]
  sum(mapply(function(x, y) (is.na(x) && is.na(y)) || (!is.na(x) && !is.na(y) && x == y), a, b))
}))
cat("(a) live vs source cells equal:", cell_ok, "/", nrow(m) * 18, "\n")

# (b) rebuild subscale scores from LIVE items
agg <- function(v) ifelse(m$Sample == 1, rowSums(as.matrix(m[, v, drop=FALSE])),
                          rowMeans(as.matrix(m[, v, drop=FALSE])))
res_ok <- TRUE
for (s in names(SCORE)) {
  v <- paste0("AMI_CV_", names(SUBSCALE)[SUBSCALE == s])
  x <- agg(v); y <- m[[SCORE[s]]]; ok <- !is.na(x) & !is.na(y)
  dev <- max(abs(x[ok] - y[ok]))
  cat(sprintf("(b) %s items {%s}: reproduced %d/%d persons, max |diff| = %.2e\n",
              s, paste(sub("AMI_CV_", "", v), collapse=","), sum(abs(x[ok]-y[ok]) < 1e-6), sum(ok), dev))
  if (dev > 1e-6) res_ok <- FALSE
}

# (c) discrimination: moving any single item to either other subscale must break reproduction
still <- 0
for (i in names(SUBSCALE)) for (s2 in setdiff(names(SCORE), SUBSCALE[i])) {
  sub2 <- SUBSCALE; sub2[i] <- s2; allok <- TRUE
  for (s in names(SCORE)) {
    v <- paste0("AMI_CV_", names(sub2)[sub2 == s]); x <- agg(v); y <- m[[SCORE[s]]]
    ok <- !is.na(x) & !is.na(y); if (max(abs(x[ok]-y[ok])) > 1e-6) allok <- FALSE
  }
  if (allok) still <- still + 1
}
cat("(c) single-item subscale reassignments (36 tried) that still reproduce:", still, "\n")

# (d) direction sanity: 0 = 'Completely TRUE'. Prosocial ES items should sit near 0.
for (i in c("AMI_CV_16","AMI_CV_18","AMI_CV_3")) {
  r <- live$resp[live$item == i]
  cat(sprintf("(d) %s mean %.2f, %%at 0 = %.1f\n", i, mean(r, na.rm=TRUE), 100*mean(r == 0, na.rm=TRUE)))
}
cat("Not established: order within a subscale (see header).\n")
pass <- res_ok && still == 0 && cell_ok == nrow(m) * 18
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

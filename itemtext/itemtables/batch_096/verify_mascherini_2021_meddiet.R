# verify_mascherini_2021_meddiet.R
#
# WHAT IS BEING VERIFIED. The item axis needs no inference: data/mascherini_2021_meddiet.py
# melts the S1 File XLSX's own headers ("Red meat" -> red_meat), so the IRW code IS the
# source column name and mapping_basis is data_labels. What DID carry inference is the
# OTHER axis -- option_text <-> resp. The ABITUD-19 questionnaire (S2 File) prints six
# frequency bands per food group in ascending order of consumption; the shipped table maps
# them 0..5 ascending for the eight "close to the pattern" foods and 5..0 (reversed) for
# red meat, white meat, dairy products and alcohol. This script tests that direction, plus
# the item<->text correspondence against the paper's published per-item means.
#
# The falsifiable prediction: if the stored 0-5 values were raw consumption levels rather
# than pyramid-direction scores, their per-respondent sum could not equal the published
# Med Diet Score (31.0 +/- 4.1), because four of eleven items would be running backwards.

suppressMessages(library(irw))

TABLE <- "mascherini_2021_meddiet"

# Mascherini et al. 2021, PLOS ONE 16(5):e0252395, Table 2 (image; read directly).
# "Data are shown in a score range from 0 to 5 according to their position in the
#  Mediterranean diet pyramid. The Med Diet Score is the sum of all items in the same column."
ITEMS   <- c("grains","potatoes","fruits","vegetables","legumes","fish",
             "red_meat","white_meat","dairy","oil","alchool")
LABEL   <- c("Cereals","Potatoes","Fruits","Vegetables","Legumes","Fish",
             "Red meat","White meat","Dairy products","Olive oil","Alcohol")
PUB_W1  <- c(1.7, 1.0, 2.4, 2.5, 2.0, 1.7, 3.4, 3.7, 4.1, 3.7, 4.8)   # before confinement
PUB_W2  <- c(1.9, 1.1, 2.5, 2.5, 1.9, 1.7, 3.5, 3.7, 4.0, 3.7, 4.7)   # during confinement
PUB_TOT <- c(31.0, 4.1)                                               # Med Diet Score, before
TOL_ITEM <- 0.05   # published to 1 dp
TOL_MEAN <- 0.05
TOL_SD   <- 0.10

# Reversed items under the shipped mapping, and the option each *would* be modal on if the
# direction were flipped -- printed so a reader can judge the implausibility for themselves.
SHIPPED_MODE <- c(grains="1-6", potatoes="1-4", fruits="9-15", vegetables="13-20",
                  legumes="1-2", fish="1-2", red_meat="2-3", white_meat="2-3",
                  dairy="<10", oil="Daily", alchool="<300")
FLIPPED_MODE <- c(grains="19-31", potatoes="13-18", fruits="5-8", vegetables="7-12",
                  legumes="3-4", fish="3-4", red_meat="4-5", white_meat="8-10",
                  dairy="> 30", oil="Never", alchool="> 700")

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

m1 <- tapply(d$resp[d$wave == 1], d$item[d$wave == 1], mean)[ITEMS]
m2 <- tapply(d$resp[d$wave == 2], d$item[d$wave == 2], mean)[ITEMS]

cat("=== A. per-item means vs paper Table 2 (score scale 0-5) ===\n")
cat(sprintf("%-11s %-15s %6s %6s %7s | %6s %6s %7s\n",
            "item","paper label","pubW1","obsW1","diff","pubW2","obsW2","diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-11s %-15s %6.1f %6.2f %7.3f | %6.1f %6.2f %7.3f\n",
                ITEMS[i], LABEL[i], PUB_W1[i], m1[i], m1[i]-PUB_W1[i],
                PUB_W2[i], m2[i], m2[i]-PUB_W2[i]))
worst_item <- max(abs(c(m1 - PUB_W1, m2 - PUB_W2)))
cat(sprintf("largest per-item deviation: %.3f (tolerance %.2f)\n\n", worst_item, TOL_ITEM))

cat("=== B. Med Diet Score total: does the sum of the 11 stored items reproduce it? ===\n")
w <- reshape(as.data.frame(d[d$wave == 1, c("id","item","resp")]), idvar = "id",
             timevar = "item", direction = "wide")
tot <- rowSums(w[, paste0("resp.", ITEMS)])
cat(sprintf("observed  wave 1 total: mean %.2f  sd %.2f  range %d-%d  n %d\n",
            mean(tot), sd(tot), min(tot), max(tot), length(tot)))
cat(sprintf("published wave 1 total: mean %.1f  sd %.1f  (Table 2, 'Med Diet Score')\n",
            PUB_TOT[1], PUB_TOT[2]))
# What the same sum would be if red_meat/white_meat/dairy/alchool were stored as RAW
# consumption level rather than reverse-scored -- i.e. if the shipped option mapping for
# those four items were flipped.
REV <- c("red_meat","white_meat","dairy","alchool")
tot_flip <- tot - rowSums(w[, paste0("resp.", REV)]) + rowSums(5 - w[, paste0("resp.", REV)])
cat(sprintf("same sum with the four reversed items flipped: mean %.2f (would miss by %.1f)\n\n",
            mean(tot_flip), abs(mean(tot_flip) - PUB_TOT[1])))

cat("=== C. modal response option under the shipped vs flipped mapping ===\n")
cat(sprintf("%-11s %6s %5s%%  %-9s %-9s\n","item","mode","pct","shipped","if flipped"))
for (it in ITEMS) {
    v  <- d$resp[d$item == it]
    tb <- table(v); md <- names(tb)[which.max(tb)]
    cat(sprintf("%-11s %6s %5.1f%%  %-9s %-9s\n",
                it, md, 100*max(tb)/length(v), SHIPPED_MODE[it], FLIPPED_MODE[it]))
}

cat("\nWhat this does NOT establish: (a) three pairs of items tie at the published 1-dp mean\n",
    "(grains/fish at 1.7, white_meat/oil at 3.7, fruits/vegetables at 2.5 in wave 2), so the\n",
    "means alone cannot separate those pairs -- the item codes being the source column names\n",
    "verbatim is what does; (b) it pins the DIRECTION of each item's option scale, not which\n",
    "frequency band each intermediate level is, which rests on the printed order of the six\n",
    "options in the S2 File questionnaire.\n", sep = "")

ok <- worst_item <= TOL_ITEM &&
      abs(mean(tot) - PUB_TOT[1]) <= TOL_MEAN &&
      abs(sd(tot)   - PUB_TOT[2]) <= TOL_SD
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_thomeczek2025_les.R -- Step 5b check for thomeczek2025_les (batch_421).
#
# ITEM AXIS: the codebook (codebook_EN_hh.pdf, Harvard Dataverse doi:10.7910/DVN/VFTK3K)
# prints every question under a heading that IS the data column name, and
# data/thomeczek2025_les.py melts those columns by name with no rename; the codes are
# also self-describing (asylum, ukraine, rentcontrol ...). That is a label match, not
# an inference, and it is what distinguishes every item from every other.
#
# What this script tests is the OTHER axis, which the label match does not cover:
# that option_text "1: <pole A>" / "20: <pole B>" points the right way for each item.
# Prediction: on each item the party whose platform is known to sit at a pole sits at
# that end of the 1-20 scale. Pairs: AfD vs Greens for every item; FDP vs Linke added
# for the four economic items. Expected signs are derived from the shipped pole labels.
# A reversed pole label (or two items of opposite polarity swapped) flips a sign.
#
# NOT established: order among items whose expected sign agrees (that rests on the
# label match above), or the wording of the German administration.

suppressMessages(library(irw))
TABLE <- "thomeczek2025_les"
d <- irw::irw_fetch(TABLE)
d$party <- sub("_.*", "", d$id)

# expected sign of mean(AfD) - mean(Greens), from the shipped pole labels
exp_ag <- c(leftrightgeneral=+1, lrecon=+1, galtan=+1, genderlanguage=-1, genderroles=-1,
            childcare=+1, communityschool=+1, antielitism=+1, peoplecentrism=+1,
            publicdebt=+1, migrantbenefit=-1, assimilation=-1, liberalism=+1,
            climatepolicy=+1, immigration=+1, lawandorder=+1, asylum=+1,
            rentcontrol=-1, ukraine=+1, publicbroadcast=-1)
# expected sign of mean(FDP) - mean(Linke), economic items
exp_fl <- c(lrecon=+1, publicdebt=+1, rentcontrol=-1, childcare=+1)

m <- tapply(d$resp, list(d$item, d$party), mean, na.rm = TRUE)
ok <- TRUE
cat(sprintf("%-17s %6s %6s %7s %4s\n", "item", "AfD", "Greens", "diff", "exp"))
for (it in names(exp_ag)) {
  df <- m[it, "afd"] - m[it, "greens"]
  pass <- sign(df) == exp_ag[[it]] && abs(df) >= 3
  ok <- ok && pass
  cat(sprintf("%-17s %6.2f %6.2f %7.2f %4s %s\n", it, m[it,"afd"], m[it,"greens"], df,
              ifelse(exp_ag[[it]] > 0, "+", "-"), ifelse(pass, "ok", "FAIL")))
}
cat(sprintf("\n%-17s %6s %6s %7s %4s\n", "item", "FDP", "Linke", "diff", "exp"))
for (it in names(exp_fl)) {
  df <- m[it, "fdp"] - m[it, "linke"]
  pass <- sign(df) == exp_fl[[it]] && abs(df) >= 3
  ok <- ok && pass
  cat(sprintf("%-17s %6.2f %6.2f %7.2f %4s %s\n", it, m[it,"fdp"], m[it,"linke"], df,
              ifelse(exp_fl[[it]] > 0, "+", "-"), ifelse(pass, "ok", "FAIL")))
}
cat("\nNote: pins the pole direction per item (option_text <-> resp) and rules out swaps\n",
    "between opposite-polarity items; item identity itself rests on the codebook's\n",
    "variable-name headings, not on this test.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

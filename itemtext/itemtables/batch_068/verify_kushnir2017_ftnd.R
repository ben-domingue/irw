# verify_kushnir2017_ftnd.R -- Step 5b, route 9 (response-frequency matching).
#
# mapping_basis is data_labels on the item axis: the live `item` values ARE the
# source .xlsx column headers verbatim, so item_text (the same header with the
# "(FTND_n)" code prefix stripped) cannot be permuted. Nothing to verify there.
#
# The axis that DID carry a decision is option_text <-> resp. The raw file stores
# text labels ("Within 5 minutes", "Yes", "11 - 20"); the live table stores
# integers 0-3. data/kushnir2017_smoking_cessation.py declares the label->integer
# map (FTND_ITEM_MAPS); this script checks that declared map against the data by
# counting each label in the raw deposit and each integer in the live table.
# A flipped direction or any permuted level breaks the cell-for-cell match.

suppressMessages(library(irw))

TABLE <- "kushnir2017_ftnd"
XLSX_URL <- "https://dataverse.harvard.edu/api/access/datafile/3059090"  # CC0, doi:10.7910/DVN/8LBLYS

# Label counts in the raw Harvard Dataverse .xlsx (N=319), transcribed here so the
# script runs offline; re-derive with readxl::read_excel() on the URL above.
RAW <- list(
  "(FTND_1)" = c("After 60 minutes"=27, "31 - 60 minutes"=54, "6 - 30 minutes"=148, "Within 5 minutes"=90),
  "(FTND_2)" = c("No"=170, "Yes"=149),
  "(FTND_3)" = c("Any other"=111, "The first one in the morning"=208),
  "(FTND_4)" = c("10 or less"=64, "11 - 20"=183, "21 - 30"=53, "31 or more"=19),
  "(FTND_5)" = c("No"=181, "Yes"=138),
  "(FTND_6)" = c("No"=126, "Yes"=193)
)
# resp value each label is shipped against in kushnir2017_ftnd__items.csv
RESP <- list(
  "(FTND_1)" = c(0, 1, 2, 3), "(FTND_2)" = c(0, 1), "(FTND_3)" = c(0, 1),
  "(FTND_4)" = c(0, 1, 2, 3), "(FTND_5)" = c(0, 1), "(FTND_6)" = c(0, 1)
)

d <- irw::irw_fetch(TABLE)
ok <- TRUE
cat(sprintf("%-9s %-30s %5s %8s %8s\n", "item", "option_text", "resp", "raw_n", "live_n"))
for (code in names(RAW)) {
  it <- grep(code, unique(d$item), fixed = TRUE, value = TRUE)
  stopifnot(length(it) == 1)
  sub <- d[d$item == it, ]
  for (j in seq_along(RAW[[code]])) {
    lab <- names(RAW[[code]])[j]; rn <- RAW[[code]][[j]]; rv <- RESP[[code]][j]
    ln <- sum(sub$resp == rv)
    if (ln != rn) ok <- FALSE
    cat(sprintf("%-9s %-30s %5d %8d %8d%s\n", code, lab, rv, rn, ln,
                if (ln == rn) "" else "   <-- MISMATCH"))
  }
}

cat("\nAll 16 item x level cells must match. Every level count within an item is\n",
    "distinct (e.g. FTND_1: 27/54/148/90; FTND_2: 170 vs 149), so the match pins\n",
    "each option_text to one resp value, not merely the scale's direction.\n",
    "This does NOT test item_text<->item; that is data_labels (item == header).\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

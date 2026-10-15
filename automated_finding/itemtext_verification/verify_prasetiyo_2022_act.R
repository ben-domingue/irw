# verify_prasetiyo_2022_act.R -- Step 5b, re-runnable evidence (automated_finding repos 2026-10-14 A).
#
# CLAIM: the k-th statement of Part B of the deposited questionnaire (Mendeley 10.17632/bdzjtff5bh,
# Questionnaire_An Investigation of TPACK among Indonesian Teachers.docx) is the stem of the k-th
# ACT item column of the xlsx (A1..A8, Up1..Up5, Un1..Un6). mapping_basis paper_order: the xlsx
# header row carries the code, not the wording.
#
# Route: keyed polarity. By CONTENT, eight Part B statements are negatively worded about computer
# technology (A3 "I'm not the type ...", A4 "There is a fear ...", A5 "... confusing me", A7 "I'm
# anxious ...", Un1 "I don't use a computer every day", Un2 "... more work to do", Un3 "I don't think
# ... any use", Un5 "I don't see how ...", Un6 "... will not help") and A6 ("I don't feel threatened")
# is positive. The claim predicts that each negatively keyed column correlates negatively with the
# mean of the positively keyed columns, and each positive column positively. A stem assigned to the
# wrong column would flip the sign for that column.
# NOT established: order WITHIN the positive set or within the negative set -- PARTIAL.
#
# Data: staged response CSV (not on Redivis yet). Run from the repo root (irw/src) or automated_finding/.

TABLE <- "prasetiyo_2022_act"
f <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))
if (!file.exists(f)) f <- file.path("irw_output", paste0(TABLE, ".csv"))
d <- read.csv(f)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
NEG <- c("A3", "A4", "A5", "A7", "Un1", "Un2", "Un3", "Un5", "Un6")
POS <- setdiff(c(paste0("A", 1:8), paste0("Up", 1:5), paste0("Un", 1:6)), NEG)
cat("respondents:", nrow(w), "\n\n")
ok <- TRUE
cat(sprintf("%-5s %-9s %8s\n", "item", "keyed", "r(pos)"))
for (it in c(POS, NEG)) {
  others <- setdiff(POS, it)
  r <- cor(w[[it]], rowMeans(w[, others]), use = "complete.obs")
  keyed <- if (it %in% NEG) "negative" else "positive"
  good <- if (it %in% NEG) r < -0.1 else r > 0.1
  ok <- ok && good
  cat(sprintf("%-5s %-9s %8.3f %s\n", it, keyed, r, if (good) "" else "<-- MISMATCH"))
}
cat("\nRESULT (2026-10-15): every negatively worded statement's column correlates POSITIVELY\n",
    "(r 0.22-0.45) with the positive block, and Un4 ('Whatever a computer can do, I can also do\n",
    "well in other ways') is the only column that correlates negatively. Either the deposit\n",
    "stores the negative items already reverse-scored (then Un4 is a stem in the wrong position)\n",
    "or it does not (then nine stems sit on the wrong columns). The route cannot tell which, so\n",
    "the positional claim is NOT confirmed and the item text is withheld.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

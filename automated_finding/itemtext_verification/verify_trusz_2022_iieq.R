# Step 5b verification for the three trusz_2022_iieq_* tables.
#
# mapping_basis is paper_explicit: the .sav carries NO variable or value labels
# on the item columns, so every stem comes from the deposit's companion
# 1_IIEQ.docx, which prints the items numbered 1..14 per section. The claim
# under test is that docx item k is data column <pre>k -- the thing that would
# break if item_text for items 3 and 5 were swapped.
#
# THE ROUTE. The same deposit ships six derived subscale means it used in the
# chapter -- SSEMat/SSELit, PEMat/PELit, TEMat/TELit, labelled "Average
# students'/parents'/teachers' expectancies on math/literacy. The docx states
# which item numbers belong to each subscale, and which are reverse-scored.
# So the docx's lists make a falsifiable prediction about columns the docx
# never mentions: averaging the named columns must reproduce the deposit's own
# mean, to the bit. It would not if the item numbering were offset, permuted
# across subscales, or wrong about which items reverse.
#
# The negative control matters as much as the positive one: the same average
# computed WITHOUT substituting the depositor's reverse-scored copies must
# FAIL, which is what independently confirms the docx's asterisks.
#
# WHAT THIS DOES NOT ESTABLISH, and why the status is PARTIAL rather than
# VERIFIED: a mean is invariant to permutation WITHIN a subscale. Swapping
# item_text for SelfExp4 and SelfExp5 -- both math, both forward-scored --
# leaves every number below unchanged. This route pins each item's subscale and
# its polarity class, which is 2 x 2 = 4 classes over 14 items, not 14.
#
# Self-contained: reads the deposit's .sav directly, because these tables are
# not live yet. Point IIEQ_SAV at
# 8_AnxietyAchievementExpectancies_Routledge_n897.tab downloaded with
# ?format=original from doi:10.7910/DVN/3BZAUD (md5 43c7bb08670f8490989e69d0a61407a8).

suppressMessages(library(haven))

SAV <- Sys.getenv("IIEQ_SAV", "data.sav")
TOL <- 1e-9

d <- haven::read_sav(SAV)

# 1_IIEQ.docx: "Expectancies concerning achievement in math: item #..." and the
# "* reverse scale" asterisks, transcribed per section.
SPEC <- list(
  list(pre = "SelfExp",    math = c(1, 4, 5, 6, 8, 9, 13),
       lit = c(2, 3, 7, 10, 11, 12, 14), rev = c(6, 7, 8, 10),
       tgt_math = "SSEMat", tgt_lit = "SSELit"),
  list(pre = "ParentExp",  math = c(1, 3, 6, 10, 12, 13, 14),
       lit = c(2, 4, 5, 7, 8, 9, 11), rev = c(2, 3),
       tgt_math = "PEMat", tgt_lit = "PELit"),
  list(pre = "TeacherExp", math = c(1, 2, 4, 6, 7, 8, 9),
       lit = c(3, 5, 10, 11, 12, 13, 14), rev = integer(0),
       tgt_math = "TEMat", tgt_lit = "TELit")
)

# The deposit computed its means after linear interpolation, so compare against
# the `_1` copies. The shipped resp values are the raw columns; the mapping from
# code to column is the same either way, which is what is under test here.
cols_for <- function(pre, idx, rev, use_rev) {
  vapply(idx, function(i) {
    nm <- if (use_rev && i %in% rev) paste0(pre, i, "r_1") else paste0(pre, i, "_1")
    if (!nm %in% names(d)) stop("missing column: ", nm)
    nm
  }, character(1))
}

recon <- function(pre, idx, rev, use_rev)
  rowMeans(as.data.frame(d[, cols_for(pre, idx, rev, use_rev), drop = FALSE]))

cat(sprintf("%-11s %-7s %-10s %12s %12s %9s\n",
            "section", "subscale", "reverse", "max|diff|", "mean|diff|", "n exact"))
ok <- TRUE
for (s in SPEC) {
  for (which in c("math", "lit")) {
    idx <- s[[which]]
    tgt <- d[[s[[paste0("tgt_", which)]]]]
    for (use_rev in c(TRUE, FALSE)) {
      diff <- abs(recon(s$pre, idx, s$rev, use_rev) - tgt)
      cat(sprintf("%-11s %-7s %-10s %12.9f %12.9f %9d\n",
                  s$pre, which, if (use_rev) "as docx" else "ignored",
                  max(diff), mean(diff), sum(diff < TOL)))
      if (use_rev && max(diff) > TOL) ok <- FALSE
      # negative control: ignoring the asterisks must break a section that has
      # reverse items. TeacherExp has none, so there it legitimately matches.
      if (!use_rev && length(s$rev) > 0 && max(diff) <= TOL) ok <- FALSE
    }
  }
}

cat("\nSix subscale means reconstructed from the docx's own item lists, on all",
    nrow(d), "rows.\n")
cat("Reverse-scored copies substituted per the docx's asterisks: exact.\n")
cat("Same averages with the asterisks ignored: must and does differ for\n",
    "SelfExp and ParentExp, confirming the polarity assignment independently.\n", sep = "")
cat("Note: a subscale mean is invariant to permutation WITHIN the subscale, so\n",
    "this route pins each item's subscale and polarity -- four classes over 14\n",
    "items -- and cannot separate two forward-scored math items from each other.\n",
    "That is why the recorded status is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

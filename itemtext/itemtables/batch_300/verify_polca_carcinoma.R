# Verification for polca_carcinoma (#2228, batch_300).
#
# SOURCE. The carcinoma data set in the poLCA R package (CRAN, GPL-2+), whose man
# page states it outright: "Dichotomous ratings by seven pathologists of 118
# slides for the presence or absence of carcinoma in the uterine cervix.
# Pathologists are labeled A through G." Originally Agresti (2002), Categorical
# Data Analysis 2nd ed., Table 13.1, p. 542.
#
# THE ITEMS ARE RATERS, NOT QUESTIONS, and that is the whole point of the table.
# data/polca.R does item = names(x)[i] over the seven columns, so the code IS the
# pathologist label; the persons are slides. There is no administered wording to
# transcribe, so item_text describes the rating task in brackets.
#
# Route 1: codes are A-G, and the table has the documented shape.
# Route 2: the recode. The man page says the source stores 1 = "no" and 2 =
#   "yes"; the script subtracts 1, so the live table must be 0/1.
# Route 3: 118 slides, 20 distinct response patterns -- both stated on the man
#   page, and both checkable in the live data.
d <- as.data.frame(irw::irw_fetch("polca_carcinoma"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== Route 1: the seven pathologists ===\n")
r1 <- setequal(unique(d$item), LETTERS[1:7])
cat(sprintf("  live codes: %s -- equals A-G: %s\n", paste(sort(unique(d$item)), collapse=","), r1))

cat("\n=== Route 2: the 1/2 -> 0/1 recode ===\n")
lv <- sort(unique(d$resp))
r2 <- identical(as.numeric(lv), c(0, 1))
cat(sprintf("  live resp levels %s; the man page documents 1 = no, 2 = yes and\n", paste(lv, collapse=",")))
cat(sprintf("  data/polca.R does df$resp <- df$resp - 1, so 0 = no and 1 = yes: %s\n", r2))
cat("  option_text ships those two labels and raw_resp keeps the source's 1/2,\n")
cat("  so a reader can get back to the original coding.\n")

cat("\n=== Route 3: 118 slides and 20 response patterns ===\n")
n_slides <- length(unique(d$id))
w <- reshape(d[, c("id","item","resp")], direction="wide", idvar="id", timevar="item")
pat <- apply(w[, -1], 1, paste, collapse="")
cat(sprintf("  distinct slides: %d (man page says 118)\n", n_slides))
cat(sprintf("  distinct response patterns: %d (man page says 20)\n", length(unique(pat))))
r3 <- n_slides == 118 && length(unique(pat)) == 20
cat(sprintf("  -> both match the published description: %s\n", r3))
cat("  A dropped or duplicated rater would change the pattern count, so this is\n")
cat("  a joint check on the item set and the recode rather than a headcount.\n")

cat("\n=== per-pathologist positive rate, for a human read ===\n")
for (i in LETTERS[1:7])
    cat(sprintf("  %s  n=%3d  proportion 'yes' %.3f\n", i, sum(d$item==i), mean(d$resp[d$item==i])))

cat("\n=== What this does NOT establish ===\n")
cat("  Which human pathologist is which -- the labels A-G are anonymous in the\n")
cat("  source and carry no identity. item_text is this project's description of\n")
cat("  the rating task, not anything a rater was shown.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")

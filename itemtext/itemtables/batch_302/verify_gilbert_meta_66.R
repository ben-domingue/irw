# Verification for gilbert_meta_66 (#2228, batch_302).  STATUS: PARTIAL.
#
# SOURCE. A cluster-randomised controlled trial of a mental health literacy
# program for community sport leaders, doi:10.1016/j.mhp.2023.200259; deposit
# bridges.monash.edu article 20422257, CC BY 4.0.
#
# NO ITEM TEXT SHIPS, AND THE REASON IS AN ADAPTATION THAT CANNOT BE PINNED.
# The instrument is the General Help Seeking Questionnaire (Wilson, Deane,
# Ciarrochi & Rickwood 2005), which lists help sources -- intimate partner,
# friend, parent, mental health professional and so on -- and asks how likely
# the respondent is to seek help from each. The deposit's data file carries only
# bare column names (GHSQ_1..GHSQ_10 and a _T2 set), with no labels, and the
# paper is not open access.
#
# THE CANONICAL GHSQ HAS TEN SOURCES, which matches the ten codes and is
# tempting. But the canonical scale is answered 1-7 (extremely unlikely to
# extremely likely) and THIS DATA IS 1-4, so the study demonstrably adapted the
# instrument. An adaptation that changes the response scale can equally change
# or reorder the source list, and for help-seeking content a wrong assignment --
# saying "intimate partner" where the item is "doctor" -- is worse than none.
# So item_text is blank and only the structure and the instrument identity ship.
#
# Route 1: ten codes on a 1-4 scale.
# Route 2: the scale departs from the published instrument, which is the
#   evidence that an adaptation happened.
d <- as.data.frame(irw::irw_fetch("gilbert_meta_66"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/gilbert_meta_66__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: the code set and scale ===\n")
r1 <- setequal(unique(d$item), paste0("ghsq_", 1:10))
lv <- sort(unique(d$resp))
cat(sprintf("  codes: %s\n", paste(sort(unique(d$item)), collapse = ", ")))
cat(sprintf("  exactly ghsq_1..ghsq_10: %s\n", r1))
cat(sprintf("  resp levels: %s\n", paste(lv, collapse = ",")))
r1b <- setequal(unique(items$item), unique(d$item))
cat(sprintf("  shipped item set matches live: %s\n", r1b))

cat("\n=== Route 2: the scale is not the published one ===\n")
r2 <- identical(as.numeric(lv), as.numeric(1:4))
cat(sprintf("  live scale is 1-4; the published GHSQ uses 1-7 (extremely unlikely to\n"))
cat(sprintf("  extremely likely): adaptation confirmed: %s\n", r2))
cat("  This is the finding that blocks the wording rather than a detail: it shows\n")
cat("  the study modified the instrument, so the canonical ten-source order\n")
cat("  cannot be assumed to survive. Ten codes matching ten canonical sources is\n")
cat("  suggestive and not sufficient.\n")

cat("\n=== per-item means, for a human read ===\n")
for (i in paste0("ghsq_", 1:10))
    cat(sprintf("  %-8s n=%4d  mean %.2f\n", i, sum(d$item == i), mean(d$resp[d$item == i], na.rm = TRUE)))
cat("  The spread across items is consistent with different help sources being\n")
cat("  differently likely, but it names none of them.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which help source each code is -- the whole of the item text. WHAT WOULD\n")
cat("  UNBLOCK IT: the trial's own questionnaire, or a labelled version of the\n")
cat("  deposit's data file. The instrument, the ten-item structure and the 1-4\n")
cat("  scale are recorded so a later pass starts from there.\n")
cat("\nVERDICT:", if (r1 && r1b && r2) "PASS" else "FAIL", "\n")

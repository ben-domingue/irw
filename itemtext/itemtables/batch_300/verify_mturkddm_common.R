# Shared verification for the two mturkddm_* tables (#2228, batch_300).
# Sourced by the per-table wrappers, which set TB first.
#
# SOURCE. Ratcliff & Hendrickson (2021), 'Do data from mechanical Turk subjects
# replicate accuracy, response time, and diffusion modeling results?', Behavior
# Research Methods 53:2302, CC BY; deposit osf.io/za9y8.
#
# WHAT MAKES BOTH OF THESE FULLY ADDRESSABLE. In each table the item code IS the
# stimulus -- the letter string shown on screen for the lexical task, and the
# "yellow blue" dot counts for the numerosity task -- and data/mturk_ddm.R's
# header documents the response mapping outright, key 1 and key 2 with their
# meanings. So option_text, resp, raw_resp and correct_response are all fixed by
# the source rather than inferred, and no option row is left unjoinable.
d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv(file.path("itemtables/batch_300", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")
items$item <- as.character(items$item)

cat("=== Route 1: every item carries a correct and an incorrect option row ===\n")
opt <- items[!is.na(items$option_text), ]
per <- tapply(opt$resp, opt$item, function(v) identical(sort(as.numeric(v)), c(0, 1)))
r1 <- all(per) && setequal(unique(items$item), unique(d$item))
cat(sprintf("  items %d; each with exactly one resp=1 and one resp=0 option row: %s\n",
            length(per), all(per)))
cat(sprintf("  item set identical to live: %s\n", setequal(unique(items$item), unique(d$item))))
cat("  So option_text joins to the response data on (item, resp): the resp=1 row\n")
cat("  names the response that scored correct, the resp=0 row the one that did not.\n")

cat("\n=== Route 2: the key agrees with the stimulus the code encodes ===\n")
r2 <- CHECK_KEY(items)

cat("\n=== Route 3: accuracy is above chance and below ceiling ===\n")
acc <- mean(d$resp, na.rm = TRUE)
sub <- tapply(d$resp, d$id, mean, na.rm = TRUE)
cat(sprintf("  overall accuracy %.3f over %d responses and %d participants\n",
            acc, nrow(d), length(sub)))
cat(sprintf("  per-participant accuracy: median %.3f, range %.3f-%.3f\n",
            median(sub, na.rm = TRUE), min(sub, na.rm = TRUE), max(sub, na.rm = TRUE)))
r3 <- acc > 0.5 && acc < 1
cat(sprintf("  -> above chance and off ceiling: %s\n", r3))
cat("  A key assigned the wrong way round would put accuracy below chance, since\n")
cat("  resp was computed against it in the processing script.\n")

cat("\n=== What this does NOT establish ===\n")
cat(NOT_ESTABLISHED)
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")

# Shared verification for the nine imos_* tables (#2228, batch_301).
# Sourced by the per-year wrappers, which set YEAR first.
#
# WHAT THESE TABLES ARE. Each imos_<year> is one International Mathematical
# Olympiad: six problems, each scored 0-7 by the coordinators, with contestants
# as persons. The response data comes from the Kaggle "imo-scores" dataset
# (kaggle.com/datasets/luckyt/imo-scores), whose source page states CC0: Public
# Domain in its structured metadata -- checked directly, not taken from
# biblio.csv. The item text is the official English problem paper published by
# the IMO at imo-official.org.
#
# THE MAPPING IS AS DIRECT AS IT GETS: the live codes are problem1..problem6 and
# the paper prints Problems 1 to 6. There is no renaming step and nothing to
# infer, so these routes check the shape rather than a correspondence.
#
# Route 1: six problems, scored 0-7, split three per day.
# Route 2: the shipped text is distinct per problem and plausibly a problem.
TB <- sprintf("imos_%d", YEAR)
d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv(file.path("itemtables/batch_301", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: six problems, 0-7, three per day ===\n")
r1 <- setequal(unique(d$item), paste0("problem", 1:6))
lv <- sort(unique(d$resp))
r1b <- identical(as.numeric(lv), as.numeric(0:7))
cat(sprintf("  codes: %s\n", paste(sort(unique(d$item)), collapse = ", ")))
cat(sprintf("  exactly problem1..problem6: %s\n", r1))
cat(sprintf("  resp levels %s -- the IMO marks each problem out of 7: %s\n",
            paste(lv, collapse = ","), r1b))
day <- table(unique(items[, c("item", "section_prompt")])$section_prompt)
print(day)
r1c <- length(day) == 2 && all(day == 3)
cat(sprintf("  three problems on each of two days: %s\n", r1c))

cat("\n=== Route 2: the problem statements ===\n")
tx <- unique(items[, c("item", "item_text")])
tx <- tx[order(as.integer(sub("problem", "", tx$item))), ]
r2 <- nrow(tx) == 6 && length(unique(tx$item_text)) == 6 && all(nchar(tx$item_text) > 60)
cat(sprintf("  6 distinct, non-trivial statements: %s (lengths %s)\n",
            r2, paste(nchar(tx$item_text), collapse = ", ")))
for (i in 1:6) cat(sprintf("  P%d  %s\n", i, substr(tx$item_text[i], 1, 74)))

cat("\n=== What this does NOT establish ===\n")
cat(NOT_ESTABLISHED)
cat("\nVERDICT:", if (r1 && r1b && r1c && r2) "PASS" else "FAIL", "\n")

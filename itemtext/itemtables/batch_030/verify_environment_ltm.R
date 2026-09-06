# verify_environment_ltm.R -- Step 5b route 9 (response-frequency matching).
#
# CLAIM UNDER TEST. The item text and the response anchors come from the `ltm`
# R package's own `Environment` data set and its Rd documentation. The IRW table
# stores resp as integers 1-3; the package stores an ordered factor with levels
# "very concerned" / "slightly concerned" / "not very concerned". The claim is
# (a) resp 1/2/3 = very / slightly / not very concerned in that order, and
# (b) each IRW item code names the package column whose text we shipped.
#
# THE FALSIFIABLE PREDICTION. Cross-tabulate item x level in the package data and
# item x resp in the live IRW table. A correct mapping matches cell for cell.
# All six items' count triples are distinct from one another, so this also pins
# the item axis: swapping any two items' text would break the match.
#
# This is not a plumbing re-check -- validate_items.R already compared the sets.

suppressMessages(library(irw))
suppressMessages(library(ltm))

TABLE <- "environment_ltm"
LEVELS <- c("very concerned", "slightly concerned", "not very concerned")  # resp 1,2,3

data(Environment)
src <- do.call(rbind, lapply(names(Environment), function(v)
    data.frame(item = v,
               resp = seq_along(LEVELS),
               src_n = as.integer(table(factor(Environment[[v]], levels = LEVELS))),
               stringsAsFactors = FALSE)))

# Live counts via a server-side GROUP BY -- a query, not a whole-table export.
tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                   "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS INT64) AS resp,",
                   "COUNT(*) AS live_n FROM `%s` GROUP BY item, resp"),
             tbl$qualified_reference)
live <- as.data.frame(irw:::.irw_query_tibble(q))

m <- merge(src, live, by = c("item", "resp"), all = TRUE)
m <- m[order(m$item, m$resp), ]
m$src_n[is.na(m$src_n)] <- 0L
m$live_n[is.na(m$live_n)] <- 0L

cat(sprintf("%-13s %5s %-20s %8s %8s %6s\n",
            "item", "resp", "option_text", "ltm_n", "irw_n", "diff"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-13s %5d %-20s %8d %8d %6d\n",
                m$item[i], m$resp[i], LEVELS[m$resp[i]],
                m$src_n[i], m$live_n[i], m$live_n[i] - m$src_n[i]))

mismatch <- sum(m$src_n != m$live_n)
cat(sprintf("\ncells compared: %d | mismatched cells: %d\n", nrow(m), mismatch))

# Distinctness of the item signatures -- what makes this pin the item axis too.
sig <- tapply(seq_len(nrow(m)), m$item, function(ix)
    paste(m$src_n[ix][order(m$resp[ix])], collapse = "/"))
cat("per-item count signatures: ",
    paste(sprintf("%s=%s", names(sig), sig), collapse = "  "), "\n", sep = "")
cat(sprintf("distinct signatures: %d of %d items\n", length(unique(sig)), length(sig)))
distinct_ok <- length(unique(sig)) == length(sig)

cat("Note: this establishes the anchor order and each item's identity against the\n",
    "package data IRW was built from. It does not independently confirm the ltm\n",
    "documentation's own wording against the 1990 British Social Attitudes\n",
    "questionnaire, which is not open-access.\n", sep = "")

cat(if (mismatch == 0 && distinct_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

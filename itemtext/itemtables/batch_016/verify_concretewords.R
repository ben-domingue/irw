# verify_concretewords.R -- Step 5b evidence for `concretewords` (batch_016).
#
# HISTORICAL. This script records the state that issue #1876 reported, and its
# assertions describe the BROKEN orientation deliberately. data/concretewords.R was
# corrected on 2026-09-04 (item = Expression, id = Participant); once the corrected
# table is uploaded this script will report ok=FALSE, which is the expected outcome
# and confirms the fix rather than indicating a regression. Kept unchanged as the
# batch_016 record of what was found.
#
# STATUS: NO_ROUTE, no items CSV shipped. This script therefore does NOT verify an
# item<->item_text mapping (there is none to verify). It makes the *reason* for
# NO_ROUTE re-runnable: the claim that the IRW `item` axis holds RATERS, not the
# rated multiword expressions, so no per-item text exists or can ever be recovered.
#
# The falsifiable prediction: Muraki, Abdalla, Brysbaert & Pexman (2023) collected
# concreteness ratings for 62,000 English MULTIWORD expressions. If `item` held the
# rated expressions, essentially every item value would contain a space and the item
# count would be in the tens of thousands. If `item` holds Qualtrics respondent IDs,
# every value matches ^R_[A-Za-z0-9]{15,17}$, none contains a space, and the count is
# the number of raters (order 10^3). Those two hypotheses cannot both survive.
#
# Quota note: this uses irw::irw_table_sets(), a server-side aggregate. It does NOT
# call irw_fetch(), which would export all 691,689 rows.

suppressMessages(library(irw))

TABLE <- "concretewords"

s <- irw::irw_table_sets(TABLE, source = "core", per_item = FALSE)
items <- s$items
resp  <- sort(as.numeric(s$resp))

n_items      <- length(items)
n_qualtrics  <- sum(grepl("^R_[A-Za-z0-9]{15,17}$", items))
n_with_space <- sum(grepl(" ", items))

cat(sprintf("distinct item values                      : %d\n", n_items))
cat(sprintf("matching Qualtrics ResponseID ^R_[A-Za-z0-9]{15,17}$ : %d / %d\n",
            n_qualtrics, n_items))
cat(sprintf("containing a space (multiword expression) : %d / %d\n",
            n_with_space, n_items))
cat(sprintf("resp set                                  : %s\n",
            paste(resp, collapse = ", ")))
cat("\nfirst 5 item values:\n")
cat(paste0("  ", head(items, 5), collapse = "\n"), "\n")

cat("\nprediction if item = rated expression : ~62,000 items, nearly all containing a space\n")
cat(  "prediction if item = rater (ResponseID): ~10^3 items, 100% ^R_..., 0 containing a space\n")

# data/concretewords.R (repo root, sibling of itemtext/) is the corroborating source:
#   item <- x$Participant ; id <- x$Expression
SCRIPT <- file.path("..", "..", "..", "data", "concretewords.R")
if (file.exists(SCRIPT)) {
    src <- readLines(SCRIPT, warn = FALSE)
    cat("\ndata/concretewords.R assignment lines:\n")
    cat(paste0("  ", grep("^(item|id)\\s*<-", src, value = TRUE), collapse = "\n"), "\n")
} else {
    cat("\n(data/concretewords.R not found at", SCRIPT, "-- skipping corroboration)\n")
}

ok <- (n_qualtrics == n_items) && (n_with_space == 0) && n_items < 10000

cat("\nWhat this does NOT establish: nothing about any item<->item_text mapping,\n",
    "because no item text was shipped and none exists -- an anonymous respondent ID\n",
    "has no stem. It also does not verify the option axis: the 1-5 direction shipped\n",
    "in the parked file (1 = Abstract, 5 = Concrete) follows the printed anchor order\n",
    "in the OSF instructions docx and was not checked against counts or value labels.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

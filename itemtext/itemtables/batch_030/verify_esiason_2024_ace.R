# verify_esiason_2024_ace.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST: each item code in esiason_2024_ace names one of the ten
# canonical ACE categories, and the item_text shipped for that code is the
# canonical ACE question for that same category.
#
# Two independent falsifiable checks:
#
#  A. SELF-DESCRIBING CODES (the Step 5b exemption, made mechanical).
#     Every item code appears as a whole word in its OWN item_text and in no
#     other item's item_text. If item_text for any two items were swapped this
#     fails immediately. This is what distinguishes all ten items from each
#     other.
#
#  B. PER-ITEM ENDORSEMENT COUNTS (route 1).
#     Esiason et al. 2024 (PLOS ONE 19(3):e0300777) print per-category
#     endorsement counts for their caregiver sample (n = 21). That sample is
#     the 21-record S1 file, which the IRW processing script labels
#     cov_group == "patient" (the group labels are transposed relative to the
#     paper -- see notes_esiason_2024_ace.csv; it does not affect item text).
#     Summing resp within that subset must reproduce the published counts.
#     NB: this route alone is only PARTIAL -- three categories tie at 5 and two
#     tie at 0, so it cannot separate push/loved/depressed or touch/eat. Check A
#     is what does that.

suppressMessages(library(irw))

TABLE <- "esiason_2024_ace"
ITEMS <- c("swear","push","touch","loved","eat","divorced","mother","drugs","depressed","prison")

# Esiason et al. 2024, Results, caregiver sample (denominator 21):
# "parental divorce (28.6%, n = 6); abuse: verbal/emotional (38.1%, n = 8),
#  physical (23.8%, n = 5), sexual (0%); neglect: emotional (23.8%, n = 5),
#  physical (0%); household member with: substance abuse (42.9%, n = 9)
#  mental illness (23.8%, n = 5) imprisoned (9.5%, n = 2); and caregiver
#  physical abuse (9.5%, n = 2)."
PUBLISHED <- c(swear = 8, push = 5, touch = 0, loved = 5, eat = 0,
               divorced = 6, mother = 2, drugs = 9, depressed = 5, prison = 2)
CATEGORY <- c(swear = "verbal/emotional abuse", push = "physical abuse",
              touch = "sexual abuse", loved = "emotional neglect",
              eat = "physical neglect", divorced = "parental divorce",
              mother = "caregiver physical abuse", drugs = "household substance abuse",
              depressed = "household mental illness", prison = "household member imprisoned")
# Known single discrepancy, documented in provenance/notes: the paper reports 2
# caregivers endorsing "imprisoned" while the deposited file records 0.
KNOWN_MISMATCH <- "prison"

script_dir <- {
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grep("^--file=", a)])
    if (length(f)) dirname(normalizePath(f[1])) else "."
}
items <- read.csv(file.path(script_dir, paste0(TABLE, "__items.csv")),
                  stringsAsFactors = FALSE)
txt <- tapply(items$item_text, items$item, function(x) unique(x)[1])

cat("=== A. self-describing codes: code appears as a whole word in its own item_text only ===\n")
okA <- TRUE
for (i in ITEMS) {
    hits <- ITEMS[vapply(ITEMS, function(j)
        grepl(paste0("\\b", i, "\\b"), txt[[j]], ignore.case = TRUE), logical(1))]
    good <- identical(hits, i)
    okA <- okA && good
    cat(sprintf("%-10s -> matches item_text of: %-28s %s\n",
                i, paste(hits, collapse = ","), if (good) "OK" else "FAIL"))
}

cat("\n=== B. per-item endorsement counts, paper caregiver sample (n=21) ===\n")
d <- irw::irw_fetch(TABLE)
sub <- d[d$cov_group == "patient", ]          # = the 21-record S1 file
cat(sprintf("subset: %d ids, %d rows\n", length(unique(sub$id)), nrow(sub)))
obs <- tapply(sub$resp, sub$item, sum)
cat(sprintf("%-10s %-28s %10s %10s %8s\n", "item", "paper category", "published", "observed", "diff"))
okB <- TRUE
for (i in ITEMS) {
    o <- as.numeric(obs[[i]]); p <- PUBLISHED[[i]]
    hit <- isTRUE(o == p)
    if (!hit && !(i %in% KNOWN_MISMATCH)) okB <- FALSE
    cat(sprintf("%-10s %-28s %10d %10d %8d %s\n", i, CATEGORY[[i]], p, o, o - p,
                if (hit) "" else if (i %in% KNOWN_MISMATCH) "(known source discrepancy)" else "MISMATCH"))
}
nmatch <- sum(vapply(ITEMS, function(i) isTRUE(as.numeric(obs[[i]]) == PUBLISHED[[i]]), logical(1)))
cat(sprintf("\nexact count matches: %d / %d\n", nmatch, length(ITEMS)))

cat(sprintf("\nA (self-describing codes): %s\nB (published counts): %s\n",
            if (okA) "PASS" else "FAIL", if (okB) "PASS" else "FAIL"))
cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

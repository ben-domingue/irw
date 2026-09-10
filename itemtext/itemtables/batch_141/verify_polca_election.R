# verify_polca_election.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each live IRW `item` code carries exactly the responses of the
# identically-named column of poLCA::election, so the item_text shipped for e.g.
# "MORALG" really is the trait asked as election$MORALG (ANES 2000 K2a, "MORAL",
# about Al Gore) and not some other trait/candidate column.
#
# FALSIFIABLE PREDICTION: data/polca.R melts election[,1:12] with
# item = names(x)[i] and drops nothing, so the live per-item row count over
# non-missing resp must equal the per-column non-NA count in poLCA::election.
# All 12 of those counts are DISTINCT, so any permutation of the 12 codes --
# swapping two traits, or swapping the G/B candidate suffix -- breaks at least
# two rows of the comparison below. This is why n, not content, is the discriminator.
#
# Uses irw_table_sets() (server-side aggregate), NOT irw_fetch() -- no export.

suppressMessages(library(irw))
suppressMessages(library(poLCA))

TABLE <- "polca_election"
ITEMS <- c("MORALG","CARESG","KNOWG","LEADG","DISHONG","INTELG",
           "MORALB","CARESB","KNOWB","LEADB","DISHONB","INTELB")

data(election, package = "poLCA")
src <- sapply(ITEMS, function(v) sum(!is.na(election[[v]])))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live <- setNames(as.numeric(pi$n), as.character(pi$item))[ITEMS]

cat(sprintf("%-9s %12s %10s %7s\n", "item", "poLCA n", "live n", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-9s %12d %10d %7d\n", ITEMS[i], src[i], live[i], live[i] - src[i]))

nbad <- sum(src != live)
cat(sprintf("\nmismatched items: %d of %d\n", nbad, length(ITEMS)))
cat(sprintf("distinct n values among the 12 source columns: %d of 12 -- so any permutation of the codes is detectable\n", length(unique(src))))

# Response-option axis: the factor levels of the source columns literally carry
# the integer the IRW table stores, and data/polca.R sets
# resp <- as.numeric(substr(resp, 1, 1)) on those labels.
lv <- levels(election$MORALG)
cat("\nsource factor levels (all 12 columns identical):", paste(lv, collapse = " | "), "\n")
ok_lv <- identical(lv, c("1 Extremely well","2 Quite well","3 Not too well","4 Not well at all")) &&
         all(sapply(ITEMS, function(v) identical(levels(election[[v]]), lv)))
cat("levels carry their own resp integer, identical across all 12 items:", ok_lv, "\n")

cat("\nNote: this route pins the item CODE to its source COLUMN, and the resp integer\n",
    "to its option label, both exactly. It does not independently test that the header\n",
    "abbreviation MORAL/CARES/KNOW/LEAD/DISHON/INTEL + G/B expands to the ANES trait\n",
    "wording shipped in item_text -- that rests on the codes being self-describing and\n",
    "on poLCA's own ?election listing the same six traits for Gore and Bush.\n", sep = "")

cat(if (nbad == 0 && ok_lv) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

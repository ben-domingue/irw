## Session A_batch: select 100 fresh tables for batch evaluation, reusing
## cached data from the pilot (sessionA). No live Redivis/Sheet pulls.
pilot <- "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionA"
here  <- "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionA_batch"
cache_dir <- file.path(pilot, "raw_cache")

## STEP 1 -- load from cache
tabs  <- readRDS(file.path(pilot, "tables_available.rds"))
stats <- readRDS(file.path(pilot, "table_stats.rds"))
dict  <- readRDS(file.path(pilot, "dict_raw.rds"))

missing_from_cache <- setdiff(tabs, sub("\\.rds$", "", list.files(cache_dir, pattern = "\\.rds$")))
cat("Tables missing from raw_cache (would need live re-fetch):", length(missing_from_cache), "\n")
if (length(missing_from_cache)) print(missing_from_cache)

## STEP 2 -- exclude already-used tables
pilot_manifest <- read.csv(file.path(pilot, "manifest.csv"), stringsAsFactors = FALSE)
pilot_used <- pilot_manifest$table

verify_fix_used <- c(
    "firstborn_personality", "fisher_temperment",
    "idcr_martinez_2023_story_recall_2", "preschool_sel_wj",
    "veterans_affairs_ssvf_survey_2018-20"
)
## NOTE: instructions said "2 of those 5 overlap the original 10", but the
## actual verify_fix/ directory (candidate_*.rds, 5 files) shows ALL 5
## verify-fix tables are already among the pilot 10 -- flagged back to Ben,
## proceeding with the correct (larger) overlap, which just means the
## exclusion set is the pilot's 10 tables, not 13.
excluded <- union(pilot_used, verify_fix_used)
cat("Excluded tables (pilot + verify_fix union):", length(excluded), "\n")

pool <- setdiff(tabs, excluded)
cat("Remaining candidate pool:", length(pool), "\n")

## STEP 3 -- stratification
stats <- stats[match(pool, stats$table), ]
stopifnot(!any(is.na(stats$table)))

## item-name type: bare-integer vs named. Determined from cached raw pull:
## a table is "bare-integer" if ALL of its distinct item ids are pure
## integers (e.g. "1","2","03"), no letters/underscores/prefixes.
is_bare_integer_table <- function(tab) {
    f <- file.path(cache_dir, paste0(tab, ".rds"))
    d <- readRDS(f)
    items <- unique(as.character(d$item))
    all(grepl("^[0-9]+$", items))
}
stats$has_bare_integer_items <- vapply(pool, is_bare_integer_table, logical(1))

cat("\nPool breakdown before sampling:\n")
cat("  multi-option:", sum(stats$has_multi_option), " | free/binary:", sum(!stats$has_multi_option), "\n")
cat("  nontrivial sections:", sum(stats$has_nontrivial_sections),
    " | flat:", sum(!stats$has_nontrivial_sections), "\n")
cat("  bare-integer items:", sum(stats$has_bare_integer_items),
    " | named items:", sum(!stats$has_bare_integer_items), "\n")

## flat, multi-item tables (per pilot note: most flat tables are single-item)
flat_multi_item <- stats$table[!stats$has_nontrivial_sections & stats$n_items > 1]
cat("  flat AND >1 item:", length(flat_multi_item), "\n")

set.seed(20260811)

bare_int_pool <- stats$table[stats$has_bare_integer_items]
named_pool    <- stats$table[!stats$has_bare_integer_items]

## Target: oversample bare-integer tables to >=15-20 of the 100.
n_bare_target <- min(length(bare_int_pool), 20)
sel_bare <- sample(bare_int_pool, n_bare_target)

## Remaining 80 (or more, if bare_int_pool was short) drawn from everything
## else, stratified roughly proportionally on multi-option x flat/nontrivial
## within the named+leftover-bare pool, but simplest robust approach:
## stratified sample on (has_multi_option, has_nontrivial_sections) crossed
## with remaining pool after removing sel_bare.
remaining_pool <- setdiff(pool, sel_bare)
rstats <- stats[match(remaining_pool, stats$table), ]
rstats$strata <- interaction(rstats$has_multi_option, rstats$has_nontrivial_sections, drop = TRUE)

n_remaining_target <- 100 - length(sel_bare)
strata_tab <- table(rstats$strata)
## proportional allocation with rounding, then top up/trim to hit exact n
alloc <- floor(n_remaining_target * strata_tab / sum(strata_tab))
deficit <- n_remaining_target - sum(alloc)
## distribute leftover one at a time to largest strata first
ord <- order(-strata_tab)
i <- 1
while (deficit > 0) {
    s <- names(strata_tab)[ord[(i - 1) %% length(strata_tab) + 1]]
    if (alloc[s] < strata_tab[s]) {
        alloc[s] <- alloc[s] + 1
        deficit <- deficit - 1
    }
    i <- i + 1
}

sel_remaining <- unlist(lapply(names(alloc), function(s) {
    cand <- rstats$table[rstats$strata == s]
    sample(cand, min(alloc[s], length(cand)))
}))

selected <- c(sel_bare, sel_remaining)
## top up if short (shouldn't happen given pool size) by random draw from leftover pool
if (length(selected) < 100) {
    leftover <- setdiff(pool, selected)
    selected <- c(selected, sample(leftover, 100 - length(selected)))
}
selected <- unique(selected)
stopifnot(length(selected) == 100)

sel_stats <- stats[match(selected, stats$table), ]

cat("\n=== FINAL 100-table selection: stratification breakdown ===\n")
cat("Response format:  multi-option =", sum(sel_stats$has_multi_option),
    " | free/binary =", sum(!sel_stats$has_multi_option), "\n")
cat("Structure:        nontrivial sections =", sum(sel_stats$has_nontrivial_sections),
    " | flat =", sum(!sel_stats$has_nontrivial_sections), "\n")
cat("Item-name type:   bare-integer =", sum(sel_stats$has_bare_integer_items),
    " | named/labeled =", sum(!sel_stats$has_bare_integer_items), "\n")

saveRDS(sel_stats, file.path(here, "selected_stats.rds"))
saveRDS(pool, file.path(here, "candidate_pool.rds"))

## STEP 4 -- pull and store groundtruth_<table>.rds from cache
for (tab in selected) {
    outfile <- file.path(here, paste0("groundtruth_", tab, ".rds"))
    if (file.exists(outfile)) next
    f <- file.path(cache_dir, paste0(tab, ".rds"))
    if (!file.exists(f)) {
        cat("WARNING: no cache for", tab, "-- would need live fetch (skipped)\n")
        next
    }
    d <- readRDS(f)
    saveRDS(d, outfile)
}

## manifest_batch.csv
names(dict)[names(dict) == "URL (for data)"] <- "url_for_data"
names(dict)[names(dict) == "DOI (for paper)"] <- "doi"
dict$table.lower <- tolower(dict$table.lower)
dict_m <- dict[match(tolower(selected), dict$table.lower), c("url_for_data", "Reference", "doi")]

manifest <- data.frame(
    table = selected,
    n_items = sel_stats$n_items,
    n_sections = sel_stats$n_sections,
    has_multi_option = sel_stats$has_multi_option,
    has_bare_integer_items = sel_stats$has_bare_integer_items,
    url_for_data = dict_m$url_for_data,
    reference_citation = dict_m$Reference,
    doi = dict_m$doi,
    stringsAsFactors = FALSE
)

write.csv(manifest, file.path(here, "manifest_batch.csv"), row.names = FALSE)
cat("\nWrote manifest_batch.csv and", sum(file.exists(file.path(here, paste0("groundtruth_", selected, ".rds")))),
    "groundtruth_*.rds files\n")

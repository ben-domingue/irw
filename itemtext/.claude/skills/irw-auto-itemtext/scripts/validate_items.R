# Usage: Rscript validate_items.R <table> <path/to/table__items.csv>
#
# Same non-negotiable gate as itemtext/join.R (item-set and resp-set must
# match live response data exactly), but reports exactly which values differ
# instead of just TRUE/FALSE, and tolerates a `raw_resp` column in place of
# `resp` for tables where the scoring key can't be recovered (see
# references/itemtext_standard.md). Run this on the merged CSV before it is
# treated as valid output -- do not skip straight to writing/uploading.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("Usage: Rscript validate_items.R <table> <items_csv>")
table <- args[1]
items_path <- args[2]

items <- read.csv(items_path, stringsAsFactors = FALSE)
df <- irw::irw_fetch(table)

cat("=== Column check ===\n")
required <- c("table", "section_id", "item", "instrument", "instructions",
              "section_prompt", "item_text", "correct_response", "option_text")
missing_cols <- setdiff(required, names(items))
if (length(missing_cols)) {
    cat("Missing:", paste(missing_cols, collapse = ", "),
        "-- confirm each is genuinely not applicable (e.g. no section grouping), not just omitted.\n")
} else {
    cat("All standard columns present.\n")
}
has_resp <- "resp" %in% names(items) && any(!is.na(items$resp) & items$resp != "")
raw_resp_col <- if ("raw_resp" %in% names(items)) "raw_resp" else if ("resp_raw" %in% names(items)) "resp_raw" else NA
if (!has_resp && is.na(raw_resp_col)) {
    cat("No resp or raw_resp/resp_raw column found at all -- output is incomplete.\n")
}

cat("\n=== Item set check ===\n")
missing_from_items <- setdiff(unique(df$item), unique(items$item))
extra_in_items <- setdiff(unique(items$item), unique(df$item))
if (length(missing_from_items) == 0 && length(extra_in_items) == 0) {
    cat("PASS: item sets match exactly (", length(unique(df$item)), " items).\n", sep = "")
} else {
    cat("FAIL: item sets differ.\n")
    if (length(missing_from_items)) {
        cat("  In response data but missing from items csv (", length(missing_from_items), "): ",
            paste(missing_from_items, collapse = ", "), "\n", sep = "")
    }
    if (length(extra_in_items)) {
        cat("  In items csv but not in response data (", length(extra_in_items), "): ",
            paste(extra_in_items, collapse = ", "), "\n", sep = "")
    }
}

cat("\n=== Bare-integer item check ===\n")
item_vals <- unique(df$item)
looks_bare_integer <- length(item_vals) > 0 && all(grepl("^[0-9]+$", trimws(as.character(item_vals))))
if (looks_bare_integer) {
    cat("CAUTION: this table's `item` values are bare integers (e.g. \"",
        item_vals[1], "\") rather than named codes. An exact item-set match (above) only ",
        "confirms the *set* of integers is right, not that each integer's item_text was ",
        "mapped to the correct paper item -- resp type/range plausibility is not enough ",
        "evidence either, since multiple items typically share the same range. Manually ",
        "confirm the item order/count against the paper (position in the instrument, ",
        "subscale grouping, reverse-scored markers) before treating this as validated. ",
        "See SKILL.md Step 4.\n", sep = "")
} else {
    cat("Item identifiers are not bare integers -- no extra reconstruction caution needed.\n")
}

cat("\n=== Resp set check ===\n")
if (!has_resp) {
    if (!is.na(raw_resp_col)) {
        cat("No populated `resp` column -- using `", raw_resp_col,
            "` (scoring key not recoverable). Resp-value match against live data is not expected here; ",
            "confirm this is a deliberate call, not a shortcut.\n", sep = "")
    } else {
        cat("FAIL: no resp values at all.\n")
    }
} else {
    i1 <- sort(unique(items$resp))
    i2 <- sort(unique(df$resp))
    missing_resp <- setdiff(i2, i1)
    extra_resp <- setdiff(i1, i2)
    if (length(missing_resp) == 0 && length(extra_resp) == 0) {
        cat("PASS: resp sets match exactly.\n")
    } else {
        cat("FAIL: resp sets differ.\n")
        if (length(missing_resp)) cat("  In response data but missing from items csv:", paste(missing_resp, collapse = ", "), "\n")
        if (length(extra_resp)) cat("  In items csv but not in response data:", paste(extra_resp, collapse = ", "), "\n")
    }
}

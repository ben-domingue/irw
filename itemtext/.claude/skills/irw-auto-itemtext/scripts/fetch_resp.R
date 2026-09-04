# Shared response-data source for validate_items.R and audit_batch.R.
#
# Both gates ask the same question -- what are this table's item and resp
# values? -- and both used to answer it only from live Redivis data. That is
# right for the itemtext pipeline, whose tables are already published, but it
# cannot serve the automated_finding pipeline, which generates item text at
# processing time from a response CSV staged in irw_output/ that is not live
# yet (and must not be uploaded before its item text has been checked against
# it). See automated_finding SKILL.md Step 3.5.
#
# So the data source becomes a parameter. Passing no override reproduces the
# previous behaviour exactly; the live route is untouched.
#
# A local read is also quota-free, which matters: on 2026-08-18 the account's
# 200GB/30-day Redivis export limit was exhausted by a single round.

# Coerce a resp vector the way irw_fetch()/irw_table_sets() do: the literal
# "NA" token and blanks are missing, everything else is numeric. Keeping this
# in one place is the point -- a local gate that treated "NA" as a level while
# the live gate dropped it would disagree about the resp set for reasons that
# have nothing to do with the item text.
coerce_resp <- function(x) {
    s <- trimws(as.character(x))
    s[s %in% c("NA", "")] <- NA_character_
    suppressWarnings(as.numeric(s))
}

# A failed live fetch must not be handed back to a caller that will treat it as
# data. irw_fetch() signals "table not found" with a message() and
# invisible(NULL) rather than stop() -- deliberate upstream (fetch.R: quota,
# timeout and transport errors ARE re-raised; only not-found is softened), but
# the caller has to honour it. Unguarded, R's set semantics turn the absence
# into a confident accusation: setdiff(x, NULL) returns all of x, so "no ground
# truth" and "ground truth disagrees with every code" are indistinguishable in
# validate_items.R's output, and the obvious response to it is to damage a
# correct CSV. See ben-domingue/irw#1736.
.stop_no_live_data <- function(table) {
    v <- tryCatch(as.character(utils::packageVersion("irw")),
                  error = function(e) "not installed")
    stop("irw_fetch(", shQuote(table), ") returned no rows, so there is no ground truth to\n",
         "  compare against. NOTHING was checked -- this is a missing dependency, not a\n",
         "  finding about the CSV. Do not 'fix' the CSV in response to this.\n",
         "  Likely causes:\n",
         if (isTRUE(try(utils::packageVersion("irw") < "1.0.1", silent = TRUE)))
             paste0("    1. THE LIKELY ONE: the installed irw package (", v, ") is too old to see the\n",
                    "       warehouse shard this table lives in; these scripts need >= 1.0.1.\n",
                    "       Fix: Rscript -e 'remotes::install_github(\"itemresponsewarehouse/Rpkg\")'\n")
         else
             paste0("    1. (ruled out) irw ", v, " is recent enough to see every warehouse shard.\n"),
         "    2. The table name is misspelled.\n",
         "    3. A Redivis version pin is active and this table postdates the pinned release\n",
         "       (irw_get_version() reports pins; irw_reset_version() clears them).\n",
         call. = FALSE)
}

# The response data as a data.frame with `item` (character) and `resp`.
# resp_csv: path to a staged IRW response CSV, or NA for live.
get_resp <- function(table, resp_csv = NA) {
    if (is.na(resp_csv) || !nzchar(resp_csv)) {
        d <- irw::irw_fetch(table)
        if (is.null(d) || !nrow(d)) .stop_no_live_data(table)
        return(d)
    }
    if (!file.exists(resp_csv)) {
        stop("response CSV not found: ", resp_csv)
    }
    d <- read.csv(resp_csv, stringsAsFactors = FALSE)

    # An items CSV carries `item` and `resp` too, so pointing this at the file
    # being validated would compare it against itself and PASS vacuously.
    # `id` is required of every IRW response table and absent from an items
    # table, so it is what separates them.
    if (any(c("item_text", "option_text") %in% names(d)) && !("id" %in% names(d))) {
        stop("response CSV ", resp_csv, " looks like an itemtext table, not a ",
             "response table -- pass the staged IRW response CSV instead")
    }
    missing <- setdiff(c("id", "item", "resp"), names(d))
    if (length(missing)) {
        stop("response CSV ", resp_csv, " has no `",
             paste(missing, collapse = "`/`"), "` column -- is it an IRW response table?")
    }
    d$item <- as.character(d$item)
    d
}

# The item and resp SETS for a live table, WITHOUT exporting it.
#
# Why this exists. `get_resp()`'s live route calls irw_fetch(), which exports
# every row. validate_items.R only ever compares sets -- unique(item) and
# unique(resp), a few dozen values -- so on a large published table the gate
# spends a large export to compute almost nothing. The corpus is 181.8GB
# against a 200GB/30-day cap, and on 2026-08-18 one round of twelve agents
# exhausted it outright.
#
# That left the standing "never irw_fetch for a gate" rule unsatisfiable for
# published tables: --resp-csv only helps a table that is not live yet. In
# batch_016 five agents hit the conflict and resolved it five different ways --
# two skipped the gate, two exported, and one hand-built a surrogate CSV from an
# aggregate query and passed it via --resp-csv. That divergence is the bug this
# closes: the gate now has a route that satisfies the rule, so nobody has to
# improvise one.
#
# What it returns is a SURROGATE frame, not the data: enough distinct values for
# unique() to reproduce the two sets exactly, and nothing else. Anything that
# needs per-row or per-item counts must use a different route -- which is why
# audit_batch.R does not use this.
get_resp_sets <- function(table) {
    s <- irw::irw_table_sets(table)
    if (is.null(s) || !length(s$items)) .stop_no_live_data(table)
    items <- as.character(s$items)
    resp  <- s$resp
    n <- max(length(items), max(1L, length(resp)))
    data.frame(
        item = c(items, rep(items[1], n - length(items))),
        resp = if (length(resp)) c(resp, rep(resp[1], n - length(resp))) else NA_real_,
        stringsAsFactors = FALSE
    )
}

# The same summary shape audit_batch.R's live_sets() returns -- items, resp,
# per-item row counts, per-item resp levels -- computed from a local CSV.
# Row counts include rows with missing resp, and levels exclude them, matching
# live_sets(): the row-count anomaly check wants total rows, the per-item
# coverage check wants the levels respondents actually used.
resp_sets_local <- function(path) {
    d <- get_resp(NA_character_, path)
    item <- as.character(d$item)
    resp <- coerce_resp(d$resp)
    list(items = sort(unique(item)),
         resp = sort(unique(resp[!is.na(resp)])),
         counts = tapply(rep(1, length(item)), item, sum),
         levels = tapply(resp, item, function(v) sort(unique(v[!is.na(v)]))))
}

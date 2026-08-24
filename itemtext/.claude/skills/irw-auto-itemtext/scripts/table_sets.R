# Usage: Rscript table_sets.R <table>
#
# Prints the exact `item` and `resp` value sets for a live IRW table WITHOUT
# downloading it. This is now a thin CLI wrapper over `irw::irw_table_sets()`
# (itemresponsewarehouse/Rpkg#121, landed; in irw >= 1.0.1), which does the
# shard resolution and the server-side aggregate queries. It used to carry its
# own copy of both -- keeping two implementations of the same resolution logic
# is how they drift, so the logic lives in the package and this file only
# formats the result.
#
# WHY THIS EXISTS AT ALL: irw::irw_fetch() calls to_tibble(), which EXPORTS THE
# WHOLE TABLE. Step 5's gate needs only unique(item) and unique(resp), so
# validating a 68-million-row table that way egresses 68 million rows to compute
# a few dozen distinct values. On 2026-08-18 a round of 12 agents pointed at the
# corpus's largest tables exhausted the account's 200GB/30-day Redivis export
# quota outright. The quota window has since rolled over, but the arithmetic
# that made it inevitable has not changed: the core warehouse is 181.8GB, so any
# workflow that exports every table once spends ~91% of a month's allowance.
# Exports are capped; queries are not.
#
# The other half of #121 fixed the misreporting: an export-quota failure used to
# surface as "table does not exist in IRW", which sent four agents chasing a
# phantom missing table. irw_fetch() now names an account-wide export limit as
# such, and "does not exist" means all four core datasources genuinely returned
# not-found.
#
# This answers only "what are the item and resp sets"; for the dictionary row
# and source leads you still want table_context.R.

suppressMessages(library(irw))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Usage: Rscript table_sets.R <table>")

# per_item = TRUE is one more GROUP BY and it is the per-item coverage check
# audit_batch.R does; a whole-table download was never needed for it.
s <- irw::irw_table_sets(args[1], source = "core", per_item = TRUE)

cat("table:", s$table, "\n")
cat(sprintf("rows: %s | distinct items: %s\n",
            format(s$n_rows, big.mark = ","), length(s$items)))

cat("\n-- item set (", length(s$items), ") --\n", sep = "")
print(s$items)
cat("\n-- resp set (", length(s$resp), ") --\n", sep = "")
print(s$resp)

# NOTE ON `n`: irw_table_sets() computes the per-item rows over rows with a
# non-missing resp (the literal "NA" token and blanks are excluded, matching how
# irw_fetch() coerces them). Items whose resp is missing throughout therefore
# appear in the item set above but not in this table.
cat("\n-- per-item n and resp range (non-missing resp only) --\n")
if (is.null(s$per_item)) cat("(no item column)\n") else
    print(as.data.frame(s$per_item), row.names = FALSE)

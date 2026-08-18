# Usage: Rscript table_sets.R <table>
#
# Prints the exact `item` and `resp` value sets for a live IRW table WITHOUT
# downloading it, using a server-side aggregate query.
#
# WHY: irw::irw_fetch() calls to_tibble(), which EXPORTS THE WHOLE TABLE. Step 5's
# gate needs only unique(item) and unique(resp), so validating a 68-million-row
# table currently egresses 68 million rows to compute a few dozen distinct values.
# On 2026-08-18 a round of 12 agents pointed at the corpus's largest tables
# exhausted the account's Redivis quota outright:
#
#   [400 invalid_request] Cannot export more than 200GB within a 30 day period.
#   You have exported 204GB in the past 30 days...
#
# which irw_fetch then reported as "table does not exist in IRW" (see
# irw:::.irw_handle_datasource_error -- with several core datasources configured,
# ANY error is swallowed and the caller falls through to the not-found message).
# A GROUP BY returns a handful of rows and is unaffected by the export limit.
#
# Use this in place of table_context.R's ground truth whenever the table is large
# or export is blocked. It answers only "what are the item and resp sets"; for the
# dictionary row and source leads you still want table_context.R.

suppressMessages(library(redivis))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Usage: Rscript table_sets.R <table>")
tb <- args[1]

# The core warehouse is sharded across four datasets; a table lives in exactly one.
DATASETS <- c("item_response_warehouse:as2e", "item_response_warehouse_2:epbx",
              "item_response_warehouse_3:5xaj", "item_response_warehouse_4:980f")

qualified <- NA_character_
for (ds in DATASETS) {
    ok <- tryCatch({
        t <- redivis$user("datapages")$dataset(ds)$table(tb)
        suppressWarnings(t$get())
        TRUE
    }, error = function(e) FALSE)
    if (ok) { qualified <- sprintf("datapages.%s.%s", sub(":.*$", "", ds), tb); break }
}
if (is.na(qualified)) stop("table not found in any core datasource: ", tb)
cat("table:", qualified, "\n")

run <- function(sql) suppressWarnings(redivis$query(sql)$to_tibble())

n <- run(sprintf("SELECT COUNT(*) AS n, COUNT(DISTINCT item) AS n_items FROM `%s`", qualified))
cat(sprintf("rows: %s | distinct items: %s\n", format(n$n[1], big.mark = ","), n$n_items[1]))

# `resp` is stored as a STRING in Redivis and carries a literal "NA" token, which
# irw_fetch coerces to a real NA. Mirror that here or MIN/MAX come back NA and the
# resp set gains a phantom level.
NOT_NA <- "resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')"
items <- run(sprintf("SELECT DISTINCT item FROM `%s` ORDER BY item", qualified))$item
resp  <- run(sprintf(paste("SELECT DISTINCT CAST(resp AS FLOAT64) AS resp FROM `%s`",
                           "WHERE %s ORDER BY resp"), qualified, NOT_NA))$resp

cat("\n-- item set (", length(items), ") --\n", sep = "")
print(items)
cat("\n-- resp set (", length(resp), ") --\n", sep = "")
print(resp)

# Per-item resp coverage is the check audit_batch.R does; it is one more GROUP BY
# and it is the thing a whole-table download was never needed for.
cat("\n-- per-item n and resp range --\n")
per <- run(sprintf(paste("SELECT item, COUNT(*) AS n,",
                         "MIN(CAST(resp AS FLOAT64)) AS lo, MAX(CAST(resp AS FLOAT64)) AS hi,",
                         "COUNT(DISTINCT CAST(resp AS FLOAT64)) AS n_lev",
                         "FROM `%s` WHERE %s GROUP BY item ORDER BY item"),
                   qualified, NOT_NA))
print(as.data.frame(per), row.names = FALSE)

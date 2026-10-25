##################################################################################
## itemtext_prune.R -- drop itemtext_metadata rows whose item text is no longer
## served, with a guard against doing it on the strength of a failed listing.
##
## 08_itemtext.R only ever ADDED rows: `tables.new` is the live listing minus
## what the file already has, and nothing removed a row again. So a withdrawn
## table kept its row for ever. On 2026-10-25 that was 199 of 2,921 rows -- the
## 191 rights withdrawals plus the 9 whose text never arrived (#3224) -- and the
## file is the index of what `irw_itemtext()` can return, so each of those rows
## sends a reader to nothing and inflates every published count of tables with
## item text. Ruled 2026-10-25: they leave here, and `itemtext_issues.qmd`
## carries the fact of the withdrawal, which is where withdrawals are already
## explained.
##
## Separate from the stage so it can be tested without Redivis
## (tests/test_itemtext_prune.R).
##################################################################################

##The share of the file a single run may remove. A real withdrawal round is tens
##of tables; anything approaching a tenth of the corpus is a failed read.
ITEMTEXT_PRUNE_MAX <- 0.15

##Drop rows of `df` whose `table` is not in `live`.
##
##The guard matters more than the prune. `live` comes from a listing, and a
##listing that failed or came back short is not a corpus whose item text was
##withdrawn -- the same mistake the 2026-10-24 review found three times over in
##the clients. So an empty listing, or a prune above `max_share`, stops.
##
##Matched case-insensitively, because the published names and the listing
##disagree on case for a handful of tables (review R-31); an exact match would
##delete a row whose table is alive under a different capitalisation. Exactly one
##row was in that position on 2026-10-25.
prune_unserved_itemtext <- function(df, live, max_share = ITEMTEXT_PRUNE_MAX,
                                    announce = message) {
  if (length(live) == 0L) {
    stop("the item text listing returned nothing; refusing to prune ",
         nrow(df), " row(s) on the strength of an empty listing")
  }
  alive <- tolower(df$table) %in% tolower(live)
  if (!any(!alive)) return(df)
  share <- sum(!alive) / nrow(df)
  if (share > max_share) {
    stop(sprintf(paste("would drop %d of %d row(s) (%.1f%%), above the %.0f%%",
                       "ceiling -- that is a failed listing, not a withdrawal",
                       "round. Check the listing before raising max_share."),
                 sum(!alive), nrow(df), 100 * share, 100 * max_share))
  }
  announce(sprintf("dropping %d row(s) whose item text is no longer served (%.1f%%):",
                   sum(!alive), 100 * share))
  announce(paste(" ", paste(sort(df$table[!alive]), collapse = ", ")))
  df[alive, , drop = FALSE]
}

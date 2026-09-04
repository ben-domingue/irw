# verify_DART_Brysbaert_2020_3_4_5.R
#
# This table was BLOCKED on rights (CC BY-NC-SA on the DART/DART_R wording), so no
# __items.csv was shipped and there is no shipped mapping to verify. What this script
# verifies instead is the claim recorded in verification_DART_Brysbaert_2020_3_4_5.csv:
# that the mapping needs no inference, because every IRW `item` code is literally an
# author/foil name taken verbatim from the source files -- the Name column of
# raw_data_study3/4.xlsx (Studies 3-4, spaced spelling) and the column headers of
# raw_data_study5.xlsx (Study 5 / DART_R, underscore spelling).
#
# It is falsifiable: if the IRW codes were positional, renumbered, or otherwise
# re-derived, the live item set would not be the exact union of those source names.
#
# Ground truth is obtained server-side via irw_table_sets() -- no full-table export.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "DART_Brysbaert_2020_3_4_5"
CACHE <- file.path("..", "..", ".cache", TABLE)
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)

osf <- c(raw_study3.xlsx = "bsuy2", raw_study4.xlsx = "3n59k", raw_study5.xlsx = "nsb3a")
for (nm in names(osf)) {
  p <- file.path(CACHE, nm)
  if (!file.exists(p))
    download.file(sprintf("https://osf.io/download/%s/", osf[[nm]]), p, quiet = TRUE, mode = "wb")
}

s3 <- unique(as.character(readxl::read_excel(file.path(CACHE, "raw_study3.xlsx"))$Name))
s4 <- unique(as.character(readxl::read_excel(file.path(CACHE, "raw_study4.xlsx"))$Name))
s5h <- names(readxl::read_excel(file.path(CACHE, "raw_study5.xlsx")))
s5 <- setdiff(s5h, c("Participantcode", "Extra"))

sets <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- sets$items

src <- union(union(s3, s4), s5)

cat(sprintf("live rows                       : %d\n", sets$n_rows))
cat(sprintf("live distinct items             : %d\n", length(live)))
cat(sprintf("live resp set                   : %s\n", paste(sort(sets$resp), collapse = ", ")))
cat(sprintf("study3 Name values              : %d\n", length(s3)))
cat(sprintf("study4 Name values              : %d\n", length(s4)))
cat(sprintf("study3 vs study4 set difference : %d / %d\n",
            length(setdiff(s3, s4)), length(setdiff(s4, s3))))
cat(sprintf("study5 item columns (of %d)     : %d\n", length(s5h), length(s5)))
cat(sprintf("source union                    : %d\n", length(src)))
cat(sprintf("live minus source               : %d  %s\n",
            length(setdiff(live, src)), paste(head(setdiff(live, src)), collapse = "; ")))
cat(sprintf("source minus live               : %d  %s\n",
            length(setdiff(src, live)), paste(head(setdiff(src, live)), collapse = "; ")))

pi <- as.data.frame(sets$per_item)
n_sp <- pi$n[pi$item %in% s3]
n_us <- pi$n[pi$item %in% s5]
cat(sprintf("per-item n, Studies 3+4 items   : %d items, n in [%d, %d]\n",
            length(n_sp), min(n_sp), max(n_sp)))
cat(sprintf("per-item n, Study 5 items       : %d items, n in [%d, %d]\n",
            length(n_us), min(n_us), max(n_us)))
cat(sprintf("items with no non-missing resp  : %s\n",
            paste(setdiff(live, pi$item), collapse = "; ")))

ok <- length(setdiff(live, src)) == 0 &&
      length(setdiff(src, live)) == 0 &&
      length(setdiff(s3, s4)) == 0 && length(setdiff(s4, s3)) == 0 &&
      length(unique(n_sp)) == 1 && length(unique(n_us)) == 1

cat("\nNOTE: no __items.csv was shipped for this table (rights block). This checks that\n")
cat("the item codes are verbatim source names, i.e. that the mapping was never in doubt.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

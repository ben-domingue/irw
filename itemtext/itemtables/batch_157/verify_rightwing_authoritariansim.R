# verify_rightwing_authoritariansim.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes 1..48 are bare integers invented by data/rightwing_authoritariansim.R
# (`row_number()` over `unique(item)` after pivot_longer), so they carry no trace of the
# source column name. The extraction claims:
#     items  1-22 = Q1..Q22      (Altemeyer RWA statements, 1-9 agreement scale)
#     items 23-32 = TIPI1..TIPI10 (Gosling TIPI traits, 1-7)
#     items 33-48 = VCL1..VCL16   (vocabulary check-list words, 0/1)
# derived by re-running that script over the source deposit
# (https://openpsychometrics.org/_rawdata/RWAS.zip, RWAS/data.csv).
#
# THE TEST -------------------------------------------------------------------
# Re-run the script's column-order logic on the raw file, then compare the FULL
# per-item x per-resp count table against server-side aggregates of the live IRW
# table (a GROUP BY query, not an export). A swap of any two items -- or a shifted
# range -- changes those counts. All 48 items have pairwise-distinct response
# distributions, so a match distinguishes every item from every other item.
# This verifies the item<->item_text mapping AND the option_text<->resp mapping
# (the 1-9 / 1-7 / 0-1 supports and their level counts) at the same time.

suppressMessages({
    library(irw); library(readr); library(dplyr); library(tidyr)
})

TABLE <- "rightwing_authoritariansim"
RAW_URL <- "https://openpsychometrics.org/_rawdata/RWAS.zip"

# --- source side: re-run data/rightwing_authoritariansim.R's item numbering ---
tmp <- tempfile(fileext = ".zip"); dir <- tempfile(); dir.create(dir)
download.file(RAW_URL, tmp, quiet = TRUE); unzip(tmp, exdir = dir)
raw <- read_delim(file.path(dir, "RWAS", "data.csv"), show_col_types = FALSE, progress = FALSE)
names(raw) <- tolower(names(raw))
raw <- raw |>
    select(-ip_country, -education, -urban, -gender, -engnat, -age, -screenw, -screenh,
           -hand, -religion, -orientation, -race, -voted, -married, -familysize,
           -surveyaccurate, -major, -introelapse, -testelapse, -surveyelapse) |>
    mutate(id = row_number(),
           across(starts_with("tipi") | starts_with("q"), ~ if_else(. == 0, NA, .)))
long <- raw |> select(-starts_with("e")) |>
    pivot_longer(cols = -id, names_to = "col", values_to = "resp")
key <- data.frame(col = unique(long$col), item = seq_along(unique(long$col)))
src <- long |> left_join(key, by = "col") |> filter(!is.na(resp)) |>
    count(item, resp, name = "n_source")

cat("column -> item assignment reproduced from the script:\n")
print(data.frame(item = key$item, source_column = key$col)[c(1:3, 22:24, 32:34, 48), ], row.names = FALSE)

# --- live side: server-side GROUP BY, no table export -------------------------
tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, TRIM(CAST(resp AS STRING)) AS resp,",
                   "COUNT(*) AS n_live FROM `%s`",
                   "WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                   "GROUP BY item, resp"), tbl$qualified_reference)
live <- as.data.frame(irw:::.irw_query_tibble(q))
live$item <- as.integer(live$item); live$resp <- as.numeric(live$resp)

m <- merge(src, live, by = c("item", "resp"), all = TRUE)
m$n_source[is.na(m$n_source)] <- -1; m$n_live[is.na(m$n_live)] <- -1
bad <- m[m$n_source != m$n_live, ]

cat(sprintf("\ncells compared (item x resp): %d   mismatching: %d\n", nrow(m), nrow(bad)))
cat("\nsample of the comparison (source re-run vs live aggregate):\n")
show <- m[m$item %in% c(1, 2, 22, 23, 32, 33, 48), ]
print(show[order(show$item, show$resp), ], row.names = FALSE)
if (nrow(bad)) print(head(bad[order(bad$item, bad$resp), ], 20), row.names = FALSE)

# per-item response support, the structural signature of the three sub-instruments
sup <- src |> group_by(item) |> summarise(min = min(resp), max = max(resp), lv = n(), .groups = "drop")
cat("\nresponse support by block (source re-run):\n")
cat(sprintf("  items 1-22  (Q1-Q22):      min %g max %g levels %s\n",
            min(sup$min[1:22]), max(sup$max[1:22]), paste(unique(sup$lv[1:22]), collapse = "/")))
cat(sprintf("  items 23-32 (TIPI1-10):    min %g max %g levels %s\n",
            min(sup$min[23:32]), max(sup$max[23:32]), paste(unique(sup$lv[23:32]), collapse = "/")))
cat(sprintf("  items 33-48 (VCL1-16):     min %g max %g levels %s\n",
            min(sup$min[33:48]), max(sup$max[33:48]), paste(unique(sup$lv[33:48]), collapse = "/")))

# are the 48 distributions actually distinguishable from each other?
sig <- tapply(seq_len(nrow(src)), src$item, function(i) paste(src$resp[i], src$n_source[i], collapse = ","))
cat(sprintf("\ndistinct per-item response distributions: %d of %d\n", length(unique(sig)), length(sig)))

ok <- nrow(bad) == 0 && length(unique(sig)) == length(sig) && nrow(m) == 300
cat("\nThis pins every item individually. It does NOT check the wording itself against\n",
    "the administered form -- that tie is the openpsychometrics form's own Q/TIPI/VCL\n",
    "field names, recorded in provenance.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

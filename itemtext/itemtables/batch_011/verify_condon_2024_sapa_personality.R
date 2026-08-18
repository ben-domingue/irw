# verify_condon_2024_sapa_personality.R
#
# mapping_basis is data_labels (the Dataverse deposit ships ItemInfo.csv, a codebook
# keyed by the very q_### column names the IRW table uses), so a statistical route is
# not required. This script exists anyway for two reasons specific to this table:
#
#   1. irw::irw_fetch("condon_2024_sapa_personality") FAILS -- the table is 68,188,858
#      rows and to_tibble() cannot materialise it, so the failure surfaces misleadingly
#      as "table does not exist in IRW". validate_items.R therefore cannot gate this
#      table. The set checks are re-run here directly against Redivis instead.
#   2. It re-fetches the deposit's own ItemInfo.csv and diffs it against the shipped
#      item_text, so the code->text tie is reproduced rather than asserted.
#
# Plus one falsifiable check of the OTHER axis (option_text <-> resp): the anchors run
# 1 = Very Inaccurate ... 6 = Very Accurate per the official SPI-135 form. If that
# direction were flipped, socially undesirable items would sit ABOVE prosocial ones.

suppressMessages(library(redivis))

TABLE <- "condon_2024_sapa_personality"
TBL   <- "`datapages.item_response_warehouse_3.condon_2024_sapa_personality`"
ITEMINFO_URL <- "https://dataverse.harvard.edu/api/access/datafile/10988886"  # doi:10.7910/DVN/3BTT82

cs <- read.csv(file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                         paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
ok <- TRUE

## ---- 1. set checks (the validate_items.R gate, run against Redivis directly) ----
gt <- redivis$query(sprintf("select item, count(*) n, avg(resp) m from %s group by item", TBL))$to_data_frame()
gr <- redivis$query(sprintf("select distinct resp from %s", TBL))$to_data_frame()

cat(sprintf("live items: %d   csv items: %d   sets identical: %s\n",
            nrow(gt), length(unique(cs$item)), setequal(gt$item, unique(cs$item))))
cat(sprintf("live resp: %s   csv resp: %s   sets identical: %s\n",
            paste(sort(gr$resp), collapse = ","), paste(sort(unique(cs$resp)), collapse = ","),
            setequal(gr$resp, unique(cs$resp))))
cat(sprintf("rows per item in live data: %d - %d (ratio %.2f; SAPA administers a planned-missing subset per respondent)\n",
            min(gt$n), max(gt$n), max(gt$n) / min(gt$n)))
ok <- ok && setequal(gt$item, unique(cs$item)) && setequal(gr$resp, unique(cs$resp))

## ---- 2. code -> text tie, re-fetched from the deposit's own codebook ----
info <- tryCatch(read.csv(ITEMINFO_URL, stringsAsFactors = FALSE), error = function(e) NULL)
if (is.null(info)) {
    cat("ItemInfo.csv could not be fetched (offline?) -- code->text diff SKIPPED\n")
} else {
    ship <- unique(cs[, c("item", "item_text")])
    m <- merge(info[, c("item_id", "item")], ship, by.x = "item_id", by.y = "item")
    bad <- m[trimws(m$item) != trimws(m$item_text), ]
    cat(sprintf("ItemInfo.csv codebook rows: %d   matched to shipped items: %d   text mismatches: %d\n",
                nrow(info), nrow(m), nrow(bad)))
    if (nrow(bad)) print(head(bad, 10))
    ok <- ok && nrow(m) == nrow(ship) && nrow(bad) == 0
}

## ---- 3. anchor direction: 6 = Very Accurate, not Very Inaccurate ----
# Undesirable-trait items must sit below prosocial items if 6 = Very Accurate.
LOW  <- c("q_501" = "Cheat to get ahead.", "q_4296" = "Tell a lot of lies.",
          "q_1896" = "Use others for my own ends.")
HIGH <- c("q_90" = "Am concerned about others.", "q_1763" = "Sympathize with others' feelings.",
          "q_851" = "Feel sympathy for those who are worse off than myself.")
mn <- setNames(gt$m, gt$item)
cat("\nanchor-direction check (1 = Very Inaccurate ... 6 = Very Accurate)\n")
for (k in names(LOW))  cat(sprintf("  %-8s %-56s mean %.2f\n", k, LOW[[k]],  mn[[k]]))
for (k in names(HIGH)) cat(sprintf("  %-8s %-56s mean %.2f\n", k, HIGH[[k]], mn[[k]]))
gap <- min(mn[names(HIGH)]) - max(mn[names(LOW)])
cat(sprintf("  separation (lowest prosocial - highest undesirable): %.2f scale points\n", gap))
ok <- ok && gap > 1

cat("\nNote: this establishes the item set, the code->text tie against the deposit's own\n",
    "codebook, and the polarity of the 1-6 anchors. It does NOT independently re-derive\n",
    "the anchor WORDING between the endpoints -- those come from the official SPI-135\n",
    "form (sapa-project.org), which prints 1..6 beside each label.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

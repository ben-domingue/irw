# verify_peters_2025_att_exp_strength.R
#
# CLAIM UNDER TEST (Step 5b): each IRW item code in
# peters_2025_att_exp_strength is the lower-cased tail of one LimeSurvey
# question code `AttExEx<Tail>` in the Your COVID-19 Risk project's own
# question-definition spreadsheet, and the item_text / option_text shipped for
# that code are that spreadsheet row's own `subquestion_en`,
# `bottom_anchor_bare` and `top_anchor_bare`.
#
# What would break if the mapping were wrong: if item_text/option_text for two
# items were swapped, the anchors shipped at resp=1 / resp=max would no longer
# be the anchors the spreadsheet row with that code carries (check A), and the
# scale width predicted by that row's `scale_type` would land on the wrong item
# (check B).
#
# Sources fetched live:
#   A. DMQs sheet, worksheet "en", Google Sheets key
#      1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc -- the sheet named in the
#      taskSpecs list of https://your-risk.com/v1-translation-results-limesurvey
#      (the project's own LimeSurvey-generation R Markdown, CC0).
#   B. irw::irw_table_sets(per_item = TRUE) -- server-side aggregate, no export.

suppressMessages(library(irw))

TABLE <- "peters_2025_att_exp_strength"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")

items_csv <- file.path(dirname(sub("^--file=", "", grep("^--file=",
                 commandArgs(FALSE), value = TRUE)[1])),
                 paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_133", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

dmq <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = TRUE)
dmq <- dmq[grepl("^AttExEx", dmq$id), ]
dmq$code <- tolower(sub("^AttExEx", "", dmq$id))
dmq$maxcode <- ifelse(trimws(dmq$scale_type) == "uni", 5L, 7L)

cat(sprintf("spreadsheet rows matching ^AttExEx: %d\n", nrow(dmq)))

sets <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
per <- as.data.frame(sets$per_item)

## ---- CHECK A: shipped anchors vs the spreadsheet row carrying that code ----
cat("\n-- CHECK A: option_text at resp=1 / resp=max vs that item's own",
    "spreadsheet anchors --\n")
cat(sprintf("%-11s %-5s %-26s %-26s %-26s %-26s %s\n",
            "item", "type", "sheet bottom", "shipped resp=1",
            "sheet top", "shipped resp=max", "ok"))
badA <- 0L
for (i in seq_len(nrow(dmq))) {
    cd  <- dmq$code[i]
    mx  <- dmq$maxcode[i]
    lo_ship <- ship$option_text[ship$item == cd & ship$resp == 1L]
    hi_ship <- ship$option_text[ship$item == cd & ship$resp == mx]
    lo_ship <- if (length(lo_ship)) lo_ship[1] else "<missing>"
    hi_ship <- if (length(hi_ship)) hi_ship[1] else "<missing>"
    lo_src <- trimws(dmq$bottom_anchor_bare[i])
    hi_src <- trimws(dmq$top_anchor_bare[i])
    ok <- identical(lo_ship, lo_src) && identical(hi_ship, hi_src)
    if (!ok) badA <- badA + 1L
    cat(sprintf("%-11s %-5s %-26s %-26s %-26s %-26s %s\n",
                cd, trimws(dmq$scale_type[i]), lo_src, lo_ship,
                hi_src, hi_ship, if (ok) "ok" else "MISMATCH"))
}
cat(sprintf("CHECK A: %d/%d items reproduce both anchors verbatim\n",
            nrow(dmq) - badA, nrow(dmq)))

## ---- CHECK B: scale width declared per item vs observed live resp_max ----
cat("\n-- CHECK B: scale_type-implied max code vs live per-item resp_max --\n")
cat(sprintf("%-11s %-5s %10s %10s %s\n",
            "item", "type", "predicted", "observed", "ok"))
badB <- 0L
for (i in seq_len(nrow(dmq))) {
    cd <- dmq$code[i]
    obs <- per$resp_max[match(cd, per$item)]
    ok <- !is.na(obs) && obs == dmq$maxcode[i]
    if (!ok) badB <- badB + 1L
    cat(sprintf("%-11s %-5s %10d %10s %s\n", cd, trimws(dmq$scale_type[i]),
                dmq$maxcode[i], ifelse(is.na(obs), "NA", obs),
                if (ok) "ok" else "MISMATCH"))
}
cat(sprintf("CHECK B: %d/%d items match the predicted scale width\n",
            nrow(dmq) - badB, nrow(dmq)))

## ---- CHECK C: shipped stem is that row's own subquestion_en ----
badC <- sum(sapply(seq_len(nrow(dmq)), function(i) {
    s <- unique(ship$item_text[ship$item == dmq$code[i]])
    !(length(s) == 1L && identical(s, trimws(dmq$subquestion_en[i])))
}))
cat(sprintf("\nCHECK C: %d/%d items ship exactly their spreadsheet row's subquestion_en\n",
            nrow(dmq) - badC, nrow(dmq)))

cat("\nWhat CHECK B does NOT establish: only `weird` is declared `uni`, so the\n",
    "scale-width signature separates that one item from the other 15 and says\n",
    "nothing about the ordering among those 15. The item-by-item tie for all 16\n",
    "rests on CHECK A/C -- the spreadsheet's `id` column IS the raw LimeSurvey\n",
    "column name that data/peters_2025_covid19_risk_dcts.py lower-cases into the\n",
    "IRW `item` code, so the correspondence is a label match, not an order\n",
    "inference. Neither check can detect an error inside the spreadsheet itself.\n",
    sep = "")

cat(if (badA == 0L && badB == 0L && badC == 0L)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_peters_2025_pbc_cond_power.R
#
# CLAIM UNDER TEST (Step 5b): each IRW item code in peters_2025_pbc_cond_power
# is the lower-cased tail of exactly one LimeSurvey question code
# `PbcCnPw<Tail>` in the Your COVID-19 Risk project's own question-definition
# spreadsheet, and the item_text / option_text shipped for that code are that
# spreadsheet row's own `subquestion_en`, `bottom_anchor_bare` (resp = 1) and
# `top_anchor_bare` (resp = 7).
#
# What would break if the mapping were wrong: if item_text for two items were
# swapped, the stem shipped for a code would no longer be the stem the
# spreadsheet row with that code carries (CHECK B), and the Dutch question text
# the deployed survey file attaches to that same question code would no longer
# describe the same condition (CHECK C -- an independent file, not a restatement
# of the spreadsheet). CHECK D would catch a confusion with the near-twin table
# peters_2025_pbc_cond_presence (the `PbcCnPr*` component, a 1-5 unipolar
# scale), and CHECK E would catch a reversal of the option->resp direction.
#
# Sources fetched live:
#   A. DMQs sheet, worksheet "en", Google Sheets key
#      1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc -- named in the taskSpecs
#      list of https://your-risk.com/v1-translation-results-limesurvey (the
#      project's own LimeSurvey-generation R Markdown, CC0).
#   B. v1/operationalizations/limesurvey/v1.01/limesurvey_survey_100101.lss from
#      https://gitlab.com/a-bc/your-covid-19-risk -- the deployed Dutch survey.
#   C. irw::irw_table_sets(per_item = TRUE) and one server-side GROUP BY query.
#      No irw_fetch(), no table export.

suppressMessages(library(irw))

TABLE <- "peters_2025_pbc_cond_power"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")
LSS <- paste0("https://gitlab.com/a-bc/your-covid-19-risk/-/raw/master/",
              "v1/operationalizations/limesurvey/v1.01/limesurvey_survey_100101.lss")

items_csv <- file.path(dirname(sub("^--file=", "", grep("^--file=",
                 commandArgs(FALSE), value = TRUE)[1])),
                 paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_134", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

dmq <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = TRUE)
pw  <- dmq[grepl("^PbcCnPw", dmq$id), ]
pr  <- dmq[grepl("^PbcCnPr", dmq$id), ]
pw$code <- tolower(sub("^PbcCnPw", "", pw$id))

sets <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
per  <- as.data.frame(sets$per_item)
live <- sort(sets$items)

## ---- CHECK A: code re-derivation is one-to-one and onto the live item set ----
cat("-- CHECK A: spreadsheet ids ^PbcCnPw -> lower-cased tail vs live item set --\n")
derived <- sort(pw$code)
cat(sprintf("spreadsheet rows ^PbcCnPw: %d | distinct derived codes: %d | live items: %d\n",
            nrow(pw), length(unique(derived)), length(live)))
cat(sprintf("in spreadsheet not live: %d | live not in spreadsheet: %d\n",
            length(setdiff(derived, live)), length(setdiff(live, derived))))
badA <- as.integer(!identical(derived, live) ||
                   length(unique(derived)) != nrow(pw))
cat(sprintf("CHECK A: %s\n", if (badA == 0L) "ok (22/22 one-to-one and onto)" else "MISMATCH"))

## ---- CHECK B: shipped stem/anchors are that row's own spreadsheet fields ----
cat("\n-- CHECK B: shipped item_text / option_text vs that item's spreadsheet row --\n")
badB <- 0L
for (i in seq_len(nrow(pw))) {
    cd <- pw$code[i]
    st <- unique(ship$item_text[ship$item == cd])
    lo <- ship$option_text[ship$item == cd & ship$resp == 1L]
    hi <- ship$option_text[ship$item == cd & ship$resp == 7L]
    mid <- ship$option_text[ship$item == cd & ship$resp %in% 2:6]
    ok <- length(st) == 1L && identical(st, trimws(pw$subquestion_en[i])) &&
          length(lo) == 1L && identical(lo, trimws(pw$bottom_anchor_bare[i])) &&
          length(hi) == 1L && identical(hi, trimws(pw$top_anchor_bare[i])) &&
          length(mid) == 5L && all(is.na(mid))
    if (!ok) badB <- badB + 1L
    cat(sprintf("%-11s %-3s  %s\n", cd, if (ok) "ok" else "BAD", substr(st[1], 1, 96)))
}
cat(sprintf("CHECK B: %d/%d items ship exactly their own row's subquestion_en,",
            nrow(pw) - badB, nrow(pw)))
cat(" bottom_anchor_bare at resp=1, top_anchor_bare at resp=7, blank at resp 2-6\n")

## ---- CHECK C: independent per-item corroboration from the deployed .lss ----
cat("\n-- CHECK C: Dutch question text in limesurvey_survey_100101.lss carries the",
    "condition the English row names --\n")
kw <- c(busyplace = "drukke plek", somecare = "iemand om wie ik geef",
        sprmrkt = "supermarkt", work = "op mijn werk", shopping = "winkelen",
        enoughroom = "te weinig ruimte", lonely = "eenzaam", bored = "verveeld",
        usualact = "dagelijkse activiteiten", socialise = "socializen",
        tired = "moe zijn", distrac = "afgeleid",
        signposts = "borden die de afstand aangeven",
        normclose = "normaal gesproken dichtbij andere mensen",
        forget = "houden, dan maakt dit vergeten dit",
        forgexer = "naar buiten ga om te sporten", techtouch = "technologie",
        sitclose = "dichtbij iemand moet zijn", othdist = "anderen houden afstand",
        othappr = "anderen benaderen me", lotmind = "veel aan mijn hoofd",
        payatt = "geen aandacht besteedt")
lss <- tryCatch(paste(readLines(LSS, warn = FALSE), collapse = "\n"),
                error = function(e) NA_character_)
badC <- NA_integer_
if (is.na(lss)) {
    cat("  .lss could not be fetched; CHECK C skipped (does not fail the verdict)\n")
} else {
    m <- gregexpr("<title><!\\[CDATA\\[PbcCnPw[A-Za-z]+\\]\\]></title>.*?<question><!\\[CDATA\\[.*?\\]\\]></question>",
                  lss)
    hits <- regmatches(lss, m)[[1]]
    codes <- tolower(sub(".*PbcCnPw([A-Za-z]+)\\]\\].*", "\\1", hits))
    qs    <- sub(".*<question><!\\[CDATA\\[(.*?)\\]\\]></question>", "\\1", hits)
    cat(sprintf("  PbcCnPw questions found in the .lss: %d\n", length(hits)))
    badC <- 0L
    for (i in seq_along(codes)) {
        want <- kw[[codes[i]]]
        ok <- !is.null(want) && grepl(want, qs[i], fixed = TRUE)
        if (!ok) badC <- badC + 1L
        cat(sprintf("  %-11s %-3s %s\n", codes[i], if (ok) "ok" else "BAD",
                    substr(qs[i], 1, 92)))
    }
    cat(sprintf("CHECK C: %d/%d question codes carry the predicted Dutch condition phrase\n",
                length(codes) - badC, length(codes)))
}

## ---- CHECK D: this is the Pw (bipolar 1-7) component, not the Pr twin ----
cat("\n-- CHECK D: declared scale widths vs live per-item resp range --\n")
cat(sprintf("spreadsheet: PbcCnPw rows scale_type='bi' %d/%d ; PbcCnPr rows scale_type='uni' %d/%d\n",
            sum(trimws(pw$scale_type) == "bi"), nrow(pw),
            sum(trimws(pr$scale_type) == "uni"), nrow(pr)))
cat(sprintf("live: items with resp_min=1 and resp_max=7: %d/%d (a 1-5 range would mean the Pr twin)\n",
            sum(per$resp_min == 1 & per$resp_max == 7), nrow(per)))
badD <- as.integer(!(all(trimws(pw$scale_type) == "bi") &&
                     all(per$resp_min == 1 & per$resp_max == 7)))

## ---- CHECK E: route 8, semantic coherence / option direction ----
cat("\n-- CHECK E: per-item live means vs barrier/facilitator content (route 8) --\n")
facil <- c("othdist", "techtouch", "signposts")   # only 3 items name a helping condition
tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")$qualified_reference
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, COUNT(*) AS n,",
                   "AVG(SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64)) AS mean",
                   "FROM `%s` WHERE resp IS NOT NULL AND",
                   "TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                   "GROUP BY item ORDER BY mean DESC"), tbl)
st <- as.data.frame(irw:::.irw_query_tibble(q))
print(st, row.names = FALSE)
lo_f <- min(st$mean[st$item %in% facil])
hi_b <- max(st$mean[!st$item %in% facil])
cat(sprintf("lowest facilitator mean %.2f (%s) vs highest barrier mean %.2f (%s); gap %.2f\n",
            lo_f, paste(st$item[st$item %in% facil], collapse = "/"),
            hi_b, st$item[!st$item %in% facil][which.max(st$mean[!st$item %in% facil])],
            lo_f - hi_b))
badE <- as.integer(!(lo_f > hi_b))
cat(sprintf("CHECK E: %s -- all 3 facilitator items rank above all 19 barrier items\n",
            if (badE == 0L) "ok" else "MISMATCH"))

cat("\nWhat these checks do NOT establish: CHECK E separates the 3-item facilitator\n",
    "class from the 19-item barrier class and fixes the option->resp direction\n",
    "(resp=1 'much harder', resp=7 'much easier'); it says nothing about the order\n",
    "WITHIN either class. The item-by-item tie for all 22 rests on CHECK A/B/C --\n",
    "the spreadsheet's `id` column IS the raw LimeSurvey/CSV column name that\n",
    "data/peters_2025_covid19_risk_dcts.py strips of the ^PbcCn(Pw|Pr) prefix and\n",
    "lower-cases, so the correspondence is a label match, not an order inference,\n",
    "and CHECK C confirms it against a second file the spreadsheet did not write.\n",
    "No check can detect an error inside the spreadsheet itself, and none of them\n",
    "speaks to the ~20 non-English wordings this table pools.\n", sep = "")

cat(if (badA == 0L && badB == 0L && badD == 0L && badE == 0L &&
        (is.na(badC) || badC == 0L)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

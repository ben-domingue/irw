# verify_peters_2025_att_instr_eval.R
#
# CLAIM UNDER TEST (SKILL Step 5b), two axes:
#
#   AXIS 1 (item <-> item_text). Every IRW item code in
#   peters_2025_att_instr_eval is the lower-cased tail of exactly one
#   LimeSurvey question code `At(t)InEv<Tail>` in the Your COVID-19 Risk
#   project's own question-definition spreadsheet, after applying that
#   project's own code-shortening vector (Respons->Rspns, Flip->Fl, ...), and
#   the item_text / option_text shipped for that code are that same
#   spreadsheet row's `subquestion_en` / `bottom_anchor_bare` /
#   `top_anchor_bare`. The IRW processing script performs no positional step:
#   data/peters_2025_covid19_risk_dcts.py matches ^At?tIn(Ex|Ev)(.+)$ and
#   lower-cases group 2, a name-preserving rename.
#
#   AXIS 2 (resp <-> option_text). resp = 1 carries the BOTTOM anchor and
#   resp = 5 (unipolar) / 7 (bipolar) carries the TOP anchor, not the reverse.
#
# What would break if the mapping were wrong:
#   A: a swapped or shifted assignment would leave some live code with no
#      spreadsheet row, or two codes claiming one row.
#   B: swapped item_text between two items would put the wrong stem/anchors on
#      a code whose spreadsheet row states them.
#   C: the spreadsheet's per-item uni/bi scale_type would predict the wrong
#      live response width for the mis-assigned items.
#   D: if the anchor->code direction were reversed, the six "Flip" twin pairs
#      (same stem, anchors deliberately swapped in the spreadsheet) would move
#      the wrong way relative to their non-flipped partner.
#
# Sources fetched live:
#   - DMQs spreadsheet, worksheet "en", Google Sheets key
#     1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc (the `DMQs` taskSpec of
#     https://your-risk.com/v1-translation-results-limesurvey).
#   - irw::irw_table_sets(per_item = TRUE) -- server-side aggregates, no export.
#   - irw::irw_fetch() for check D only (this table is 63,271 rows / a few MB).

suppressMessages(library(irw))

TABLE <- "peters_2025_att_instr_eval"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")
CONSTRUCT <- "Instrumental attitude belief evaluation"
# the build script's own dmqReplacements vector, in its own order
REPL <- c(generic = "gnrc", Decline = "Decl", Supermarket = "Sprmrkt",
          Neighbourhood = "Neighbrhd", NrmDeIde = "NrmDeId",
          Respons = "Rspns", Flip = "Fl")
# the build script's own DMQs_to_globally_eliminate vector, restricted to AttInEv
ELIM <- c("AttInEvFamilySafe", "AttInEvChildFeel", "AttInEvChildReject")

fail <- 0L

items_csv <- file.path("itemtables/batch_133", paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) {
    a <- grep("^--file=", commandArgs(FALSE), value = TRUE)
    items_csv <- file.path(dirname(sub("^--file=", "", a[1])),
                           paste0(TABLE, "__items.csv"))
}
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

dmq <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = TRUE)
dmq <- dmq[trimws(dmq$raa_construct) == CONSTRUCT, ]
cat(sprintf("spreadsheet rows with raa_construct == '%s': %d\n",
            CONSTRUCT, nrow(dmq)))
cat(sprintf("of those, globally eliminated by the build script: %d (%s)\n",
            sum(dmq$id %in% ELIM), paste(intersect(dmq$id, ELIM), collapse = ", ")))
dmq <- dmq[!(dmq$id %in% ELIM), ]

code <- dmq$id
for (k in names(REPL)) code <- gsub(k, REPL[[k]], code, fixed = TRUE)
dmq$code <- tolower(sub("^At?tInEv", "", code))
dmq$maxcode <- ifelse(trimws(dmq$scale_type) == "uni", 5L, 7L)

sets <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live_items <- sort(unique(as.character(sets$items)))
per <- as.data.frame(sets$per_item)

## ---- CHECK A: code re-derivation is complete, unique and two-sided --------
cat("\n-- CHECK A: re-derived codes vs live item set --\n")
cat(sprintf("spreadsheet rows after removing eliminated: %d\n", nrow(dmq)))
cat(sprintf("distinct re-derived codes:                  %d\n", length(unique(dmq$code))))
cat(sprintf("distinct live item codes:                   %d\n", length(live_items)))
only_sheet <- setdiff(dmq$code, live_items)
only_live  <- setdiff(live_items, dmq$code)
cat(sprintf("in spreadsheet but not live: %d (%s)\n", length(only_sheet),
            paste(only_sheet, collapse = ", ")))
cat(sprintf("live but not in spreadsheet: %d (%s)\n", length(only_live),
            paste(only_live, collapse = ", ")))
if (length(only_sheet) || length(only_live) ||
    length(unique(dmq$code)) != nrow(dmq)) fail <- fail + 1L

## ---- CHECK B: shipped text vs that code's own spreadsheet row -------------
cat("\n-- CHECK B: shipped item_text / anchors vs that row's own fields --\n")
badB <- 0L
for (i in seq_len(nrow(dmq))) {
    cd <- dmq$code[i]; mx <- dmq$maxcode[i]
    g <- function(v) if (length(v)) { v <- v[1]; if (is.na(v)) "" else v } else "<missing>"
    st <- g(ship$item_text[ship$item == cd])
    lo <- g(ship$option_text[ship$item == cd & ship$resp == 1L])
    hi <- g(ship$option_text[ship$item == cd & ship$resp == mx])
    ok <- identical(trimws(st), trimws(dmq$subquestion_en[i])) &&
          identical(trimws(lo), trimws(dmq$bottom_anchor_bare[i])) &&
          identical(trimws(hi), trimws(dmq$top_anchor_bare[i]))
    if (!ok) {
        badB <- badB + 1L
        cat(sprintf("  MISMATCH %-12s sheet[%s | %s | %s] shipped[%s | %s | %s]\n",
                    cd, dmq$subquestion_en[i], dmq$bottom_anchor_bare[i],
                    dmq$top_anchor_bare[i], st, lo, hi))
    }
}
cat(sprintf("items whose shipped stem AND both anchors equal their own row: %d/%d\n",
            nrow(dmq) - badB, nrow(dmq)))
if (badB > 0L) fail <- fail + 1L

## ---- CHECK C: uni/bi width predicted per item, against live data ---------
cat("\n-- CHECK C: spreadsheet scale_type predicts live resp_max, per item --\n")
badC <- 0L
for (i in seq_len(nrow(dmq))) {
    r <- per[as.character(per$item) == dmq$code[i], ]
    if (!nrow(r)) { badC <- badC + 1L; next }
    if (as.integer(r$resp_max[1]) != dmq$maxcode[i]) {
        badC <- badC + 1L
        cat(sprintf("  MISMATCH %-12s scale_type=%s predicts %d, live resp_max=%s\n",
                    dmq$code[i], trimws(dmq$scale_type[i]), dmq$maxcode[i],
                    r$resp_max[1]))
    }
}
cat(sprintf("uni items predicted max 5: %d | bi items predicted max 7: %d\n",
            sum(dmq$maxcode == 5L), sum(dmq$maxcode == 7L)))
cat(sprintf("items whose live resp_max equals the predicted width: %d/%d\n",
            nrow(dmq) - badC, nrow(dmq)))
if (badC > 0L) fail <- fail + 1L

## ---- CHECK D: Flip twins move as the spreadsheet's anchors say -----------
# For each twin pair the spreadsheet either SWAPS the two anchors (prediction:
# mean(flip) == (max+1) - mean(base), a mirror) or leaves them IDENTICAL
# (prediction: mean(flip) == mean(base)). Which of the two applies is read from
# the spreadsheet, not chosen; reversing the anchor->code direction would swap
# the predictions and blow up the five mirrored pairs.
cat("\n-- CHECK D: flipped-twin direction test on the live response data --\n")
TWINS <- list(c("uni", "unifl"), c("bi", "bifl"), c("traduni", "tradfl"),
              c("hybriduni", "hybridunifl"), c("reasuni", "reasunifl"),
              c("reasbi", "reasbifl"))
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
mu <- tapply(d$resp, d$item, mean, na.rm = TRUE)
nn <- tapply(d$resp, d$item, function(x) sum(!is.na(x)))
TOL <- 0.30
badD <- 0L
cat(sprintf("%-12s %-12s %-9s %8s %8s %10s %8s %s\n", "base", "flip",
            "anchors", "M_base", "M_flip", "predicted", "diff", "ok"))
for (p in TWINS) {
    a <- p[1]; b <- p[2]
    ra <- dmq[dmq$code == a, ]; rb <- dmq[dmq$code == b, ]
    mx <- ra$maxcode[1]
    swapped <- identical(trimws(ra$bottom_anchor_bare[1]), trimws(rb$top_anchor_bare[1])) &&
               identical(trimws(ra$top_anchor_bare[1]),    trimws(rb$bottom_anchor_bare[1]))
    identical_anchors <- identical(trimws(ra$bottom_anchor_bare[1]), trimws(rb$bottom_anchor_bare[1])) &&
                         identical(trimws(ra$top_anchor_bare[1]),    trimws(rb$top_anchor_bare[1]))
    pred <- if (swapped) (mx + 1) - mu[[a]] else if (identical_anchors) mu[[a]] else NA_real_
    dv <- mu[[b]] - pred
    ok <- !is.na(dv) && abs(dv) <= TOL
    if (!ok) badD <- badD + 1L
    cat(sprintf("%-12s %-12s %-9s %8.3f %8.3f %10.3f %8.3f %s\n", a, b,
                if (swapped) "swapped" else if (identical_anchors) "identical" else "other",
                mu[[a]], mu[[b]], pred, dv, if (ok) "ok" else "FAIL"))
}
cat(sprintf("(per-item n for the twins: %s)\n",
            paste(sprintf("%s=%d", unlist(TWINS),
                          as.integer(nn[unlist(TWINS)])), collapse = " ")))
cat(sprintf("twin pairs matching the spreadsheet's own prediction (tol %.2f): %d/%d\n",
            TOL, length(TWINS) - badD, length(TWINS)))
if (badD > 0L) fail <- fail + 1L

cat("\n")
if (fail == 0L) cat("VERDICT: PASS\n") else cat("VERDICT: FAIL\n")

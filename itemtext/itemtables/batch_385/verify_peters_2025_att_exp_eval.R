# verify_peters_2025_att_exp_eval.R
#
# CLAIM UNDER TEST (Step 5b): each IRW item code in peters_2025_att_exp_eval is
# the lower-cased tail of one LimeSurvey question code `AttExEv<Tail>` in the
# Your COVID-19 Risk project's own question-definition spreadsheet (DMQs sheet,
# worksheet "en"), and the item_text / option_text shipped for that code are
# that row's own `subquestion_en`, `bottom_anchor_bare` (resp=1) and
# `top_anchor_bare` (resp=max).
#
# What would break if the mapping were wrong:
#   A. anchors at resp=1/resp=max would not equal the sheet row with that code;
#   B. the sheet's scale_type (uni = 1..5, bi = 1..7) would land on the wrong item;
#   C. the stem would differ from the row's subquestion_en;
#   D. POLARITY: the stem is "I prefer feeling ...", so each item's live mean
#      should sit on the side of the scale midpoint carrying the socially
#      desirable anchor (e.g. 'very good' top, 'very freaked out' top -> low).
#      If anchors were swapped between a positively- and negatively-poled item,
#      or the anchor direction reversed, the mean would land on the wrong side.
#
# Sources fetched live:
#   DMQs sheet key 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc (worksheet 'en'),
#   named in the taskSpecs of https://your-risk.com/v1-translation-results-limesurvey
#   irw::irw_table_sets(per_item=TRUE) and irw::irw_fetch() (uses the local irw cache).

suppressMessages(library(irw))

TABLE <- "peters_2025_att_exp_eval"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")

args <- grep("^--file=", commandArgs(FALSE), value = TRUE)
items_csv <- if (length(args)) file.path(dirname(sub("^--file=", "", args[1])),
                 paste0(TABLE, "__items.csv")) else ""
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_385", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

dmq <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = TRUE)
dmq <- dmq[grepl("^AttExEv", dmq$id), ]
dmq$code <- tolower(sub("^AttExEv", "", dmq$id))
dmq$maxcode <- ifelse(trimws(dmq$scale_type) == "uni", 5L, 7L)
cat(sprintf("spreadsheet rows matching ^AttExEv: %d (%s)\n", nrow(dmq),
            paste(dmq$code, collapse = ", ")))
live_items <- sort(unique(irw::irw_table_sets(TABLE, source = "core")$items))
absent <- setdiff(dmq$code, live_items)
cat("sheet codes absent from live table:", if (length(absent)) absent else "none", "\n")
dmq <- dmq[dmq$code %in% live_items, ]

per <- as.data.frame(irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)$per_item)

badA <- 0L; badB <- 0L; badC <- 0L
cat("\n-- CHECK A/B/C: anchors, scale width, stem vs that code's own sheet row --\n")
cat(sprintf("%-11s %-4s %-28s %-28s %4s %4s %s\n", "item", "type",
            "sheet bottom | shipped r=1", "sheet top | shipped r=max",
            "pred", "obs", "ok"))
for (i in seq_len(nrow(dmq))) {
    cd <- dmq$code[i]; mx <- dmq$maxcode[i]
    lo <- ship$option_text[ship$item == cd & ship$resp == 1L][1]
    hi <- ship$option_text[ship$item == cd & ship$resp == mx][1]
    okA <- identical(lo, trimws(dmq$bottom_anchor_bare[i])) &&
           identical(hi, trimws(dmq$top_anchor_bare[i]))
    obs <- per$resp_max[match(cd, per$item)]
    okB <- !is.na(obs) && obs == mx
    st <- unique(ship$item_text[ship$item == cd])
    okC <- length(st) == 1L && identical(st, trimws(dmq$subquestion_en[i]))
    badA <- badA + !okA; badB <- badB + !okB; badC <- badC + !okC
    cat(sprintf("%-11s %-4s %-28s %-28s %4d %4s %s\n", cd, trimws(dmq$scale_type[i]),
        paste(dmq$bottom_anchor_bare[i], "|", lo), paste(dmq$top_anchor_bare[i], "|", hi),
        mx, obs, if (okA && okB && okC) "ok" else "MISMATCH"))
}
cat(sprintf("CHECK A: %d/%d anchors verbatim; CHECK B: %d/%d scale widths; CHECK C: %d/%d stems\n",
            nrow(dmq) - badA, nrow(dmq), nrow(dmq) - badB, nrow(dmq),
            nrow(dmq) - badC, nrow(dmq)))

## ---- CHECK D: preference polarity ----
# Desirable pole per item, judged from the anchor pair (hard-coded prediction).
DESIRABLE_TOP <- c(altruistic = TRUE, comfort = FALSE, connected = TRUE,
    freakedout = FALSE, good = TRUE, incontrol = TRUE, leftout = FALSE,
    lonely = FALSE, safe = TRUE, silly = FALSE, socresp = TRUE,
    threatened = FALSE, upset = FALSE, vulnerable = FALSE, weird = FALSE)
d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)
badD <- 0L
cat("\n-- CHECK D: live mean vs scale midpoint, predicted from which anchor is desirable --\n")
cat(sprintf("%-11s %-28s %6s %6s %-6s %s\n", "item", "desirable anchor", "mid", "mean", "pred", "ok"))
for (cd in names(DESIRABLE_TOP)) {
    mx <- dmq$maxcode[dmq$code == cd]; mid <- (1 + mx) / 2
    anc <- if (DESIRABLE_TOP[[cd]]) ship$option_text[ship$item == cd & ship$resp == mx][1]
           else ship$option_text[ship$item == cd & ship$resp == 1L][1]
    ok <- if (DESIRABLE_TOP[[cd]]) m[[cd]] > mid else m[[cd]] < mid
    badD <- badD + !ok
    cat(sprintf("%-11s %-28s %6.1f %6.2f %-6s %s\n", cd, anc, mid, m[[cd]],
                if (DESIRABLE_TOP[[cd]]) "high" else "low", if (ok) "ok" else "MISMATCH"))
}
cat(sprintf("CHECK D: %d/%d items on the predicted side of the midpoint\n",
            length(DESIRABLE_TOP) - badD, length(DESIRABLE_TOP)))

cat("\nWhat these checks do NOT establish: B separates only `weird` (uni) from the\n",
    "other 14; D separates the 6 desirable-top items from the 9 desirable-bottom\n",
    "items and confirms anchor direction, but not order within each class. The\n",
    "item-by-item tie rests on A/C: the sheet's `id` IS the raw LimeSurvey column\n",
    "name that data/peters_2025_covid19_risk_dcts.py lower-cases into the IRW code\n",
    "(a label match, not an order inference). No check can detect an error inside\n",
    "the spreadsheet itself.\n", sep = "")

cat(if (badA + badB + badC + badD == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

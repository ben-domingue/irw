# Step 5b verification for peters_2025_nrm_inj_approval (batch_134).
#
# CLAIM UNDER TEST: each of the 10 live item codes carries the perceived-referent-
# approval stem of the SAME referent, taken from the study's own question-definition
# spreadsheet (DMQs Google Sheet key 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc,
# worksheet 'en'), i.e. boss -> "... my boss would ...", household -> "... people in
# my household would ...", and so on, with resp=1 the bottom anchor "strongly
# disapprove" and resp=7 the top anchor "strongly approve".
#
# ROUTE A (primary, label match / code re-derivation). The sheet's own `id` column
# holds the LimeSurvey question code. Applying the project's published code
# shortening (dmqReplacements, https://your-risk.com/v1-translation-results-limesurvey:
# Neighbourhood -> Neighbrhd) and then the IRW script's rename
# (data/peters_2025_covid19_risk_dcts.py, ^NrmIn(Ap|Mc)(.+)$ -> group(2).lower())
# must reproduce the live item set exactly, one-to-one and onto -- no order
# inference anywhere -- and the shipped item_text/option_text must equal that same
# sheet row's fields. This is what would break if two items' texts were swapped.
#
# ROUTE B (data-side corroboration, PARTIAL by construction). Injunctive-norm
# referents differ in applicability: not every respondent has a boss or colleagues,
# and the tool offered "(not applicable)" as answer code 0, which the IRW script
# drops. The two workplace referents must therefore have the fewest retained
# responses of the ten. This separates the {boss, colleagues} class from the other
# eight; it does NOT order items within either class.
#
# The script fetches the live item set and per-item n via irw::irw_table_sets()
# (server-side aggregate, no table export) and re-fetches the source sheet.

suppressMessages(library(irw))

TABLE <- "peters_2025_nrm_inj_approval"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")

items_csv <- file.path(dirname(sub("^--file=", "", grep("^--file=",
                 commandArgs(FALSE), value = TRUE)[1])),
                 paste0(TABLE, "__items.csv"))
if (is.na(items_csv) || !file.exists(items_csv))
    items_csv <- file.path("itemtables", "batch_134", paste0(TABLE, "__items.csv"))
shipped <- read.csv(items_csv, stringsAsFactors = FALSE)

sheet <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = FALSE)
ap <- sheet[grepl("^NrmInAp", sheet$id), ]

shorten <- function(x) {
  reps <- c(generic = "gnrc", Decline = "Decl", Supermarket = "Sprmrkt",
            Neighbourhood = "Neighbrhd", NrmDeIde = "NrmDeId",
            Respons = "Rspns", Flip = "Fl")
  for (k in names(reps)) x <- gsub(k, reps[[k]], x)
  x
}
ap$derived <- tolower(sub("^NrmInAp", "", shorten(ap$id)))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- sort(s$items)

cat("== ROUTE A: re-derive IRW item codes from the sheet's own question codes ==\n")
cat(sprintf("%-24s -> %-12s %-11s\n", "sheet id", "derived code", "in live set"))
for (i in order(ap$derived))
    cat(sprintf("%-24s -> %-12s %-11s\n", ap$id[i], ap$derived[i],
                ap$derived[i] %in% live))
missing_live  <- setdiff(live, ap$derived)
missing_sheet <- setdiff(ap$derived, live)
cat(sprintf("\nlive codes not derived from the sheet: %d %s\n",
            length(missing_live), paste(missing_live, collapse = " ")))
cat(sprintf("derived codes not in the live set:     %d %s\n",
            length(missing_sheet), paste(missing_sheet, collapse = " ")))
bijection <- length(missing_live) == 0 && length(missing_sheet) == 0 &&
             length(unique(ap$derived)) == length(live)

cat("\n-- shipped text vs the sheet row that derives to that code --\n")
ok_txt <- 0
for (i in order(ap$derived)) {
    code <- ap$derived[i]
    rows <- shipped[shipped$item == code, ]
    stem_ok <- length(unique(rows$item_text)) == 1 &&
               identical(unique(rows$item_text), ap$subquestion_en[i])
    bot <- rows$option_text[rows$resp == 1]
    top <- rows$option_text[rows$resp == 7]
    mid <- rows$option_text[!rows$resp %in% c(1, 7)]
    anch_ok <- identical(bot, ap$bottom_anchor_bare[i]) &&
               identical(top, ap$top_anchor_bare[i]) && all(is.na(mid))
    ok_txt <- ok_txt + (stem_ok && anch_ok)
    cat(sprintf("%-11s stem=%-5s anchors(1/7)=%-5s  %s\n", code, stem_ok, anch_ok,
                substr(ap$subquestion_en[i], 1, 62)))
}
cat(sprintf("\nitem_text + anchors equal to the sheet's own fields: %d/%d\n",
            ok_txt, nrow(ap)))

cat("\n== ROUTE B: workplace referents must lose the most respondents ==\n")
pi <- as.data.frame(s$per_item)
pi <- pi[order(pi$n), ]
for (k in seq_len(nrow(pi)))
    cat(sprintf("%-11s n=%5d\n", pi$item[k], pi$n[k]))
work <- c("boss", "colleagues")
route_b <- all(sort(pi$item[1:2]) == sort(work))
cat(sprintf("\ntwo smallest n are {boss, colleagues}: %s (%d, %d vs next %d)\n",
            route_b, pi$n[1], pi$n[2], pi$n[3]))

cat("\nWHAT THIS DOES NOT ESTABLISH: Route A is a label match against the study's\n",
    "own question-definition sheet, not a data-side test -- it proves the code\n",
    "re-derivation is exact and one-to-one and that the shipped strings are that\n",
    "sheet row's own fields, but it cannot detect an error inside the sheet itself.\n",
    "Route B is only a class separation: it pins {boss, colleagues} as the two\n",
    "workplace referents and does not order items within either class. Neither\n",
    "route tests the unlabelled midpoints resp=2..6 (shipped blank by design), nor\n",
    "the non-English administered wordings, which are not shipped.\n", sep = "")

pass <- bijection && ok_txt == nrow(ap) && route_b
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

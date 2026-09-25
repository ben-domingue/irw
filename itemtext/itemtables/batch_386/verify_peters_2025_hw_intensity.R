# verify_peters_2025_hw_intensity.R
#
# CLAIM UNDER TEST (Step 5b): each IRW item code in peters_2025_hw_intensity is
# the LimeSurvey answer-option code of the `hwIntensity` checkboxes question
# (raw export column hwIntensity.<code>., lower-cased by
# data/peters_2025_covid19_risk_precautions.py -- the codes are already lower
# case, so the rename is the identity), and the shipped item_text for that code
# is that option's own text_en in the project's REQs question-definition
# spreadsheet (worksheet 'en'); instructions is the question's own text_en.
#
# What would break if the mapping were wrong:
#   A. shipped item_text would not equal the text_en of the REQs row whose
#      ls_answer_code is that item (level-1 label match, per item);
#   B. the deployed LimeSurvey structure file (sid 100101, the Dutch survey)
#      would order its hwIntensity subquestion codes differently from the
#      sheet's ls_order (an independent second copy of code<->option);
#   C. MARKER ITEM (route 7): 'none' = "I don't do any of the above" must be
#      (i) the rarest option and (ii) the only option whose checkers almost
#      never check anything else. If its text sat on another code, that code
#      would show both properties instead;
#   D. route 8 plausibility (not decisive): soap (the minimal behaviour) should
#      be the most-endorsed substantive option, thrgh (the most demanding) the
#      least.
#
# Sources fetched live: REQs sheet key 1qMf-7khtWhHv8oBUa-yhsAvq8TCG5Nrc0t79OaqRLT0
# (named in the taskSpecs of https://your-risk.com/v1-translation-results-limesurvey);
# the .lss from gitlab.com/a-bc/your-covid-19-risk; irw::irw_fetch() (local irw cache).

suppressMessages(library(irw))

TABLE <- "peters_2025_hw_intensity"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1qMf-7khtWhHv8oBUa-yhsAvq8TCG5Nrc0t79OaqRLT0",
                "/gviz/tq?tqx=out:csv&sheet=en")
LSS <- paste0("https://gitlab.com/a-bc/your-covid-19-risk/-/raw/master/",
              "v1/operationalizations/limesurvey/v1.01/limesurvey_survey_100101.lss")

args <- grep("^--file=", commandArgs(FALSE), value = TRUE)
items_csv <- if (length(args)) file.path(dirname(sub("^--file=", "", args[1])),
                 paste0(TABLE, "__items.csv")) else ""
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_386", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

ok <- TRUE

## ---- CHECK A: label match against the REQs sheet ----
reqs <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = FALSE)
ao <- reqs[reqs$ls_question_code == "hwIntensity" & reqs$row_type == "answer_option", ]
qq <- reqs[reqs$ls_question_code == "hwIntensity" & reqs$row_type == "question", ]
ao$code <- tolower(ao$ls_answer_code)
live <- sort(unique(irw::irw_table_sets(TABLE, source = "core")$items))
cat("REQs hwIntensity answer options:", nrow(ao), "; live items:", length(live), "\n")
cat("sheet codes not live:", setdiff(ao$code, live), "| live codes not in sheet:",
    setdiff(live, ao$code), "\n")
if (!setequal(ao$code, live)) ok <- FALSE
cat("\n-- CHECK A: shipped item_text vs that code's own REQs row --\n")
nA <- 0L
for (i in seq_len(nrow(ao))) {
    st <- unique(ship$item_text[ship$item == ao$code[i]])
    m <- length(st) == 1L && identical(st, ao$text_en[i])
    nA <- nA + m
    cat(sprintf("%-6s ls_order=%s  sheet='%s'  shipped='%s'  %s\n", ao$code[i],
                ao$ls_order[i], ao$text_en[i], paste(st, collapse = "|"),
                if (m) "ok" else "MISMATCH"))
}
instr_ok <- identical(unique(ship$instructions), qq$text_en)
cat(sprintf("CHECK A: %d/%d item_text verbatim; instructions verbatim: %s\n",
            nA, nrow(ao), instr_ok))
if (nA != nrow(ao) || !instr_ok) ok <- FALSE

## ---- CHECK B: deployed .lss subquestion order vs sheet ls_order ----
cat("\n-- CHECK B: deployed LimeSurvey file (sid 100101, nl) --\n")
lss <- tryCatch(paste(readLines(LSS, warn = FALSE, encoding = "UTF-8"), collapse = "\n"),
                error = function(e) NA_character_)
if (is.na(lss)) {
    cat("could not fetch .lss -- CHECK B skipped (not counted as pass)\n"); ok <- FALSE
} else {
    rows <- regmatches(lss, gregexpr("<row>.*?</row>", lss))[[1]]
    fld <- function(r, f) sub(paste0(".*<", f, "><!\\[CDATA\\[(.*?)\\]\\]></", f, ">.*"), "\\1", r)
    par <- rows[grepl("<title><!\\[CDATA\\[hwIntensity\\]\\]>", rows) &
                grepl("<parent_qid><!\\[CDATA\\[0\\]\\]>", rows)]
    pqid <- unique(fld(par, "qid"))
    sub_rows <- rows[grepl(paste0("<parent_qid><!\\[CDATA\\[", pqid[1], "\\]\\]>"), rows)]
    sq <- unique(data.frame(code = fld(sub_rows, "title"),
                            ord = as.integer(fld(sub_rows, "question_order")),
                            text = fld(sub_rows, "question"), stringsAsFactors = FALSE))
    sq <- sq[order(sq$ord), ]
    print(sq, row.names = FALSE)
    sheet_order <- ao$code[order(as.integer(ao$ls_order))]
    b <- identical(tolower(sq$code), sheet_order)
    cat("sheet order:", sheet_order, "| lss order:", tolower(sq$code), "->", b, "\n")
    if (!b) ok <- FALSE
}

## ---- CHECK C: 'none' marker item ----
cat("\n-- CHECK C: marker item 'none' --\n")
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- tidyr::pivot_wider(d[, c("id", "item", "resp")], names_from = item, values_from = resp)
w <- as.data.frame(w); its <- c("durtn", "none", "soap", "thrgh")
cat("respondents:", nrow(w), "complete on all 4:", sum(complete.cases(w[, its])), "\n")
endorse <- sapply(its, function(x) mean(w[[x]]))
excl <- sapply(its, function(x) {
    sel <- w[[x]] == 1
    mean(rowSums(w[sel, setdiff(its, x), drop = FALSE]) == 0)
})
print(data.frame(item = its, n_checked = sapply(its, function(x) sum(w[[x]])),
                 p_checked = round(endorse, 4), p_checked_nothing_else = round(excl, 4)),
      row.names = FALSE)
cC <- names(which.min(endorse)) == "none" && names(which.max(excl)) == "none" &&
      excl["none"] > 0.9 && max(excl[its != "none"]) < 0.5
cat("rarest:", names(which.min(endorse)), "| most exclusive:", names(which.max(excl)),
    "| none exclusivity", round(excl["none"], 3), "vs max of others",
    round(max(excl[its != "none"]), 3), "->", cC, "\n")
if (!cC) ok <- FALSE

## ---- CHECK D: plausibility ordering (reported, not decisive) ----
cat("\n-- CHECK D (route 8, plausibility only): soap > durtn > thrgh --\n")
cD <- endorse["soap"] > endorse["durtn"] && endorse["durtn"] > endorse["thrgh"]
cat(sprintf("soap %.3f  durtn %.3f  thrgh %.3f -> %s\n",
            endorse["soap"], endorse["durtn"], endorse["thrgh"], cD))
if (!cD) ok <- FALSE

cat("\nWHAT THIS DOES NOT ESTABLISH: C pins only 'none'; D is an expectation about\n",
    "hand-washing behaviour, not a test that could separate a durtn/thrgh swap on\n",
    "its own. The per-item tie for durtn/soap/thrgh rests on the label match (A),\n",
    "corroborated by the deployed survey's own code order (B). Neither can detect\n",
    "an error inside the level-1 sheet itself.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

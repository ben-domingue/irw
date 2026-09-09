# verify_knight_2026_crt.R -- re-runnable Step 5b evidence.
#
# CLAIM: the live item codes CRT1..CRT7 carry the seven CRT question wordings in
# the order they appear in the study's own Qualtrics survey file (.qsf) and in the
# "Cognitive Reflection Test Confidence Task.docx" materials (questions 1-7).
#
# Route: explicit code labels (the .qsf's DataExportTag literally IS "CRT1".."CRT7",
# each carrying its QuestionText), corroborated by a response-time load partition.
#
# Data source note: this script reads the OSF deposit's own TED_CRT_longdata.csv --
# the exact file data/knight_2026_crt.py converts -- rather than irw::irw_fetch(),
# because a full fetch exports the whole table against the shared 200GB/30d Redivis
# quota and adds nothing here (the IRW table is a straight rename of these columns:
# CRTn->item, CRTc_dum->resp, exp(logRT)->rt).

QSF  <- "https://osf.io/download/vfg6m/"                      # Materials/...Survey.qsf
LONG <- "https://osf.io/download/6952a2e6900cc63c0411d38f/"   # TED_CRT_longdata.csv

ok <- TRUE

## --- 1. code -> text tie, straight out of the .qsf ---------------------------
qsf <- tryCatch(jsonlite::fromJSON(QSF, simplifyVector = FALSE), error = function(e) NULL)
if (is.null(qsf)) {
    cat("could not fetch the .qsf (network?); label check SKIPPED\n")
    ok <- FALSE
} else {
    strip <- function(x) {
        x <- gsub("<[^>]+>", " ", x)
        x <- gsub("&nbsp;", " ", x, fixed = TRUE)
        trimws(gsub("[[:space:]]+", " ", x))
    }
    tags <- list()
    for (e in qsf$SurveyElements) {
        if (!identical(e$Element, "SQ")) next
        tg <- e$Payload$DataExportTag
        if (!is.null(tg) && grepl("^CRT[1-7]$", tg))
            tags[[tg]] <- strip(e$Payload$QuestionText)
    }
    shipped <- read.csv("itemtables/batch_063/knight_2026_crt__items.csv",
                        colClasses = "character")
    shipped <- unique(shipped[, c("item", "item_text")])
    cat("-- .qsf DataExportTag -> QuestionText vs shipped item_text --\n")
    for (i in 1:7) {
        code <- paste0("CRT", i)
        a <- tags[[code]]
        b <- shipped$item_text[shipped$item == code]
        agree <- identical(a, b)
        ok <- ok && agree
        cat(sprintf("%-5s %-6s %s\n", code, if (agree) "MATCH" else "DIFFER",
                    substr(a, 1, 62)))
    }
}

## --- 2. corroboration: response-time load partition --------------------------
## The three items requiring multi-step computation or a long passage (CRT4 two-rate
## work problem, CRT6 four-step buy/sell arithmetic, CRT7 76-word stock vignette)
## must take materially longer than the four one-line single-inference items
## (CRT1, CRT2, CRT3, CRT5). Under a random permutation of the seven wordings the
## chance of that exact 3/4 split is 1/choose(7,3) = 0.029.
d <- tryCatch(read.csv(LONG), error = function(e) NULL)
if (is.null(d)) {
    cat("could not fetch TED_CRT_longdata.csv; RT check SKIPPED\n")
    ok <- FALSE
} else {
    d$rt <- exp(d$logRT)
    med <- tapply(d$rt, d$CRTn, median, na.rm = TRUE)
    acc <- tapply(d$CRTc_dum == "Correct", d$CRTn, mean, na.rm = TRUE)
    cat("\n-- per-item median RT (s) and proportion correct --\n")
    for (code in paste0("CRT", 1:7))
        cat(sprintf("%-5s med_rt %6.2f   p(correct) %.3f\n", code, med[[code]], acc[[code]]))
    heavy <- c("CRT4", "CRT6", "CRT7"); light <- c("CRT1", "CRT2", "CRT3", "CRT5")
    gap <- min(med[heavy]) - max(med[light])
    cat(sprintf("\nmin(high-load %s) = %.2f s ; max(one-line %s) = %.2f s ; gap = %.2f s\n",
                paste(heavy, collapse = "/"), min(med[heavy]),
                paste(light, collapse = "/"), max(med[light]), gap))
    ok <- ok && gap > 0
}

cat("\nNot established by either check: that TED_CRT_longdata.csv's CRTn strings were\n",
    "inherited from the Qualtrics export tags rather than reassigned when the long file\n",
    "was built (no raw CRT columns are in the deposit). The RT partition separates the\n",
    "three high-load items from the four one-line items but does not order items within\n",
    "either group. Status is recorded as PARTIAL for that reason.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

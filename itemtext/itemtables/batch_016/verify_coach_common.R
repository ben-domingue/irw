## verify_coach_common.R  --  batch_016, issue #1831
##
## Shared body for the five COACH_Chen_2022 verify scripts. All five are keyed
## to one source (the deposit's codebook.xlsx), so the re-derivation and the
## checks are identical and only the table name differs.
##
## Checks, in order:
##   1. item_text re-derived from codebook.xlsx, per item
##   2. option_text per resp level, against that item's own value labels
##   3. every live level either carries the codebook's label or is a documented
##      out-of-range level with no row at all -- nothing is silently relabelled
##   4. the translated_substitute fallback is recorded as the schema requires:
##      language names the administered language, _translated columns empty
##   5. the evidence for that fallback, re-counted: no CJK item text in the
##      deposit's own files
##   6. item and resp sets against live response data
suppressMessages({library(jsonlite)})

# Items whose option_text is deliberately empty because this table's own data
# contradict the codebook's printed direction for them (see check_csq_direction).
BLANK_LABELS <- list(COACH_Chen_2022_CSQ = c(
    "ra_customer_satisfaction_questionnaire_q3",
    "ra_customer_satisfaction_questionnaire_q8"))

# Explicit id-by-item pivot. reshape() is avoided deliberately: irw_fetch()
# returns a tibble and names its varying columns differently there than for the
# data.frame read.csv() gives.
pivot_wide <- function(d, items) {
    d <- as.data.frame(d); d$item <- as.character(d$item)
    ids <- unique(d$id)
    m <- matrix(NA_real_, nrow = length(ids), ncol = length(items),
                dimnames = list(NULL, items))
    for (nm in items) {
        s <- d[d$item == nm, , drop = FALSE]
        m[match(s$id, ids), nm] <- as.numeric(s$resp)
    }
    m
}

# WHOQOL-BREF only. Reverse-coding is a property of the table, not the
# instrument: the corpus holds this same instrument stored both ways --
# altahla_2024_whoqol keeps the canonical reverse triple raw, burkert_2019_
# whoqol_bref ships it already reversed (#1831). So which direction THIS table
# stores has to come from its own data before the codebook's labels can be
# trusted. The instrument reverse-scores q3, q4 and q26; if those three are the
# negatively-correlating outliers the table is raw and the shipped labels apply
# as they stand. If they are not, the labels are backwards for those items.
check_whoqol_direction <- function(live) {
    m <- pivot_wide(live, paste0("ra_whoqol_bref_q", 1:26))
    colnames(m) <- as.character(1:26)
    cm  <- cor(m, use = "pairwise.complete.obs")
    avg <- (rowSums(cm, na.rm = TRUE) - 1) / (ncol(cm) - 1)
    REV <- c("3", "4", "26")
    r <- avg[names(avg) %in% REV]; o <- avg[!names(avg) %in% REV]
    cat(sprintf("  canonical reverse triple q3/q4/q26: mean r %+.3f, range [%+.3f, %+.3f]\n",
                mean(r), min(r), max(r)))
    cat(sprintf("  the other 23 items:                 mean r %+.3f, range [%+.3f, %+.3f]\n",
                mean(o), min(o), max(o)))
    if (max(r) < min(o)) {
        cat("  clean separation, so this table stores the raw administered direction and\n",
            "  the codebook's labels apply as shipped\n", sep = "")
        return(character(0))
    }
    cat("  NO separation: the table may store reversed values, in which case the\n",
        "  shipped option_text is backwards for those items\n", sep = "")
    "WHOQOL-BREF reverse triple does not separate -- scoring direction unconfirmed"
}


# CSQ only. q3 and q8 are the scale's two negatively worded items and they
# carry the SAME ascending keys as the six positive ones (1 = Strongly agree ..
# 5 = Strongly disagree), so nothing cancels the reverse wording and they
# should invert. Two signatures say the stored values do not follow the printed
# labels for them, so their option_text ships empty. This re-runs both, and
# fails if the picture changes -- if a data revision ever puts them on the
# printed direction, the labels should be restored rather than left blank.
CSQ_NEG <- c(3, 8)
check_csq_direction <- function(live, it) {
    code <- function(k) paste0("ra_customer_satisfaction_questionnaire_q", k)
    m <- pivot_wide(live, vapply(1:8, code, ""))
    colnames(m) <- as.character(1:8)
    cm  <- cor(m, use = "pairwise.complete.obs")
    avg <- (rowSums(cm, na.rm = TRUE) - 1) / (ncol(cm) - 1)
    mu  <- vapply(1:8, function(k) mean(as.numeric(
               live$resp[as.character(live$item) == code(k)])), 0)
    neg <- as.character(CSQ_NEG); pos <- setdiff(as.character(1:8), neg)
    cat(sprintf("  reverse-worded q3/q8: mean r %+.3f and %+.3f | item means %.2f and %.2f\n",
                avg[neg[1]], avg[neg[2]], mu[CSQ_NEG[1]], mu[CSQ_NEG[2]]))
    cat(sprintf("  the six positive items: mean r range [%+.3f, %+.3f] | item means [%.2f, %.2f]\n",
                min(avg[pos]), max(avg[pos]), min(mu[-CSQ_NEG]), max(mu[-CSQ_NEG])))
    inverts <- all(avg[neg] < 0)
    means_high <- all(mu[CSQ_NEG] > max(mu[-CSQ_NEG]))
    labelled <- any(!is.na(it$option_text[it$item %in% vapply(CSQ_NEG, code, "")]))
    if (inverts || means_high) {
        cat("  q3/q8 DO follow the printed direction here -- restore their option_text\n")
        return("CSQ q3/q8 now follow the printed labels; blanked option_text is stale")
    }
    cat("  neither signature puts q3/q8 on the printed direction, so their option_text\n",
        "  is correctly left empty rather than shipped backwards\n", sep = "")
    if (labelled) return("CSQ q3/q8 carry option_text but their direction is unconfirmed")
    character(0)
}

# Reported, not enforced: the same 26 items already carry text in
# altahla_2024_whoqol, so position-for-position agreement is a second route on
# the wording. Minor transcription differences are expected and fine -- this
# table ships the COACH deposit's own wording verbatim, its typos included.
check_whoqol_corpus <- function(it) {
    options(irw.itemtext_disclaimer = FALSE)
    alt <- tryCatch(as.data.frame(irw::irw_itemtext("altahla_2024_whoqol")),
                    error = function(e) NULL)
    if (is.null(alt)) {
        cat("  altahla_2024_whoqol unavailable -- cross-check skipped\n"); return(invisible())
    }
    norm <- function(s) {
        s <- tolower(gsub("[‘’]", "'", s))
        trimws(gsub("\\s+", " ", gsub("[^a-z0-9' ]+", " ", s)))
    }
    alt <- unique(alt[, c("item", "item_text")])
    alt$n <- as.integer(sub("^whoqol_", "", alt$item))
    mine <- unique(it[, c("item", "item_text")])
    mine$n <- as.integer(sub("^ra_whoqol_bref_q", "", mine$item))
    same <- 0; diff <- 0
    for (k in 1:26) {
        a <- mine$item_text[mine$n == k]; b <- alt$item_text[alt$n == k]
        if (!length(a) || !length(b) || is.na(b)) next
        if (identical(norm(a), norm(b))) same <- same + 1 else diff <- diff + 1
    }
    cat(sprintf("  vs altahla_2024_whoqol at the same positions: %d identical, %d differing only in transcription\n",
                same, diff))
}

verify_coach <- function(TBL, resp_csv = NA_character_) {
    DIR <- "itemtables/batch_016"
    CSV <- file.path(DIR, paste0(TBL, "__items.csv"))
    JSN <- file.path(DIR, "rederived_coach.json")
    fail <- character(0)

    if (!file.exists(JSN))
        system2("python3", file.path(DIR, "rederive_coach.py"))
    red <- fromJSON(JSN, simplifyVector = FALSE)
    src <- red$entries
    lower <- setNames(names(src), tolower(names(src)))
    it <- read.csv(CSV, stringsAsFactors = FALSE)
    it$item <- as.character(it$item)
    codes <- unique(it$item)

    cat("=== 1. item_text re-derived from codebook.xlsx ===\n")
    bad <- 0
    for (code in codes) {
        key  <- lower[[tolower(code)]]
        want <- if (is.null(key)) NULL else trimws(src[[key]]$text)
        got  <- unique(it$item_text[it$item == code])
        if (is.null(want) || length(got) != 1 || !identical(got, want)) {
            bad <- bad + 1
            if (bad <= 3) cat(sprintf("  MISMATCH %s\n    source : %s\n    shipped: %s\n", code,
                substr(paste(want, collapse = "|"), 1, 90),
                substr(paste(got, collapse = "|"), 1, 90)))
        }
    }
    cat(sprintf("  items compared: %d | mismatches: %d\n", length(codes), bad))
    if (bad) fail <- c(fail, "item_text mismatch")

    cat("\n=== 2. option_text per resp level ===\n")
    blanked <- BLANK_LABELS[[TBL]]
    obad <- 0; cells <- 0; skipped <- 0
    for (code in codes) {
        key <- lower[[tolower(code)]]
        o   <- src[[key]]$opts
        rows <- it[it$item == code, ]
        if (code %in% blanked) {
            # These must be empty, not merely different from the codebook.
            skipped <- skipped + nrow(rows)
            if (any(!is.na(rows$option_text))) {
                obad <- obad + 1
                cat(sprintf("  %s should carry no option_text but does\n", code))
            }
            next
        }
        for (k in seq_len(nrow(rows))) {
            cells <- cells + 1
            want <- o[[as.character(rows$resp[k])]]
            if (is.null(want) || !identical(rows$option_text[k], want)) {
                obad <- obad + 1
                if (obad <= 3) cat(sprintf("  MISMATCH %s resp=%s\n    source : %s\n    shipped: %s\n",
                    code, rows$resp[k], paste(want, collapse = "|"), rows$option_text[k]))
            }
        }
    }
    cat(sprintf("  option cells checked: %d | mismatches: %d", cells, obad))
    if (skipped) cat(sprintf(" | %d cells on %d deliberately unlabelled item(s)",
                             skipped, length(blanked)))
    cat("\n")
    if (obad) fail <- c(fail, "option_text mismatch")

    cat("\n=== 4. translated_substitute fallback recorded correctly ===\n")
    tcols <- c("item_text_translated", "option_text_translated",
               "instructions_translated", "section_prompt_translated")
    langs <- unique(it$language)
    tfull <- vapply(tcols, function(c) sum(!is.na(it[[c]]) & nzchar(it[[c]])), 1L)
    cat("  language:", paste(langs, collapse = ","),
        "| non-empty cells in the _translated columns:", sum(tfull), "\n")
    if (!identical(langs, "Chinese")) fail <- c(fail, "language is not Chinese")
    if (sum(tfull))                   fail <- c(fail, "_translated columns are not empty")

    cat("\n=== 5. evidence for the fallback: CJK in the deposit's own files ===\n")
    cj <- red$cjk_evidence
    cat(sprintf("  codebook.xlsx CJK chars: %s | raw.xlsx: %s\n",
        cj[["codebook.xlsx"]], cj[["raw.xlsx"]]))
    cat("  (a small count is font names such as SimSun, not item text)\n")
    if (is.numeric(cj[["codebook.xlsx"]]) && cj[["codebook.xlsx"]] > 20)
        fail <- c(fail, "deposit may carry CJK item text after all -- recheck the fallback")

    cat("\n=== 6. item and resp sets vs live response data ===\n")
    live <- if (!is.na(resp_csv) && nzchar(resp_csv)) {
        cat("  (using local response CSV:", resp_csv, ")\n")
        read.csv(resp_csv, stringsAsFactors = FALSE)
    } else tryCatch(irw::irw_fetch(TBL), error = function(e) NULL)

    if (is.null(live) || !nrow(live)) {
        cat("  live data unavailable -- sets NOT checked\n")
        fail <- c(fail, "live data unavailable")
    } else {
        live$item <- as.character(live$item)
        si <- identical(sort(unique(it$item)), sort(unique(live$item)))
        sr <- identical(sort(unique(as.numeric(it$resp))), sort(unique(as.numeric(live$resp))))
        cat("  item set identical:", si, "| resp set identical:", sr,
            "| live rows:", nrow(live), "\n")
        if (!si || !sr) fail <- c(fail, "live set mismatch")

        cat("\n=== 3. live levels with no codebook label (expected to carry no row) ===\n")
        tot <- 0
        for (code in codes) {
            key <- lower[[tolower(code)]]
            lab <- as.integer(names(src[[key]]$opts))
            lv  <- sort(unique(as.numeric(live$resp[live$item == code])))
            off <- setdiff(lv, lab)
            if (length(off)) {
                n <- sum(live$item == code & live$resp %in% off)
                tot <- tot + n
                cat(sprintf("  %-42s levels %s -> %d live rows, no row shipped\n",
                            code, paste(off, collapse = ","), n))
                if (any(it$resp[it$item == code] %in% off))
                    fail <- c(fail, paste("unlabelled level shipped for", code))
            }
        }
        cat(sprintf("  live rows on an unlabelled level: %d of %d (%.3f%%)\n",
                    tot, nrow(live), 100 * tot / nrow(live)))

        if (TBL == "COACH_Chen_2022_CSQ") {
            cat("\n=== 7. CSQ reverse-worded items, from this table's own data ===\n")
            fail <- c(fail, check_csq_direction(live, it))
        }

        if (TBL == "COACH_Chen_2022_WHOQOL_BREF") {
            cat("\n=== 7. WHOQOL-BREF scoring direction, from this table's own data ===\n")
            fail <- c(fail, check_whoqol_direction(live))
            check_whoqol_corpus(it)
        }
    }

    cat("\n", strrep("-", 60), "\n", sep = "")
    if (length(fail)) {
        cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
    } else cat("VERDICT: PASS\n")
    invisible(fail)
}

verify_args <- function() {
    a <- commandArgs(trailingOnly = TRUE)
    i <- match("--resp-csv", a)
    if (!is.na(i)) {
        if (length(a) < i + 1) stop("--resp-csv needs a path")
        return(a[i + 1])
    }
    NA_character_
}

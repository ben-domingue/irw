# Usage: Rscript lint_verification.R <batch_dir> [<batch_dir> ...]
#        Rscript lint_verification.R mapping_verification.csv
#
# Checks the mapping-verification records for the failure mode that neither
# validate_items.R nor audit_batch.R can see: a status that claims more than its
# own evidence supports.
#
# The status field is self-reported by the agent that did the work, and it
# inflates. bang_2023_self_esteem shipped as VERIFIED while its evidence string
# said, in its own words, that the routes pin polarity class and the position of
# one item but NOT the order within each polarity block -- i.e. PARTIAL. Nothing
# downstream catches that, because a wrong mapping still passes every set-level
# check. Hence this lint.
#
# VERIFIED means: the route distinguishes every item from every other item.
# If it only pins a class, a block, a subscale, a direction, or a subset of
# positions, that is PARTIAL, however strong the evidence for what it does pin.

args <- commandArgs(trailingOnly = TRUE)
if (!length(args)) stop("Usage: Rscript lint_verification.R <batch_dir|csv> [...]")

VALID <- c("VERIFIED", "PARTIAL", "NO_ROUTE", "NOT_NEEDED")

# Phrases that describe a limit on what was established. Their presence in a
# row claiming VERIFIED is the signal this lint exists to catch.
# Deliberately narrow. Words like "ambiguous" or "underpowered" appear in good
# evidence describing a RIVAL route that failed, so matching them produced mostly
# false positives on the existing corpus. These phrases instead describe a limit
# on what the row itself established.
HEDGE <- paste0(
    "not independently (excluded|confirmed|verified)|",
    "(are|is|were|was) not excluded|cannot be excluded|",
    "not the order|but not the order|",
    "not (the )?order within|",
    "rests on (an|the) assumption|is an assumption|",
    "could not be (confirmed|verified|established)|",
    "(does not|do not|did not) (establish|settle|pin)|",   # see WORDING_OBJECT below
    "(remain|remains|are|is) unconfirmed|",
    "only pins|pins only|verifies .* not ")

# Step 5b verifies the code-to-item MAPPING. A good evidence string routinely ends by
# saying the numeric route cannot speak to the WORDING -- "what this does NOT establish
# is the words", "no numeric route can check a translation" -- which is true, in scope
# for the note and out of scope for the status. Matching it produced a WARN that was
# hand-adjudicated and dismissed in five consecutive batches (024, 026, 027, 028, 029,
# 030) and accounted for 31 of the corpus's 40 WARNs, which is how a check stops being
# read. See ben-domingue/irw#1966.
#
# So a "does not establish" hit is discarded when what follows names the wording rather
# than the mapping. Deliberately a short window: the object of the verb sits within a
# clause of it, and a wider window would start swallowing genuine hedges that merely
# happen to mention text later in the paragraph.
WORDING_OBJECT <- "(word|wording|words|translat|text|language|phrasing|anchor|option)"
WORDING_WINDOW <- 80L

# THE ITEM-AXIS RULE (Ben, 2026-09-08). VERIFIED means one route pins every item
# to its code. A hedge about what some OTHER route, or some upstream source, could
# not confirm does not weaken that -- so it must not pull the status down.
#
# This came out of six rows (jiang_2021_resilience, jo_2023_arp, kalichman1995_scs,
# kushnir2017_bfi, latifi_2026_insect_fear, li_2025_marketing_operation) that all
# WARNed on the same phrase, "does not establish", while none of them hedged about
# the item axis at all. They split two ways, and neither shape is PARTIAL:
#   - the hedge scopes a SECONDARY route that is not load-bearing. jiang_2021 says
#     route 1 could not separate C4-C8 (published means within 0.04) -- and in the
#     same sentence, that those items are pinned by Table 4's printed code labels.
#     latifi_2026 says it outright: the within-block separation "rests entirely on
#     the Q-code label match above, which is why the status is VERIFIED".
#   - the hedge scopes an upstream fact NO route could ever settle: whether the
#     authors' own appendix table is correctly labelled (jo_2023_arp), whether a
#     codebook's Q-numbering matches the published scale's order (kalichman1995).
#
# So the discard is conditional on the row SAYING, positively, that every item is
# separated -- it is not enough for the hedge to look harmless. The phrases below
# are each taken from one of the six; a row that cannot assert one of them still
# WARNs, which is what keeps bang_2023_self_esteem's shape (routes pin a polarity
# BLOCK but not the order within it, the failure this lint was written for) caught.
#
# Kept visible rather than silenced: a cleared row prints as INFO naming the phrase
# it relied on, so an agent cannot quietly buy VERIFIED with a stock sentence.
SEPARATION <- paste0(
    "every item is (separated|distinguished) from every other|",
    "distinguishes every item|",
    "identity bijection|",
    "discriminates the items|",
    "excluded per item|",
    "string for string|",
    "code[- ]label match|",
    "tied at the source|",
    "(0|no) mismatches")

# A SEPARATE SIGNAL, not part of the status question (Ben, 2026-09-08). jo_2023_arp
# is VERIFIED on its item axis and ships option_text blank because the study
# publishes no anchors. That is a real gap in what IRW ships, and folding it into
# "should this be PARTIAL?" buried it -- the status is about the item axis, so it
# gets its own flag. Deliberately narrow: it fires on option_text being BLANK or
# UNVERIFIED, not on a route merely declining to test it (li_2025_marketing_operation
# does not test the axis but rests it on the .sav's own value labels, which is a
# mapping at the source, not a gap).
OPTION_GAP <- "option_text[^.]{0,80}(ships blank|is blank|unverified|not verified)"

drop_wording_hedges <- function(ev, hits) {
    if (!length(hits)) return(hits)
    keep <- vapply(hits, function(h) {
        starts <- gregexpr(h, ev, fixed = TRUE)[[1]]
        # keep the hit if ANY of its occurrences is about something other than wording
        any(vapply(starts, function(st) {
            tail <- substr(ev, st, st + nchar(h) + WORDING_WINDOW)
            !grepl(WORDING_OBJECT, tail, ignore.case = TRUE)
        }, logical(1)))
    }, logical(1))
    hits[keep]
}

# Batches requested but skipped for want of a verification file. A skip used to
# be a bare message(), which meant an unverified batch passed this gate by being
# INVISIBLE rather than by being checked -- and linted alongside a batch that did
# have a file, the run still reported success. Collected and reported as ERROR
# flags below instead. See ben-domingue/irw#1736.
skipped <- character(0)

read_one <- function(a) {
    p <- if (dir.exists(a)) file.path(a, "verification_merged.csv") else a
    if (!file.exists(p)) {
        skipped <<- c(skipped, a)
        message("skipping ", a, " -- no verification file")
        return(NULL)
    }
    d <- read.csv(p, stringsAsFactors = FALSE)
    d$..src <- p
    d$..dir <- if (dir.exists(a)) a else NA_character_
    d
}
v <- do.call(rbind, Filter(Negate(is.null), lapply(sub("/$", "", args), read_one)))
if (is.null(v) || !nrow(v))
    stop("nothing to lint -- no verification rows were found in: ",
         paste(sub("/$", "", args), collapse = ", "),
         "\n  A batch directory is linted via its verification_merged.csv; batches that record",
         "\n  their rows only in the central itemtext/mapping_verification.csv must be linted by",
         "\n  passing that file's path instead. Nothing was checked.", call. = FALSE)

flags <- list()
add <- function(sev, table, msg) flags[[length(flags) + 1]] <<- list(sev = sev, table = table, msg = msg)

for (i in seq_len(nrow(v))) {
    r <- v[i, ]
    st <- toupper(trimws(r$status))
    ev <- if (is.na(r$evidence)) "" else r$evidence

    if (!st %in% VALID) add("ERROR", r$table, sprintf("status '%s' is not one of %s",
                                                      r$status, paste(VALID, collapse = "/")))

    if (st == "VERIFIED") {
        hits <- regmatches(ev, gregexpr(HEDGE, ev, ignore.case = TRUE))[[1]]
        hits <- drop_wording_hedges(ev, hits)
        sep  <- unique(tolower(regmatches(ev, gregexpr(SEPARATION, ev, ignore.case = TRUE))[[1]]))
        if (length(hits) && length(sep)) {
            add("INFO", r$table,
                sprintf("evidence hedges (%s) but asserts a full item-axis tie (%s) -- VERIFIED stands per the 2026-09-08 item-axis rule",
                        paste(unique(tolower(hits)), collapse = ", "),
                        paste(sep, collapse = ", ")))
            hits <- character(0)
        }
        if (length(hits))
            add("WARN", r$table, sprintf("VERIFIED but its evidence hedges (%s) -- should this be PARTIAL?",
                                          paste(unique(tolower(hits)), collapse = ", ")))
        if (!grepl("[0-9]", ev))
            add("WARN", r$table, "VERIFIED but the evidence contains no numbers; Step 5b requires the actual values compared")
    }

    if (st %in% c("VERIFIED", "PARTIAL") && grepl(OPTION_GAP, ev, ignore.case = TRUE))
        add("WARN", r$table,
            "evidence says option_text ships blank or unverified -- the item axis may be sound, but the response-option wording is a gap in what IRW ships")

    if (st == "NOT_NEEDED" && !identical(trimws(r$mapping_basis), "data_labels"))
        add("WARN", r$table, sprintf("NOT_NEEDED but mapping_basis is '%s'; only data_labels is exempt from Step 5b",
                                      r$mapping_basis))

    if (st %in% c("VERIFIED", "PARTIAL") && nchar(trimws(ev)) < 40)
        add("WARN", r$table, sprintf("%s on %d characters of evidence -- too thin to re-check", st, nchar(trimws(ev))))
}

# Every shipped CSV should have a row.
for (d in unique(na.omit(v$..dir))) {
    csvs <- sub("__items\\.csv$", "", list.files(d, pattern = "__items\\.csv$"))
    for (t in setdiff(csvs, v$table[v$..dir %in% d]))
        add("ERROR", t, sprintf("ships a CSV in %s but has no verification row", d))
}

for (a in skipped)
    add("ERROR", basename(sub("/$", "", a)),
        sprintf("requested for linting but has no verification_merged.csv -- %s was NOT checked", a))

if (!length(flags)) {
    cat(sprintf("lint_verification: %d rows, no problems found\n", nrow(v)))
    quit(save = "no")
}
sev <- vapply(flags, `[[`, "", "sev")
cat(sprintf("lint_verification: %d rows, %d ERROR, %d WARN, %d INFO\n\n", nrow(v),
            sum(sev == "ERROR"), sum(sev == "WARN"), sum(sev == "INFO")))
for (f in flags[order(sev)]) cat(sprintf("[%s] %s\n    %s\n", f$sev, f$table, f$msg))

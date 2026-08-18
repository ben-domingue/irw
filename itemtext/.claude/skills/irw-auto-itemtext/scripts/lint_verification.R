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
    "(does not|do not|did not) (establish|settle|pin)|",
    "(remain|remains|are|is) unconfirmed|",
    "only pins|pins only|verifies .* not ")

read_one <- function(a) {
    p <- if (dir.exists(a)) file.path(a, "verification_merged.csv") else a
    if (!file.exists(p)) { message("skipping ", a, " -- no verification file"); return(NULL) }
    d <- read.csv(p, stringsAsFactors = FALSE)
    d$..src <- p
    d$..dir <- if (dir.exists(a)) a else NA_character_
    d
}
v <- do.call(rbind, Filter(Negate(is.null), lapply(sub("/$", "", args), read_one)))
if (is.null(v) || !nrow(v)) stop("nothing to lint")

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
        if (length(hits))
            add("WARN", r$table, sprintf("VERIFIED but its evidence hedges (%s) -- should this be PARTIAL?",
                                          paste(unique(tolower(hits)), collapse = ", ")))
        if (!grepl("[0-9]", ev))
            add("WARN", r$table, "VERIFIED but the evidence contains no numbers; Step 5b requires the actual values compared")
    }

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

if (!length(flags)) {
    cat(sprintf("lint_verification: %d rows, no problems found\n", nrow(v)))
    quit(save = "no")
}
sev <- vapply(flags, `[[`, "", "sev")
cat(sprintf("lint_verification: %d rows, %d ERROR, %d WARN\n\n", nrow(v),
            sum(sev == "ERROR"), sum(sev == "WARN")))
for (f in flags[order(sev)]) cat(sprintf("[%s] %s\n    %s\n", f$sev, f$table, f$msg))

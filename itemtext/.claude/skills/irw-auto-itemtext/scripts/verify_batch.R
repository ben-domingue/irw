# Usage: Rscript verify_batch.R <batch_dir>
#
# Runs every verify_<table>.R in a batch and reports which reproduce their claim.
#
# WHY THIS EXISTS. Step 5b records mapping evidence as prose in an `evidence`
# column ("per-item means 4.80, 4.85, 4.78 ... match the paper's Table 1"). Prose
# cannot be re-run: checking it means rebuilding the whole analysis from the
# source, which is what made triaging batches 006-010 slow -- the orchestrator
# re-derived roughly 11 of every 12 tables by hand. A three-line script that
# recomputes the same numbers turns that into one command.
#
# CONTRACT for verify_<table>.R (see references/verify_template.R):
#   - self-contained: fetches its own data, assumes nothing in the environment
#   - prints the numbers it compares, so a human can read the output, not just
#     a pass/fail
#   - its LAST line of output is exactly "VERDICT: PASS" or "VERDICT: FAIL"
#   - it verifies the MAPPING claim, not that the file parses; a script that
#     only checks row counts is worse than none, because it looks like evidence
#
# A table with no verify script is reported as MISSING rather than passed over:
# data_labels tables are exempt from Step 5b but should still say so out loud.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Usage: Rscript verify_batch.R <batch_dir>")
d <- sub("/$", "", args[1])
if (!dir.exists(d)) stop("no such directory: ", d)

tables <- sort(sub("__items\\.csv$", "", list.files(d, pattern = "__items\\.csv$")))
prov_path <- file.path(d, "provenance.csv")
prov <- if (file.exists(prov_path)) read.csv(prov_path, stringsAsFactors = FALSE) else NULL
if (!length(tables) && !is.null(prov)) tables <- sort(prov$table[nzchar(prov$uploaded)])

if (!length(tables)) stop("no tables found in ", d)

basis_of <- function(t) {
    if (is.null(prov) || !t %in% prov$table) return(NA_character_)
    trimws(prov$mapping_basis[match(t, prov$table)])
}

res <- data.frame(table = tables, status = NA_character_, detail = NA_character_,
                  stringsAsFactors = FALSE)
for (i in seq_along(tables)) {
    t <- tables[i]
    f <- file.path(d, paste0("verify_", t, ".R"))
    if (!file.exists(f)) {
        res$status[i] <- if (identical(basis_of(t), "data_labels")) "MISSING(exempt)" else "MISSING"
        res$detail[i] <- sprintf("no verify_%s.R", t)
        next
    }
    cat("\n=== ", t, " ===\n", sep = "")
    out <- tryCatch(system2("Rscript", f, stdout = TRUE, stderr = TRUE),
                    error = function(e) paste("ERROR:", conditionMessage(e)))
    cat(paste(out, collapse = "\n"), "\n")
    verdict <- grep("^VERDICT:", out, value = TRUE)
    res$status[i] <- if (!length(verdict)) "NO VERDICT"
                     else if (grepl("PASS", tail(verdict, 1))) "PASS" else "FAIL"
    res$detail[i] <- if (length(verdict)) tail(verdict, 1) else "script printed no VERDICT line"
}

cat("\n\n=== verify_batch summary:", d, "===\n")
w <- max(nchar(res$table))
for (i in seq_len(nrow(res)))
    cat(sprintf("  %-*s  %-16s %s\n", w, res$table[i], res$status[i],
                if (res$status[i] == "PASS") "" else res$detail[i]))
tab <- table(res$status)
cat("\n", paste(sprintf("%s=%d", names(tab), tab), collapse = "  "), "\n", sep = "")
if (any(res$status %in% c("FAIL", "NO VERDICT")))
    cat("\nFAIL or NO VERDICT means the round's own claim did not reproduce. Read the output above",
        "\nbefore staging any of those tables.\n")

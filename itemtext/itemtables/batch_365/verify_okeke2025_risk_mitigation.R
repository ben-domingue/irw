# verify_okeke2025_risk_mitigation.R -- batch_365, Step 5b.
#
# Claim: IRW item codes rm_1, rm_2, rm_3 are the source workbook's columns B10, B11, B12
# ("Leverage AI Survey.xlsx", figshare 10.6084/m9.figshare.28768874, file 53579603), whose
# statements are printed against those same codes in "Leverage SC Survey Instrument.docx"
# (file 53579606), Section B table "Effectiveness in Mitigating Supply Chain Risks:".
# Post-experiment only: Section A has no risk-mitigation block. A11 ("The current tools I
# use help me effectively mitigate risks in SC management.") is the one Section A item
# about risk, but it belongs to the baseline AI-usefulness block (A9-A11), so it is
# reported here as a named rival.
#
# No IRW processing script for this table is in the repo, so the rm_k <- B(k+9) rename is
# not readable; it is checked here directly. Route: respondent-level re-derivation. Join
# the live table to the source workbook on id (= Participant ID with the "P" dropped;
# covariates checked to agree), then for each rm_k count per-respondent exact agreement
# with every one of the 32 Likert columns A1..A11, B1..B21. A correct mapping gives
# 200/200 on exactly one column, the claimed one; a swap of any two rm items, or a
# shifted block (e.g. B9-B11), would put the 200 elsewhere.

suppressMessages(library(irw))

TABLE <- "okeke2025_risk_mitigation"
CLAIM <- c(rm_1 = "B10", rm_2 = "B11", rm_3 = "B12")

tmp <- tempfile(fileext = ".xlsx")
download.file("https://ndownloader.figshare.com/files/53579603", tmp, mode = "wb", quiet = TRUE)
x <- openxlsx::read.xlsx(tmp, sheet = "Survey Data")
names(x)[1] <- "pid"
x$id <- as.integer(sub("^P", "", x$pid))

d <- as.data.frame(irw::irw_fetch(TABLE))

covs <- grep("^cov_", names(d), value = TRUE)
cat("live covariates:", paste(covs, collapse = ", "), "\n")
cv <- merge(unique(d[, c("id", "cov_industry", "cov_role")]), x, by = "id")
cat(sprintf("ids live %d, joined: %d; industry agree %d; role agree %d\n",
            length(unique(d$id)), nrow(cv), sum(cv$cov_industry == cv$Industry),
            sum(cv$cov_role == cv$Role)))
join_ok <- nrow(cv) == 200 && all(cv$cov_industry == cv$Industry) && all(cv$cov_role == cv$Role)

cols <- c(paste0("A", 1:11), paste0("B", 1:21))
ok <- join_ok
cat(sprintf("\n%-6s %-7s %9s %12s %14s\n", "item", "claimed", "agree", "best_other", "best_other_n"))
for (it in names(CLAIM)) {
    s <- merge(d[d$item == it, c("id", "resp")], x, by = "id")
    ag <- sapply(cols, function(cc) sum(s$resp == as.integer(s[[cc]]), na.rm = TRUE))
    oth <- ag[names(ag) != CLAIM[[it]]]
    bo <- names(which.max(oth))
    cat(sprintf("%-6s %-7s %5d/%d %12s %14d\n", it, CLAIM[[it]], ag[[CLAIM[[it]]]], nrow(s), bo, max(oth)))
    cat("   agreement with B10/B11/B12:", paste(ag[c("B10", "B11", "B12")], collapse = "/"),
        "  with A11 (baseline 'mitigate risks' item):", ag[["A11"]], "\n")
    cat("   live freq 1..5:", paste(tabulate(s$resp, 5), collapse = "/"),
        "  source freq 1..5:", paste(tabulate(as.integer(s[[CLAIM[[it]]]]), 5), collapse = "/"), "\n")
    ok <- ok && ag[[CLAIM[[it]]]] == nrow(s) && nrow(s) == 200 && max(oth) < nrow(s)
}

# Response-data observation (not part of the verdict): inter-item correlations.
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
cat("\nlive inter-item r (not part of verdict):\n")
print(round(cor(w[, -1]), 3))

cat("\nEach rm item must agree 200/200 with its claimed column and fall well short on every other.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

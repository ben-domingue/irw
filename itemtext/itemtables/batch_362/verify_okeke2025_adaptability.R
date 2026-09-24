# verify_okeke2025_adaptability.R -- batch_362, Step 5b.
#
# Claim: IRW item codes adp_1, adp_2, adp_3 are the source workbook's columns B7, B8, B9
# ("Leverage AI Survey.xlsx", figshare 10.6084/m9.figshare.28768874, file 53579603), whose
# statements are printed against those same codes in "Leverage SC Survey Instrument.docx"
# (file 53579606), Section B table "Adaptability (Ivanov & Dolgui, 2021)".
#
# No IRW processing script for this table is in the repo, so the adp_k <- B(6+k) rename
# is not readable; it is checked here directly. Route: respondent-level re-derivation.
# Join the live table to the source workbook on id (= Participant ID with the "P"
# dropped; covariates checked to agree), then for each adp_k count per-respondent exact
# agreement with every one of the 32 Likert columns A1..A11, B1..B21. A correct mapping
# gives 200/200 on exactly one column, the claimed one; a swap of any two adp items, or
# a shifted block, would put the 200 elsewhere.

suppressMessages(library(irw))

TABLE <- "okeke2025_adaptability"
CLAIM <- c(adp_1 = "B7", adp_2 = "B8", adp_3 = "B9")

tmp <- tempfile(fileext = ".xlsx")
download.file("https://ndownloader.figshare.com/files/53579603", tmp, mode = "wb", quiet = TRUE)
x <- openxlsx::read.xlsx(tmp, sheet = 1)
names(x)[1] <- "pid"
x$id <- as.integer(sub("^P", "", x$pid))

d <- as.data.frame(irw::irw_fetch(TABLE))

cv <- merge(unique(d[, c("id", "cov_industry", "cov_role")]), x, by = "id")
cat(sprintf("ids joined: %d; industry agree %d; role agree %d\n",
            nrow(cv), sum(cv$cov_industry == cv$Industry), sum(cv$cov_role == cv$Role)))
join_ok <- nrow(cv) == 200 && all(cv$cov_industry == cv$Industry) && all(cv$cov_role == cv$Role)

cols <- c(paste0("A", 1:11), paste0("B", 1:21))
ok <- join_ok
cat(sprintf("\n%-6s %-7s %6s %12s %14s\n", "item", "claimed", "agree", "best_other", "best_other_n"))
for (it in names(CLAIM)) {
    s <- merge(d[d$item == it, c("id", "resp")], x, by = "id")
    ag <- sapply(cols, function(cc) sum(s$resp == as.integer(s[[cc]]), na.rm = TRUE))
    oth <- ag[names(ag) != CLAIM[[it]]]
    bo <- names(which.max(oth))
    cat(sprintf("%-6s %-7s %4d/%d %12s %14d\n", it, CLAIM[[it]], ag[[CLAIM[[it]]]], nrow(s), bo, max(oth)))
    ok <- ok && ag[[CLAIM[[it]]]] == nrow(s) && nrow(s) == 200 && max(oth) < nrow(s)
}

cat("\nEach adp item must agree 200/200 with its claimed column and fall well short on every other.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

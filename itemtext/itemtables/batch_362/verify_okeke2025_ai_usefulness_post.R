# verify_okeke2025_ai_usefulness_post.R -- Step 5b mapping check (batch_362).
#
# Claim: aiu_post_1, aiu_post_2, aiu_post_3 are the deposit's columns B19, B20, B21
# (Leverage SC Survey Instrument.docx, "Perceived Usefulness of Generative AI Tools
# (Post-experiment)"), whose wording the instrument docx gives against those codes.
# No processing script for this table exists in the repo, so the B19->aiu_post_1
# rename is checked against the data rather than assumed.
#
# Route: re-match the live table to the source xlsx person by person (live id N ==
# source "Participant ID" P00N) and count, for each live item, exact resp agreements
# with EVERY one of the 32 Likert columns A1-A11, B1-B21. A correct mapping agrees on
# all 200 respondents with its own column and at chance-like levels (~40/200 for a
# 5-point item) with every other column, so this distinguishes every item from every
# other item, including from each other.

suppressMessages(library(irw))

TABLE <- "okeke2025_ai_usefulness_post"
CLAIM <- c(aiu_post_1 = "B19", aiu_post_2 = "B20", aiu_post_3 = "B21")
URL   <- "https://ndownloader.figshare.com/files/53579603"  # Leverage AI Survey.xlsx, CC BY 4.0

tmp <- tempfile(fileext = ".xlsx")
download.file(URL, tmp, mode = "wb", quiet = TRUE)
s <- as.data.frame(readxl::read_excel(tmp, sheet = "Survey Data"))
s$id <- as.integer(sub("^P", "", s[["Participant ID"]]))
cols <- c(paste0("A", 1:11), paste0("B", 1:21))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- merge(w, s, by = "id")
cat(sprintf("live ids: %d  source rows: %d  matched: %d\n\n",
            length(unique(d$id)), nrow(s), nrow(m)))

ok <- nrow(m) == 200
cat(sprintf("%-11s %-6s %10s %18s %10s\n", "item", "claim", "agree", "best other (col)", "margin"))
for (it in names(CLAIM)) {
    v  <- m[[paste0("resp.", it)]]
    ag <- sapply(cols, function(cl) sum(v == m[[cl]], na.rm = TRUE))
    own <- ag[CLAIM[[it]]]
    oth <- ag[names(ag) != CLAIM[[it]]]
    best <- names(which.max(oth))
    cat(sprintf("%-11s %-6s %6d/%-3d %12d (%s) %10d\n",
                it, CLAIM[[it]], own, nrow(m), max(oth), best, own - max(oth)))
    if (own != nrow(m) || max(oth) >= nrow(m) / 2) ok <- FALSE
}
cat("\nThis establishes the code->column tie for all three items. The column->wording tie\n",
    "is the instrument docx's own B19/B20/B21 labels, read directly (not tested here).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

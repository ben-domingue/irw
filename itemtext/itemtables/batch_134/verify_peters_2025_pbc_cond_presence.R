# Step 5b verification for peters_2025_pbc_cond_presence.
#
# CLAIM UNDER TEST
#   Each IRW item code is the study's own LimeSurvey question code with the
#   family/component prefix "PbcCnPr" stripped and the remainder lower-cased --
#   PbcCnPrBusyPlace -> busyplace, PbcCnPrSprmrkt -> sprmrkt, and so on for all
#   22 -- and the item_text shipped for each code is the subquestion_en of the
#   row whose `id` is exactly that raw question code in the project's own
#   question-definition sheet (DMQs, Google Sheets key
#   1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc, worksheet `en`).
#
#   If any two item texts were swapped, the code -> raw-column tie asserted here
#   would put a different column's responses under that code, and the cell-level
#   comparison below would break.
#
# ROUTE: re-run the mapping over the raw source files (core model s3, the
# "script-generated / re-run the script" route), at the level of individual
# response cells rather than summary statistics.
#
#   1. Download two of the project's raw LimeSurvey exports (sid 100110,
#      response ids 1-5166) from the study's own data repository.
#   2. Apply data/peters_2025_covid19_risk_dcts.py's rule by hand: melt the
#      PbcCnPr* columns (excluding the amended "...2" variants, which the
#      processing script does not read), keep resp in 1..5 (code 0 = "not
#      applicable" is dropped), build id as "<sid>-<orig_id>", and label each
#      value with the lower-cased suffix.
#   3. Merge that against irw::irw_fetch() restricted to the same ids and
#      require an EXACT match on every (id, item, resp) cell.
#
# This is decisive rather than circumstantial: a permutation of any two item
# codes would move ~60-80 response values per item onto the wrong code, and the
# merge would report mismatches immediately. It distinguishes every item from
# every other item, because every item's response vector is compared
# individually.
#
# WHAT IT DOES NOT ESTABLISH
#   - It verifies the code <-> raw-column tie. The raw-column <-> wording tie is
#     a label match in the DMQs sheet (its `id` column IS the raw column name)
#     and is not testable from response data; it is recorded in provenance.
#   - It says nothing about the unlabelled intermediate options (resp 2-4), which
#     are shipped blank because the instrument labels only the two endpoints.
#   - It does not test the endpoint direction independently; resp 1 = bottom
#     anchor / resp 5 = top anchor is published outright in the companion
#     DMQ_scales sheet, not inferred.
#   - The comparison covers one country deployment (sid 100110, 1,430 cells);
#     the live table pools 21.

suppressMessages(library(irw))

TABLE <- "peters_2025_pbc_cond_presence"
SID   <- "100110"
BASE  <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
FILES <- c("YCR-dataPipeline--sid-100110--rids-1-2583.csv",
           "YCR-dataPipeline--sid-100110--rids-2584-5166.csv")

cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)

raw_list <- list()
for (f in FILES) {
  p <- file.path(cache, f)
  if (!file.exists(p))
    utils::download.file(paste0(BASE, f), p, quiet = TRUE)
  raw_list[[f]] <- utils::read.csv(p, colClasses = "character",
                                   check.names = FALSE)
}

# melt PbcCnPr* (excluding the amended "...2" columns) into IRW long form
long <- do.call(rbind, lapply(raw_list, function(df) {
  names(df)[1] <- "orig_id"
  cols <- grep("^PbcCnPr", names(df), value = TRUE)
  cols <- cols[!grepl("2$", cols)]
  do.call(rbind, lapply(cols, function(cn) {
    v <- suppressWarnings(as.numeric(df[[cn]]))
    keep <- !is.na(v) & v >= 1 & v <= 5
    data.frame(id   = paste0(SID, "-", df$orig_id[keep]),
               item = tolower(sub("^PbcCnPr", "", cn)),
               resp_raw = v[keep], stringsAsFactors = FALSE)
  }))
}))
rownames(long) <- NULL

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
live <- d[d$id %in% unique(long$id), c("id", "item", "resp")]
names(live)[3] <- "resp_live"

m <- merge(long, live, by = c("id", "item"), all = TRUE)
unmatched <- sum(is.na(m$resp_raw) | is.na(m$resp_live))
mismatch  <- sum(m$resp_raw != m$resp_live, na.rm = TRUE)

cat(sprintf("raw cells re-derived from source exports : %d\n", nrow(long)))
cat(sprintf("live cells for the same ids              : %d\n", nrow(live)))
cat(sprintf("cells present on only one side           : %d\n", unmatched))
cat(sprintf("cells whose values disagree              : %d\n\n", mismatch))

cat(sprintf("%-11s %6s %6s %9s %9s %8s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "n_disagr"))
items <- sort(unique(long$item))
for (i in items) {
  a <- long[long$item == i, ]
  b <- live[live$item == i, ]
  mi <- m[m$item == i, ]
  cat(sprintf("%-11s %6d %6d %9.3f %9.3f %8d\n", i, nrow(a), nrow(b),
              mean(a$resp_raw), mean(b$resp_live),
              sum(mi$resp_raw != mi$resp_live, na.rm = TRUE)))
}

ok <- nrow(long) > 0 && unmatched == 0 && mismatch == 0 &&
      length(items) == 22
cat(sprintf("\n22 items compared individually; every one reproduced exactly: %s\n",
            ok))
cat("Not established here: the raw-column -> wording tie (a label match in the\n",
    "DMQs sheet), the blank intermediate options, and the published 1=bottom /\n",
    "5=top anchor direction. See provenance.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# Step 5b verification for peters_2025_ciberlite (batch_385).
#
# CLAIM UNDER TEST
#   Each IRW item code is the study's own LimeSurvey question code with the
#   "CIBERlite" prefix stripped and the remainder lower-cased (CIBERliteAttExp ->
#   attexp, CIBERlitePbcCap1 -> pbccap1, ... 8 items), per
#   data/peters_2025_covid19_risk_dcts.py, and the item_text/anchors shipped for
#   each code are those of the row whose `id` is exactly that raw question code in
#   the project's DMQs question-definition sheet (Google Sheets key
#   1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc, worksheet `en`).
#
# ROUTE: re-run the mapping over the raw source exports at the level of individual
# response cells. Download the five raw LimeSurvey exports for sid 100110 from the
# study's data repository, melt the CIBERlite* columns (excluding the *Seq
# randomisation-slot columns), keep 1..5 for the uni items and 1..7 for the bi
# items (code 0 = not applicable is dropped, as the processing script does), build
# id "<sid>-<orig_id>", label with the lower-cased suffix, and require an EXACT
# match on every (id, item, resp) cell against irw::irw_fetch().
#
# A permutation of any two item codes would move that item's response vector onto
# the wrong code and break the cell-level merge, so every item is distinguished
# from every other item.
#
# WHAT IT DOES NOT ESTABLISH
#   - The raw-column -> wording tie is a label match in the DMQs sheet (its `id`
#     column IS the raw column name) and is not testable from response data.
#   - The anchor direction (code 1 = bottom anchor, top code = top anchor) is
#     published in the DMQ_scales sheet and in the deployed .lss, not inferred here.
#   - Only one deployment (sid 100110) is compared; the live table pools 21.

suppressMessages(library(irw))

TABLE <- "peters_2025_ciberlite"
SID   <- "100110"
BASE  <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
FILES <- c("YCR-dataPipeline--sid-100110--rids-1-2583.csv",
           "YCR-dataPipeline--sid-100110--rids-2584-5166.csv",
           "YCR-dataPipeline--sid-100110--rids-5167-9096.csv",
           "YCR-dataPipeline--sid-100110--rids-9097-13026.csv",
           "YCR-dataPipeline--sid-100110--rids-13027-13135.csv")
POL <- c(CIBERliteAttExp = 7, CIBERliteAttIns = 7, CIBERliteInt = 5,
         CIBERlitePbcAut = 5, CIBERlitePbcCap1 = 5, CIBERlitePbcCap2 = 5,
         CIBERlitePnDes = 5, CIBERlitePnInj = 7)

cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)

long <- do.call(rbind, lapply(FILES, function(f) {
  p <- file.path(cache, f)
  if (!file.exists(p)) utils::download.file(paste0(BASE, f), p, quiet = TRUE)
  df <- utils::read.csv(p, colClasses = "character", check.names = FALSE)
  names(df)[1] <- "orig_id"
  cols <- grep("^CIBERlite", names(df), value = TRUE)
  cols <- cols[!grepl("Seq$", cols)]
  stopifnot(setequal(cols, names(POL)))
  do.call(rbind, lapply(cols, function(cn) {
    v <- suppressWarnings(as.numeric(df[[cn]]))
    keep <- !is.na(v) & v >= 1 & v <= POL[[cn]]
    if (!any(keep)) return(NULL)
    data.frame(id = paste0(SID, "-", df$orig_id[keep]),
               item = tolower(sub("^CIBERlite", "", cn)),
               resp_raw = v[keep], stringsAsFactors = FALSE)
  }))
}))

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
live <- d[grepl(paste0("^", SID, "-"), d$id), c("id", "item", "resp")]
names(live)[3] <- "resp_live"

m <- merge(long, live, by = c("id", "item"), all = TRUE)
unmatched <- sum(is.na(m$resp_raw) | is.na(m$resp_live))
mismatch  <- sum(m$resp_raw != m$resp_live, na.rm = TRUE)

cat(sprintf("raw cells re-derived from sid %s exports : %d\n", SID, nrow(long)))
cat(sprintf("live cells for sid %s                    : %d\n", SID, nrow(live)))
cat(sprintf("cells present on only one side             : %d\n", unmatched))
cat(sprintf("cells whose values disagree                : %d\n\n", mismatch))

cat(sprintf("%-8s %6s %6s %9s %9s %8s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "n_disagr"))
items <- sort(unique(long$item))
for (i in items) {
  a <- long[long$item == i, ]; b <- live[live$item == i, ]; mi <- m[m$item == i, ]
  cat(sprintf("%-8s %6d %6d %9.3f %9.3f %8d\n", i, nrow(a), nrow(b),
              mean(a$resp_raw), mean(b$resp_live),
              sum(mi$resp_raw != mi$resp_live, na.rm = TRUE)))
}

ok <- nrow(long) > 0 && unmatched == 0 && mismatch == 0 && length(items) == 8
cat(sprintf("\n8 items compared individually; every one reproduced exactly: %s\n", ok))
cat("Not established here: the raw-column -> wording tie (a label match in the DMQs\n",
    "sheet) and the published anchor direction. See provenance.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

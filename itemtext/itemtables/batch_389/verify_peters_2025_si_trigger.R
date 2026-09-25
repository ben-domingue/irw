# Step 5b verification for peters_2025_si_trigger (batch_389).
#
# CLAIM UNDER TEST
#   The 4 IRW items are the 4 checkbox options of the Your COVID-19 Risk tool's
#   LimeSurvey multiple-choice question `siTrigger` ("I would leave my house less
#   (or not at all) if:"). data/peters_2025_covid19_risk_precautions.py takes each
#   raw column "siTrigger.<code>." and lower-cases <code> (symSe -> symse,
#   symOt -> symot; govmt, none unchanged), a name-preserving rename with no
#   positional step; the free-text "other" box is dropped. The item_text shipped for
#   each code is the text of the answer option carrying that ls_answer_code in the
#   project's REQs sheet (Google Sheets key 1qMf-7khtWhHv8oBUa-yhsAvq8TCG5Nrc0t79OaqRLT0,
#   worksheet `en`), and the stem in `instructions` is that sheet's question text.
#   resp 1 = option ticked ("Y"), resp 0 = not ticked (administration gated on the
#   option's *Est column being non-null).
#
# ROUTES
#   A. Code-label match, two independent copies: shipped item_text vs the REQs sheet
#      AND vs the deployed English production survey file (v1.10, sid 100110) on the
#      project GitLab, subquestion by subquestion code; stem vs both.
#   B. Cell-level re-run of the processing script's decoding over the five raw sid
#      100110 exports (Est-not-null gate; "Y" -> 1, else 0), merged to irw_fetch()
#      on (id, item). A swap of any two codes moves a response vector onto the wrong
#      code and breaks the merge, so every IRW code is tied to its own raw column.
#   C. Keying polarity (route 6): `none` ("I would not consider this at all") must
#      correlate negatively with each of the three triggers, and the three triggers
#      must correlate positively with one another.
#
# WHAT IT DOES NOT ESTABLISH
#   - The raw-column -> wording tie is a code-label match (ls_answer_code = subquestion
#     title = raw column infix); response data cannot test wording for symse/symot/
#     govmt, which C does not separate from one another.
#   - Only one deployment (sid 100110, overwhelmingly English) is re-run; the live
#     table pools 21 sids.
#   - resp 0 conflates "not ticked" with "question skipped" (not mandatory).

suppressMessages(library(irw))

TABLE <- "peters_2025_si_trigger"
FAM   <- "siTrigger"
SID   <- "100110"
NITEM <- 4
BASE  <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
FILES <- c("YCR-dataPipeline--sid-100110--rids-1-2583.csv",
           "YCR-dataPipeline--sid-100110--rids-2584-5166.csv",
           "YCR-dataPipeline--sid-100110--rids-5167-9096.csv",
           "YCR-dataPipeline--sid-100110--rids-9097-13026.csv",
           "YCR-dataPipeline--sid-100110--rids-13027-13135.csv")
REQS <- "https://docs.google.com/spreadsheets/d/1qMf-7khtWhHv8oBUa-yhsAvq8TCG5Nrc0t79OaqRLT0/gviz/tq?tqx=out:csv&sheet=en"
LSS  <- "https://gitlab.com/a-bc/your-covid-19-risk/-/raw/master/v1/operationalizations/limesurvey/your-covid-19-risk--production--v1.10--100110.txt"

cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)
get <- function(url, f) { p <- file.path(cache, f); if (!file.exists(p)) utils::download.file(url, p, quiet = TRUE); p }

here <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) "itemtables/batch_389")
shipped <- utils::read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
st <- unique(shipped[, c("item", "item_text")])

# ---- A. code-label match against two copies --------------------------------
r <- utils::read.csv(get(REQS, "reqs_en.csv"), stringsAsFactors = FALSE, check.names = FALSE)
r <- r[r$ls_question_code == FAM, ]
sheet <- setNames(r$text_en[r$row_type == "answer_option"], tolower(r$ls_answer_code[r$row_type == "answer_option"]))
sheet_stem <- r$text_en[r$row_type == "question"]

l <- readLines(get(LSS, "prod_v1.10_100110.txt"), encoding = "UTF-8", warn = FALSE)
f <- strsplit(l, "\t", fixed = TRUE)
cls <- vapply(f, function(x) if (length(x) >= 3) x[3] else "", "")
nm  <- vapply(f, function(x) if (length(x) >= 5) x[5] else "", "")
lg  <- vapply(f, function(x) if (length(x) >= 9) x[9] else "", "")
txt <- vapply(f, function(x) if (length(x) >= 7) gsub('^"|"$', "", x[7]) else "", "")
qrow <- which(cls == "Q" & nm == FAM & lg == "en")
stopifnot(length(qrow) == 1)
k <- qrow + 1; sq <- character()
while (cls[k] == "SQ") { sq[tolower(nm[k])] <- txt[k]; k <- k + 1 }
lss_stem <- txt[qrow]

cat("A. item | shipped == REQs sheet | shipped == deployed English (v1.10)\n")
a_ok <- 0
for (i in sort(st$item)) {
  s <- st$item_text[st$item == i]
  e1 <- identical(s, unname(sheet[i])); e2 <- identical(s, unname(sq[i]))
  a_ok <- a_ok + (e1 && e2)
  cat(sprintf("   %-6s %-5s %-5s  %s\n", i, e1, e2, s))
}
stem_ok <- identical(unique(shipped$instructions), sheet_stem) && identical(sheet_stem, lss_stem)
cat(sprintf("   sheet codes: %s; deployed SQ codes: %s (plus free-text 'other', not an item)\n",
            paste(names(sheet), collapse = ","), paste(names(sq), collapse = ",")))
cat(sprintf("   shipped %d; text identical in both copies: %d/%d; stem identical: %s\n\n",
            nrow(st), a_ok, NITEM, stem_ok))

# ---- B. cell-level re-run over raw sid 100110 exports ---------------------
pat <- paste0("^", FAM, "\\.([A-Za-z]+)\\.$")
raw <- lapply(FILES, function(fn) {
  df <- utils::read.csv(get(paste0(BASE, fn), fn), colClasses = "character", check.names = FALSE)
  names(df)[1] <- "orig_id"; df })
cols <- Reduce(union, lapply(raw, function(df) grep(pat, names(df), value = TRUE)))
# The script drops a box whose non-null values are not all "Y" over the WHOLE
# pooled export (the free-text 'other' box). Apply that test pooled over the five
# files, not per file: in one small file 'other' happens to hold no text at all.
keep <- vapply(cols, function(cn) {
  v <- unlist(lapply(raw, function(df) df[[cn]])); v <- v[!is.na(v) & v != ""]
  all(v == "Y") }, logical(1))
cat(sprintf("   pooled Y-only test: %s\n", paste(sprintf("%s=%s", cols, keep), collapse = ", ")))
long <- do.call(rbind, lapply(raw, function(df) {
  do.call(rbind, lapply(cols[keep], function(cn) {
    code <- sub(pat, "\\1", cn)
    est  <- paste0(FAM, toupper(substr(code, 1, 1)), substring(code, 2), "Est")
    if (!est %in% names(df)) return(NULL)
    adm  <- !is.na(df[[est]]) & df[[est]] != ""
    data.frame(id = paste0(SID, "-", df$orig_id[adm]), item = tolower(code),
               resp_raw = as.integer(df[[cn]][adm] %in% "Y"), stringsAsFactors = FALSE)
  }))
}))

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.integer(d$resp)
live <- d[startsWith(d$id, paste0(SID, "-")), c("id", "item", "resp")]
names(live)[3] <- "resp_live"
m <- merge(long, live, by = c("id", "item"), all = TRUE)
unmatched <- sum(is.na(m$resp_raw) | is.na(m$resp_live))
mismatch  <- sum(m$resp_raw != m$resp_live, na.rm = TRUE)
cat(sprintf("B. raw cells %d, live cells %d (sid %s), on one side only %d, disagreeing %d\n",
            nrow(long), nrow(live), SID, unmatched, mismatch))
cat(sprintf("   %-6s %6s %6s %9s %9s\n", "item", "n_raw", "n_live", "p_raw", "p_live"))
for (i in sort(unique(long$item))) {
  a <- long$resp_raw[long$item == i]; b <- live$resp_live[live$item == i]
  cat(sprintf("   %-6s %6d %6d %9.4f %9.4f\n", i, length(a), length(b), mean(a), mean(b)))
}
b_ok <- nrow(long) > 0 && unmatched == 0 && mismatch == 0 && length(unique(long$item)) == NITEM

# ---- C. polarity of `none` over the full live table -----------------------
w <- stats::reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cm <- stats::cor(w[, setdiff(names(w), "id")])
trg <- setdiff(colnames(cm), "none")
hm <- cm["none", trg]
pairs <- cm[trg, trg][upper.tri(cm[trg, trg])]
cat(sprintf("\nC. cor(none, trigger) over %d respondents: %s\n", nrow(w),
            paste(sprintf("%s %.2f", trg, hm), collapse = ", ")))
cat(sprintf("   %d trigger pairs: min %.2f, max %.2f\n", length(pairs), min(pairs), max(pairs)))
c_ok <- all(hm < 0) && all(pairs > 0)

ok <- a_ok == NITEM && stem_ok && b_ok && c_ok
cat(sprintf("\nA %s  B %s  C %s\n", a_ok == NITEM && stem_ok, b_ok, c_ok))
cat("Not established: wording for symse/symot/govmt rests on the code-label match (A);\n",
    "C separates only `none` from the triggers; one of 21 deployments re-run in B.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

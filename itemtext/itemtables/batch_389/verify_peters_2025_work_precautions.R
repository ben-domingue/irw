# Step 5b verification for peters_2025_work_precautions (batch_389).
#
# CLAIM UNDER TEST
#   The 4 IRW items are the 4 checkbox options of the Your COVID-19 Risk tool's
#   LimeSurvey multiple-choice question `work` ("Currently, do you work within a short
#   distance of others?"). data/peters_2025_covid19_risk_precautions.py takes each raw
#   column "work.<code>." and lower-cases <code> (all four codes are already lower case),
#   a name-preserving rename with no positional step. The item_text shipped for each
#   code is the text of the answer option carrying that ls_answer_code in the
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
#   C. Keying polarity (route 6): `home` ("I am working from home or not working
#      currently") must correlate negatively with each of the three "Yes, with ..."
#      items. (The three "Yes" items are NOT required to correlate positively with
#      each other: they are near-independent workplace categories.)
#
# WHAT IT DOES NOT ESTABLISH
#   - The raw-column -> wording tie is a code-label match (ls_answer_code = subquestion
#     title = raw column infix); response data cannot test wording for the three
#     "Yes, with ..." items, which C does not separate from one another.
#   - Only one deployment (sid 100110) is re-run; the live table pools 21 sids.
#   - resp 0 conflates "not ticked" with "question skipped" (not mandatory).

suppressMessages(library(irw))

TABLE <- "peters_2025_work_precautions"
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
r <- r[r$ls_question_code == "work", ]
sheet <- setNames(r$text_en[r$row_type == "answer_option"], tolower(r$ls_answer_code[r$row_type == "answer_option"]))
sheet_stem <- r$text_en[r$row_type == "question"]

l <- readLines(get(LSS, "prod_v1.10_100110.txt"), encoding = "UTF-8", warn = FALSE)
f <- strsplit(l, "\t", fixed = TRUE)
cls <- vapply(f, function(x) if (length(x) >= 3) x[3] else "", "")
nm  <- vapply(f, function(x) if (length(x) >= 5) x[5] else "", "")
lg  <- vapply(f, function(x) if (length(x) >= 9) x[9] else "", "")
txt <- vapply(f, function(x) if (length(x) >= 7) gsub('^"|"$', "", x[7]) else "", "")
qrow <- which(cls == "Q" & nm == "work" & lg == "en")
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
cat(sprintf("   codes in sheet %d, in deployed survey %d, shipped %d; text identical in both: %d/%d; stem identical: %s\n\n",
            length(sheet), length(sq), nrow(st), a_ok, NITEM, stem_ok))

# ---- B. cell-level re-run over raw sid 100110 exports ---------------------
long <- do.call(rbind, lapply(FILES, function(fn) {
  df <- utils::read.csv(get(paste0(BASE, fn), fn), colClasses = "character", check.names = FALSE)
  names(df)[1] <- "orig_id"
  cols <- grep("^work\\.[A-Za-z]+\\.$", names(df), value = TRUE)
  do.call(rbind, lapply(cols, function(cn) {
    code <- sub("^work\\.([A-Za-z]+)\\.$", "\\1", cn)
    est  <- paste0("work", toupper(substr(code, 1, 1)), substring(code, 2), "Est")
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

# ---- C. polarity of `home` over the full live table -----------------------
w <- stats::reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cm <- stats::cor(w[, setdiff(names(w), "id")])
near <- setdiff(colnames(cm), "home")
hm <- cm["home", near]
both <- sum(w$home == 1 & (w$ptnts + w$chldr + w$publc) > 0)
cat(sprintf("\nC. cor(home, other) over %d respondents: %s\n", nrow(w),
            paste(sprintf("%s %.3f", near, hm), collapse = ", ")))
cat(sprintf("   home ticked %d; of those also ticked a 'Yes, with ...' option %d\n", sum(w$home == 1), both))
c_ok <- length(hm) == 3 && all(hm < 0)

ok <- a_ok == NITEM && stem_ok && b_ok && c_ok
cat(sprintf("\nA %s  B %s  C %s\n", a_ok == NITEM && stem_ok, b_ok, c_ok))
cat("Not established: wording for the three 'Yes, with ...' items rests on the code-label\n",
    "match (A); C separates only `home` from the rest; one of 21 deployments re-run in B.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# Step 5b verification for peters_2025_si_intention (batch_389).
#
# CLAIM UNDER TEST
#   The 5 IRW items are the 5 fixed checkbox options of the Your COVID-19 Risk tool's
#   LimeSurvey multiple-choice question `siIntention` ("What would change?", group
#   selfIsolationGroup2, array_filter = siCurrent). data/peters_2025_covid19_risk_precautions.py
#   takes each raw column "siIntention.<code>." and lower-cases <code> (all five are
#   already lower case) -- a name-preserving rename, no positional step; the free-text
#   "other" box is dropped. item_text for each code is the answer option carrying that
#   ls_answer_code in the project's REQs sheet (key 1qMf-7khtWhHv8oBUa-yhsAvq8TCG5Nrc0t79OaqRLT0,
#   worksheet `en`); the stem in `instructions` is that sheet's question text.
#   resp 1 = option ticked ("Y"), resp 0 = not ticked (gate: the option's *Est column non-null).
#
# ROUTES
#   A. Code-label match, two independent copies: shipped item_text vs the REQs sheet AND
#      vs the deployed English production survey file (v1.10, sid 100110), by subquestion
#      code; stem vs both.
#   B. Cell-level re-run of the processing script's decoding over the five raw sid 100110
#      exports, merged to the live table on (id, item). A swap of two codes moves a
#      response vector onto the wrong code and breaks the merge.
#   C. array_filter signature (content-level, over all 21 deployments): siIntention shows
#      option X only to respondents who ticked siCurrent option X, so in the live data
#      intention X = 1 must NEVER co-occur with current X = 0 (diagonal = 0), while for
#      every other pair (X, Y != X) such co-occurrences do exist (off-diagonal > 0). This
#      ties each intention code to the siCurrent option whose wording it negates, and
#      separates every item from every other.
#
# WHAT IT DOES NOT ESTABLISH
#   - Route C ties intention codes to siCurrent codes; the wording of each rests on A
#     (and on si_current's own verified mapping, batch_388).
#   - B re-runs one of 21 deployments.
#   - resp 0 conflates not ticked, skipped, and never shown (array_filter).

suppressMessages(library(irw))

TABLE <- "peters_2025_si_intention"
SIBL  <- "peters_2025_si_current"
SID   <- "100110"
NITEM <- 5
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
r <- r[r$ls_question_code == "siIntention", ]
ao <- r[r$row_type == "answer_option", ]
sheet <- setNames(ao$text_en, tolower(ao$ls_answer_code))
sheet_stem <- r$text_en[r$row_type == "question"]

l <- readLines(get(LSS, "prod_v1.10_100110.txt"), encoding = "UTF-8", warn = FALSE)
f <- strsplit(l, "\t", fixed = TRUE)
cls <- vapply(f, function(x) if (length(x) >= 3) x[3] else "", "")
nm  <- vapply(f, function(x) if (length(x) >= 5) x[5] else "", "")
lg  <- vapply(f, function(x) if (length(x) >= 9) x[9] else "", "")
af  <- vapply(f, function(x) if (length(x) >= 17) x[17] else "", "")
txt <- vapply(f, function(x) if (length(x) >= 7) gsub('^"|"$', "", x[7]) else "", "")
qrow <- which(cls == "Q" & nm == "siIntention" & lg == "en")
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
cat(sprintf("   REQs options %d (incl. 'spec' = Other), deployed SQs %d, shipped %d; text identical in both: %d/%d; stem identical: %s; array_filter = %s\n\n",
            length(sheet), length(sq), nrow(st), a_ok, NITEM, stem_ok, af[qrow]))

# ---- B. cell-level re-run over raw sid 100110 exports ---------------------
long <- do.call(rbind, lapply(FILES, function(fn) {
  df <- utils::read.csv(get(paste0(BASE, fn), fn), colClasses = "character", check.names = FALSE)
  names(df)[1] <- "orig_id"
  cols <- grep("^siIntention\\.[A-Za-z]+\\.$", names(df), value = TRUE)
  do.call(rbind, lapply(cols, function(cn) {
    code <- sub("^siIntention\\.([A-Za-z]+)\\.$", "\\1", cn)
    est  <- paste0("siIntention", toupper(substr(code, 1, 1)), substring(code, 2), "Est")
    if (!est %in% names(df)) return(NULL)
    # "other" is the free-text "Other, please specify" box. The processing script drops it
    # by content over the pooled 21-sid data (non-Y values), and the live table has no
    # "other" item; within sid 100110 alone its checkbox column is empty, so a per-file
    # content test would keep it -- drop it by name to mirror the pooled decision.
    if (code == "other") return(NULL)
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

# ---- C. array_filter signature against siCurrent, all deployments ----------
s <- as.data.frame(irw::irw_fetch(SIBL))
wi <- stats::reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
ws <- stats::reshape(s[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
codes <- sort(unique(d$item))
# rows: intention code X ticked; cols: current code Y NOT ticked
wi2 <- setNames(wi, sub("^resp\\.", "int_", names(wi)))
ws2 <- setNames(ws, sub("^resp\\.", "cur_", names(ws)))
w <- merge(wi2, ws2, by = "id")
M <- sapply(codes, function(y) sapply(codes, function(x)
  sum(w[[paste0("int_", x)]] == 1 & w[[paste0("cur_", y)]] == 0)))
dimnames(M) <- list(paste0("int=1:", codes), paste0("cur=0:", codes))
cat(sprintf("\nC. respondents in both tables: %d. Count of (siIntention X ticked AND siCurrent Y not ticked):\n", nrow(w)))
print(M)
c_ok <- all(diag(M) == 0) && all(M[row(M) != col(M)] > 0)
cat(sprintf("   diagonal all zero: %s; min off-diagonal: %d\n", all(diag(M) == 0), min(M[row(M) != col(M)])))

ok <- a_ok == NITEM && stem_ok && b_ok && c_ok
cat(sprintf("\nA %s  B %s  C %s\n", a_ok == NITEM && stem_ok, b_ok, c_ok))
cat("Not established: C ties each intention code to its siCurrent counterpart (whose wording\n",
    "batch_388 verified); intention wording itself rests on the code-label match (A).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

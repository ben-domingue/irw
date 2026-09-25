# verify_peters_2025_nrm_desc_ident.R  (batch_387)
#
# CLAIM UNDER TEST (Step 5b): each of the 8 live item codes carries the
# identification-with-referent stem of the SAME referent, taken from the study's
# own question-definition sheet (DMQs Google Sheet key
# 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc, worksheet 'en'):
#   doctor -> "... I want to be like my doctor ...", likeyou -> "... people like me ...",
#   other -> "... other people ...", and so on; resp=1 = bottom anchor
#   "as little as possible", resp=7 = top anchor "as much as possible".
#
# ROUTE A (label match / exact code re-derivation). The sheet's `id` column holds
# the LimeSurvey question code in its long form (NrmDeIdeDoctor ...). The project's
# own code shortening (dmqReplacements in the CC0 build script at
# https://your-risk.com/v1-translation-results-limesurvey: NrmDeIde -> NrmDeId)
# gives the raw export column name, and data/peters_2025_covid19_risk_dcts.py's
# rename (^NrmDe(Beh|Id)(.+)$, Id -> nrm_desc_ident, tail lower-cased) gives the
# IRW code. Must be one-to-one and onto the live item set, and the shipped
# item_text / anchors must equal that same sheet row's fields.
#
# ROUTE B (raw -> live, data side). For the respondents of two raw export files,
# the per (item x resp) counts read from raw column NrmDeId<Referent> must equal
# the live table's counts for the same ids. Pairwise, the raw count vectors of
# the 8 columns are all distinct in these files, so any swap of two item codes
# (or building from the adjacent NrmDeBeh* 1-5 columns) breaks this.

suppressMessages(library(irw))

TABLE <- "peters_2025_nrm_desc_ident"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")
RAW <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
FILES <- c("YCR-dataPipeline--sid-100103--rids-1-1479.csv",
           "YCR-dataPipeline--sid-100105--rids-1-2450.csv")

args <- grep("^--file=", commandArgs(FALSE), value = TRUE)
items_csv <- if (length(args)) file.path(dirname(sub("^--file=", "", args[1])),
                 paste0(TABLE, "__items.csv")) else ""
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_387", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

bad <- 0L

## ---- ROUTE A ----
shorten <- function(x) {
  reps <- c(generic = "gnrc", Decline = "Decl", Supermarket = "Sprmrkt",
            Neighbourhood = "Neighbrhd", NrmDeIde = "NrmDeId",
            Respons = "Rspns", Flip = "Fl")
  for (k in names(reps)) x <- gsub(k, reps[[k]], x)
  x
}
sheet <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = FALSE)
idr <- sheet[grepl("^NrmDeIde", sheet$id), ]
idr$rawcol <- shorten(idr$id)
idr$code <- tolower(sub("^NrmDeId", "", idr$rawcol))
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- sort(s$items)

cat("== ROUTE A: sheet id -> raw column -> IRW code, and shipped text ==\n")
for (i in order(idr$code)) {
  code <- idr$code[i]; rows <- ship[ship$item == code, ]
  st <- unique(rows$item_text)
  lo <- rows$option_text[rows$resp == 1]; hi <- rows$option_text[rows$resp == 7]
  mid <- rows$option_text[!rows$resp %in% c(1, 7)]
  ok <- code %in% live && length(st) == 1 && identical(st, trimws(idr$subquestion_en[i])) &&
        identical(lo, trimws(idr$bottom_anchor_bare[i])) &&
        identical(hi, trimws(idr$top_anchor_bare[i])) && all(is.na(mid) | mid == "")
  cat(sprintf("%-20s -> %-19s -> %-12s %s  | %s\n", idr$id[i], idr$rawcol[i], code,
              if (ok) "ok" else "MISMATCH", substr(st, 60, 120)))
  bad <- bad + !ok
}
ml <- setdiff(live, idr$code); ms <- setdiff(idr$code, live)
cat(sprintf("live codes not derived: %d; derived codes not live: %d; distinct derived %d vs live %d\n",
            length(ml), length(ms), length(unique(idr$code)), length(live)))
bad <- bad + (length(ml) + length(ms) > 0) + (length(unique(idr$code)) != length(live))

## ---- ROUTE B ----
d <- irw::irw_fetch(TABLE)
tab <- function(v, mx = 7) { v <- suppressWarnings(as.numeric(v)); v <- v[!is.na(v) & v >= 1 & v <= mx]
                             as.integer(table(factor(v, levels = 1:mx))) }
cat("\n== ROUTE B: per item x resp counts (resp 1..7), raw column vs live, same ids ==\n")
for (f in FILES) {
  tf <- tempfile(fileext = ".csv")
  download.file(paste0(RAW, f), tf, quiet = TRUE)
  r <- read.csv(tf, stringsAsFactors = FALSE, check.names = FALSE)
  sid <- sub(".*sid-(\\d+).*", "\\1", f)
  r$gid <- paste0(sid, "-", r[[1]])
  lv <- d[d$id %in% r$gid, ]
  cat(sprintf("%s: %d raw rows, %d live rows for these ids\n", f, nrow(r), nrow(lv)))
  rawv <- list()
  for (i in order(idr$code)) {
    code <- idr$code[i]; col <- idr$rawcol[i]
    rc <- tab(r[[col]]); lc <- tab(lv$resp[lv$item == code]); rawv[[code]] <- rc
    ok <- identical(rc, lc)
    cat(sprintf("  %-12s live %-24s raw %-19s %-24s %s\n", code, paste(lc, collapse = "/"),
                col, paste(rc, collapse = "/"), if (ok) "ok" else "MISMATCH"))
    bad <- bad + !ok
  }
  prs <- combn(names(rawv), 2)
  same <- sum(apply(prs, 2, function(p) identical(rawv[[p[1]]], rawv[[p[2]]])))
  cat(sprintf("  pairs of items with identical raw count vectors in this file: %d of %d\n",
              same, ncol(prs)))
  # same-referent behaviour column (raw names differ: LikeGeneral -> General, LikeNeighb -> Neighb)
  beh <- sub("^NrmDeId", "NrmDeBeh", sub("Like(General|Neighb)$", "\\1", idr$rawcol))
  stopifnot(all(beh %in% names(r)))
  behmatch <- sum(mapply(function(b, code)
                           identical(tab(r[[b]]), tab(lv$resp[lv$item == code])), beh, idr$code))
  cat(sprintf("  rival same-referent NrmDeBeh* columns (%s ...) that would also reproduce live: %d of 8\n",
              beh[1], behmatch))
  bad <- bad + (behmatch > 0)
}

cat("\nWHAT THIS DOES NOT ESTABLISH: Route A is a label tie to the study's own\n",
    "question-definition sheet and cannot detect an error inside that sheet. Route B\n",
    "ties each IRW code to its raw LimeSurvey column on the respondents of 2 of the 50\n",
    "export files only (not a full re-run). Neither route tests the unlabelled\n",
    "midpoints resp=2..6 (shipped blank by design) or the non-English administered\n",
    "wordings, which are not shipped.\n", sep = "")

cat(if (bad == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

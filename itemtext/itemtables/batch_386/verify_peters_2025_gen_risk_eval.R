# verify_peters_2025_gen_risk_eval.R
#
# CLAIM UNDER TEST (Step 5b): the two IRW item codes are the lower-cased tails
# of the Your COVID-19 Risk LimeSurvey question codes GenEvHospital and
# GenEvSymptoms (data/peters_2025_covid19_risk_dcts.py: ^Gen(Ex|Ev)(.+)$, Ev ->
# gen_risk_eval, tail lower-cased), and the text shipped for each is that code's
# own row in the project's DMQs sheet (worksheet 'en'):
#   hospital -> "I prefer to ..."      1 = "certainly not end up in a hospital" .. 5 = "certainly end up in a hospital"
#   symptoms -> "I prefer to get ..."  1 = "no symptoms"                        .. 5 = "severe symptoms"
#
# What would break if the mapping were wrong:
#   A. shipped stem/anchors would differ from the sheet row carrying that code;
#   B. RAW->LIVE CELL MATCH: per (item x resp) counts for the respondents of
#      two raw export files, read from raw columns GenEvHospital / GenEvSymptoms,
#      would not equal the live table's counts for the same ids. The two items'
#      raw distributions differ (e.g. sid 100103: hospital n=7, symptoms n=18),
#      so a hospital<->symptoms swap breaks this, and so would the table having
#      been built from the AMENDED variants GenEvHospital2 / GenEvSymptoms2
#      (different stems, 'For me, avoiding ... is ...'), which is also printed.
#   C. DIRECTION (content): the stems ask what the respondent PREFERS, so the
#      majority of any sample should sit at resp=1 ('certainly not end up in a
#      hospital', 'no symptoms'). If option direction were reversed, a majority
#      would be preferring to certainly be hospitalised / have severe symptoms.
#
# Sources fetched live: DMQs sheet key 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc
# (named in the taskSpecs of https://your-risk.com/v1-translation-results-limesurvey);
# raw exports from https://gitlab.com/a-bc/your-covid-19-risk-data (data/);
# irw::irw_fetch() (served from the local irw cache when present).

suppressMessages(library(irw))

TABLE <- "peters_2025_gen_risk_eval"
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
    items_csv <- file.path("itemtables/batch_386", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

bad <- 0L

## ---- CHECK A: shipped text vs that code's own sheet row ----
dmq <- read.csv(SHEET, stringsAsFactors = FALSE)
dmq <- dmq[grepl("^GenEv", dmq$id), ]
cat("sheet rows matching ^GenEv:", paste(dmq$id, collapse = ", "), "\n")
cat("\n-- CHECK A: stem and endpoint anchors vs sheet row --\n")
for (cd in c("hospital", "symptoms")) {
    row <- dmq[tolower(sub("^GenEv", "", dmq$id)) == cd, ]
    st <- unique(ship$item_text[ship$item == cd])
    lo <- ship$option_text[ship$item == cd & ship$resp == 1L]
    hi <- ship$option_text[ship$item == cd & ship$resp == 5L]
    ok <- nrow(row) == 1L && identical(st, trimws(row$subquestion_en)) &&
          identical(lo, trimws(row$bottom_anchor_bare)) &&
          identical(hi, trimws(row$top_anchor_bare))
    cat(sprintf("%-9s sheet id %-14s stem '%s' | 1='%s' | 5='%s'  %s\n", cd, row$id,
                st, lo, hi, if (ok) "ok" else "MISMATCH"))
    bad <- bad + !ok
}

## ---- CHECK B: raw -> live cell-for-cell match on two export files ----
d <- irw::irw_fetch(TABLE)
cat("\n-- CHECK B: per item x resp counts, raw export column vs live table, same ids --\n")
for (f in FILES) {
    tf <- tempfile(fileext = ".csv")
    download.file(paste0(RAW, f), tf, quiet = TRUE)
    r <- read.csv(tf, stringsAsFactors = FALSE, check.names = FALSE)
    sid <- sub(".*sid-(\\d+).*", "\\1", f)
    r$gid <- paste0(sid, "-", r[[1]])
    lv <- d[d$id %in% r$gid, ]
    cat(sprintf("%s: %d raw rows, %d live rows for these ids\n", f, nrow(r), nrow(lv)))
    tab <- function(v) { v <- v[!is.na(v) & v >= 1 & v <= 5]
                         as.integer(table(factor(v, levels = 1:5))) }
    for (cd in c("hospital", "symptoms")) {
        col <- paste0("GenEv", tools::toTitleCase(cd))
        rawc <- tab(r[[col]]); livec <- tab(lv$resp[lv$item == cd])
        amc  <- tab(r[[paste0(col, "2")]])
        other <- tab(r[[paste0("GenEv", tools::toTitleCase(setdiff(c("hospital", "symptoms"), cd)))]])
        ok <- identical(rawc, livec)
        cat(sprintf("  %-9s live %-18s raw %-14s %-18s  [rival: other item %s; amended %s2 %s]  %s\n",
                    cd, paste(livec, collapse = "/"), col, paste(rawc, collapse = "/"),
                    paste(other, collapse = "/"), col, paste(amc, collapse = "/"),
                    if (ok) "ok" else "MISMATCH"))
        bad <- bad + !ok
    }
}

## ---- CHECK C: direction, from content ----
cat("\n-- CHECK C: share at resp=1 (the non-harm anchor) should be a majority --\n")
for (cd in c("hospital", "symptoms")) {
    v <- d$resp[d$item == cd]
    p1 <- mean(v == 1); p5 <- mean(v == 5)
    ok <- p1 > 0.5 && p1 > p5
    cat(sprintf("%-9s n=%d mean=%.2f  resp=1 %.1f%% ('%s')  resp=5 %.1f%% ('%s')  %s\n",
                cd, length(v), mean(v), 100 * p1,
                ship$option_text[ship$item == cd & ship$resp == 1L], 100 * p5,
                ship$option_text[ship$item == cd & ship$resp == 5L], if (ok) "ok" else "MISMATCH"))
    bad <- bad + !ok
}

cat("\nWhat these checks do NOT establish: B ties each IRW code to its raw LimeSurvey\n",
    "column (and rules out a swap and the amended *2 variants) on the respondents of\n",
    "two of the 50 export files only; the column->wording tie rests on the DMQs sheet's\n",
    "own `id` column (A), and no check can detect an error inside that sheet. C is a\n",
    "content plausibility argument for direction, not a proof; it does not separate\n",
    "the two items (both are desirable-at-bottom). Midpoints 2-4 are unlabelled in the\n",
    "source and ship blank; nothing here tests them.\n", sep = "")

cat(if (bad == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

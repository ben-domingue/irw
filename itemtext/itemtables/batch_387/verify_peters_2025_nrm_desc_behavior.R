# Step 5b verification for peters_2025_nrm_desc_behavior (batch_387).
# Copied from references/verify_template.R and adapted.
#
# CLAIM UNDER TEST
#   Each IRW item code is the study's own LimeSurvey question code with the
#   "NrmDeBeh" prefix stripped and the remainder lower-cased (NrmDeBehDoctor ->
#   doctor, NrmDeBehLikeYou -> likeyou, ... 8 items), per the regex
#   ^NrmDe(Beh|Id)(.+)$ in data/peters_2025_covid19_risk_dcts.py, and the
#   item_text / endpoint anchors shipped for each code are those of the row whose
#   `id` is exactly that raw question code in the project's DMQs question-definition
#   sheet (Google Sheets key 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc, worksheet
#   `en`). resp 1 = bottom anchor, resp 5 = top anchor, resp 2-4 blank.
#
# CHECK A (code<->text tie): fetch the sheet, re-derive the IRW code from each
#   NrmDeBeh* row's `id`, and require that the shipped item_text and resp=1/resp=5
#   option_text for that code equal that row's subquestion_en / bottom_anchor_bare /
#   top_anchor_bare, and that the derived code set equals the live item set.
# CHECK B (raw column -> IRW code, cell level): download the five raw LimeSurvey
#   exports for sid 100110, melt the NrmDeBeh* columns (the NrmDe*Seq randomisation
#   slot columns are not matched by the prefix), keep 1..5 (code 0 = not applicable
#   is dropped, as the processing script does), build id "<sid>-<orig_id>", label
#   with the lower-cased suffix, and require an EXACT match on every (id, item,
#   resp) cell against irw::irw_fetch(). A permutation of any two codes moves that
#   item's response vector onto the wrong code and breaks the cell-level merge, so
#   every item is distinguished from every other item.
#
# WHAT IT DOES NOT ESTABLISH
#   - Check A is a source-label tie: it cannot detect an error inside the sheet
#     itself (e.g. a sheet row whose id and wording were mismatched upstream).
#   - The anchor direction (code 1 = bottom anchor) is read off the published
#     DMQ_scales key (uni: code 1 = "(1)", 5 = "(5)") and the sheet's own
#     bottom_anchor_en "very improbable (1)" / top_anchor_en "very probable (5)";
#     it is not inferred from response data here.
#   - Only one deployment (sid 100110) is compared cell by cell; the live table
#     pools 21. None of the non-English administered wordings are tested.

suppressMessages(library(irw))

TABLE <- "peters_2025_nrm_desc_behavior"
SHEET <- paste0("https://docs.google.com/spreadsheets/d/",
                "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                "/gviz/tq?tqx=out:csv&sheet=en")
SID   <- "100110"
BASE  <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
FILES <- c("YCR-dataPipeline--sid-100110--rids-1-2583.csv",
           "YCR-dataPipeline--sid-100110--rids-2584-5166.csv",
           "YCR-dataPipeline--sid-100110--rids-5167-9096.csv",
           "YCR-dataPipeline--sid-100110--rids-9097-13026.csv",
           "YCR-dataPipeline--sid-100110--rids-13027-13135.csv")

args <- grep("^--file=", commandArgs(FALSE), value = TRUE)
items_csv <- if (length(args)) file.path(dirname(sub("^--file=", "", args[1])),
                 paste0(TABLE, "__items.csv")) else ""
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_387", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

## ---- CHECK A ----
dmq <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = FALSE)
dmq <- dmq[grepl("^NrmDeBeh", dmq$id), ]
dmq$code <- tolower(sub("^NrmDeBeh", "", dmq$id))
cat("sheet rows matching ^NrmDeBeh:", paste(dmq$id, collapse = ", "), "\n")
setA <- nrow(dmq) == 8L && setequal(dmq$code, unique(d$item)) &&
        !anyDuplicated(dmq$code)
cat(sprintf("derived codes == live item set (8): %s\n", setA))
cat("\n-- CHECK A: stem and endpoint anchors vs that code's own sheet row --\n")
okA <- 0L
for (cd in sort(dmq$code)) {
    row <- dmq[dmq$code == cd, ]
    st <- unique(ship$item_text[ship$item == cd])
    lo <- ship$option_text[ship$item == cd & ship$resp == 1L]
    hi <- ship$option_text[ship$item == cd & ship$resp == 5L]
    mid <- ship$option_text[ship$item == cd & ship$resp %in% 2:4]
    ok <- nrow(row) == 1L && identical(st, trimws(row$subquestion_en)) &&
          identical(lo, trimws(row$bottom_anchor_bare)) &&
          identical(hi, trimws(row$top_anchor_bare)) &&
          length(mid) == 3L && all(is.na(mid) | mid == "")
    okA <- okA + ok
    cat(sprintf("%-8s %-17s %s\n", cd, row$id, if (ok) "match" else "MISMATCH"))
}
cat(sprintf("CHECK A: %d/8 codes match their own sheet row\n", okA))

## ---- CHECK B ----
cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)
long <- do.call(rbind, lapply(FILES, function(f) {
    p <- file.path(cache, f)
    if (!file.exists(p)) utils::download.file(paste0(BASE, f), p, quiet = TRUE)
    df <- utils::read.csv(p, colClasses = "character", check.names = FALSE)
    names(df)[1] <- "orig_id"
    cols <- grep("^NrmDeBeh", names(df), value = TRUE)
    stopifnot(setequal(cols, dmq$id))
    do.call(rbind, lapply(cols, function(cn) {
        v <- suppressWarnings(as.numeric(df[[cn]]))
        keep <- !is.na(v) & v >= 1 & v <= 5
        if (!any(keep)) return(NULL)
        data.frame(id = paste0(SID, "-", df$orig_id[keep]),
                   item = tolower(sub("^NrmDeBeh", "", cn)),
                   resp_raw = v[keep], stringsAsFactors = FALSE)
    }))
}))
live <- d[grepl(paste0("^", SID, "-"), d$id), c("id", "item", "resp")]
names(live)[3] <- "resp_live"
m <- merge(long, live, by = c("id", "item"), all = TRUE)
unmatched <- sum(is.na(m$resp_raw) | is.na(m$resp_live))
mismatch  <- sum(m$resp_raw != m$resp_live, na.rm = TRUE)

cat(sprintf("\n-- CHECK B: raw sid %s exports vs live --\n", SID))
cat(sprintf("raw cells re-derived : %d\n", nrow(long)))
cat(sprintf("live cells for sid   : %d\n", nrow(live)))
cat(sprintf("cells on one side only: %d\n", unmatched))
cat(sprintf("cells disagreeing     : %d\n\n", mismatch))
cat(sprintf("%-8s %6s %6s %9s %9s %8s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "n_disagr"))
items <- sort(unique(long$item))
for (i in items) {
    a <- long[long$item == i, ]; b <- live[live$item == i, ]; mi <- m[m$item == i, ]
    cat(sprintf("%-8s %6d %6d %9.3f %9.3f %8d\n", i, nrow(a), nrow(b),
                mean(a$resp_raw), mean(b$resp_live),
                sum(mi$resp_raw != mi$resp_live, na.rm = TRUE)))
}
okB <- nrow(long) > 0 && unmatched == 0 && mismatch == 0 && length(items) == 8

cat("\nNot established here: an error inside the DMQs sheet itself, the anchor\n",
    "direction (published key, not inferred), and the 20 other deployments.\n", sep = "")
cat(if (setA && okA == 8L && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

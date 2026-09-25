# verify_peters_2025_nrm_inj_motivation.R  (batch_387)
#
# CLAIM UNDER TEST (Step 5b): each of the 10 live item codes carries the
# motivation-to-comply stem of the SAME referent, taken from that code's own row
# of the study's DMQs question-definition sheet (Google Sheet key
# 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc, worksheet 'en'):
#   boss -> "... I want to do what my boss thinks I should do.", etc.,
# with resp=1 the bottom anchor "not at all" and resp=5 the top anchor "very much".
#
# What would break if the mapping were wrong:
#   A. CODE RE-DERIVATION + TEXT: the sheet's `id` column holds the LimeSurvey
#      question code. Applying the project's own code shortening (dmqReplacements:
#      Neighbourhood -> Neighbrhd) and the IRW script's rename
#      (data/peters_2025_covid19_risk_dcts.py: ^NrmIn(Ap|Mc)(.+)$, Mc ->
#      nrm_inj_motivation, tail lower-cased) must reproduce the live item set
#      one-to-one and onto, and each shipped stem/anchor must equal the row that
#      derives to that code. Also: the DMQ_scales key must state uni codes 1..5
#      as displayed (1)..(5), and the sheet's *_anchor_en must carry "(1)" on the
#      bottom anchor and "(5)" on the top one (this is what fixes direction).
#   B. RAW -> LIVE CELL MATCH: for every respondent of three raw export files,
#      the value in raw column NrmInMc<Referent> must equal the live resp for
#      (that id, that item), cell for cell. Rival columns are printed: if the
#      item<->column tie were permuted, the matched-cell count against the
#      rival column collapses.
#   C. CLASS CHECK (data-side, partial): code 0 "(not applicable)" is dropped by
#      the IRW script, so the two workplace referents (boss, colleagues) should
#      retain the fewest responses.

suppressMessages(library(irw))
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE  <- "peters_2025_nrm_inj_motivation"
SHEET  <- paste0("https://docs.google.com/spreadsheets/d/",
                 "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                 "/gviz/tq?tqx=out:csv&sheet=en")
SCALES <- paste0("https://docs.google.com/spreadsheets/d/",
                 "1GFFeIrwW9KVZxRCr4QrmQcVKDc5aSRu6VI4oWdQVkvw",
                 "/gviz/tq?tqx=out:csv&sheet=en")
RAW    <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
CACHE  <- ".cache/peters_2025_nrm_inj_motivation/"
FILES  <- c("YCR-dataPipeline--sid-100102--rids-1-141.csv",
            "YCR-dataPipeline--sid-100103--rids-1-1479.csv",
            "YCR-dataPipeline--sid-100105--rids-1-2450.csv")

args <- grep("^--file=", commandArgs(FALSE), value = TRUE)
items_csv <- if (length(args)) file.path(dirname(sub("^--file=", "", args[1])),
                 paste0(TABLE, "__items.csv")) else ""
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_387", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

bad <- 0L

## ---- CHECK A ----
sheet <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = FALSE)
mc <- sheet[grepl("^NrmInMc", sheet$id), ]
shorten <- function(x) {
  reps <- c(generic = "gnrc", Decline = "Decl", Supermarket = "Sprmrkt",
            Neighbourhood = "Neighbrhd", NrmDeIde = "NrmDeId",
            Respons = "Rspns", Flip = "Fl")
  for (k in names(reps)) x <- gsub(k, reps[[k]], x)
  x
}
mc$raw_col <- shorten(mc$id)
mc$derived <- tolower(sub("^NrmInMc", "", mc$raw_col))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- sort(s$items)
cat("== CHECK A: re-derive IRW codes from the sheet's own question codes ==\n")
miss_live  <- setdiff(live, mc$derived); miss_sheet <- setdiff(mc$derived, live)
cat(sprintf("sheet NrmInMc rows: %d | live items: %d | live not derived: %d | derived not live: %d\n",
            nrow(mc), length(live), length(miss_live), length(miss_sheet)))
bij <- length(miss_live) == 0 && length(miss_sheet) == 0 &&
       length(unique(mc$derived)) == length(live)
bad <- bad + !bij
ok_txt <- 0L
for (i in order(mc$derived)) {
    cd <- mc$derived[i]; rows <- ship[ship$item == cd, ]
    st_ok <- identical(unique(rows$item_text), trimws(mc$subquestion_en[i]))
    lo <- rows$option_text[rows$resp == 1]; hi <- rows$option_text[rows$resp == 5]
    mid <- rows$option_text[rows$resp %in% 2:4]
    an_ok <- identical(lo, trimws(mc$bottom_anchor_bare[i])) &&
             identical(hi, trimws(mc$top_anchor_bare[i])) && all(is.na(mid) | mid == "")
    dir_ok <- grepl("\\(1\\)$", mc$bottom_anchor_en[i]) && grepl("\\(5\\)$", mc$top_anchor_en[i])
    ok <- st_ok && an_ok && dir_ok
    ok_txt <- ok_txt + ok
    cat(sprintf("%-18s -> %-10s stem=%-5s anchors=%-5s dir(1..5)=%-5s %s\n", mc$raw_col[i], cd,
                st_ok, an_ok, dir_ok, sub(".*I want to do what ", "", mc$subquestion_en[i])))
}
cat(sprintf("shipped text equal to the deriving row: %d/%d\n", ok_txt, nrow(mc)))
bad <- bad + (ok_txt != nrow(mc))
sc <- read.csv(SCALES, stringsAsFactors = FALSE, check.names = FALSE)
uni <- sc[sc$scale_type == "uni", c("limesurvey_answer_code", "text_en")]
key_ok <- identical(as.integer(uni$limesurvey_answer_code), 1:5) &&
          identical(uni$text_en, sprintf("(%d)", 1:5))
cat(sprintf("DMQ_scales uni key: %s  -> %s\n",
            paste(uni$limesurvey_answer_code, uni$text_en, collapse = ", "), key_ok))
bad <- bad + !key_ok

## ---- CHECK B ----
d <- irw::irw_fetch(TABLE)
cat("\n== CHECK B: raw column NrmInMc<X> vs live (id, item), cell for cell ==\n")
tot_eq <- 0L; tot_ne <- 0L
for (f in FILES) {
    path <- cached_source(paste0(CACHE, f), paste0(RAW, f))
    r <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
    sid <- sub(".*sid-(\\d+).*", "\\1", f)
    r$gid <- paste0(sid, "-", r[[1]])
    lv <- d[d$id %in% r$gid, ]
    cat(sprintf("%s: %d raw rows, %d live rows for these ids\n", f, nrow(r), nrow(lv)))
    for (i in order(mc$derived)) {
        cd <- mc$derived[i]; col <- mc$raw_col[i]
        v <- suppressWarnings(as.numeric(r[[col]]))
        keep <- !is.na(v) & v >= 1 & v <= 5
        raw_k <- setNames(v[keep], r$gid[keep])
        lvi <- lv[lv$item == cd, ]; live_k <- setNames(lvi$resp, lvi$id)
        same_ids <- setequal(names(raw_k), names(live_k))
        eq <- if (same_ids) sum(raw_k[names(live_k)] == live_k) else 0L
        ne <- length(live_k) - eq + if (same_ids) 0L else 1L
        # best rival: another NrmInMc column's values at the same live ids
        rival <- sapply(setdiff(mc$raw_col, col), function(rc) {
            rv <- suppressWarnings(as.numeric(r[[rc]]))[match(names(live_k), r$gid)]
            sum(!is.na(rv) & rv == live_k)
        })
        tot_eq <- tot_eq + eq; tot_ne <- tot_ne + ne
        cat(sprintf("  %-10s n_live=%4d n_raw=%4d  cells equal %4d / %4d  (best rival column %s: %d)\n",
                    cd, length(live_k), length(raw_k), eq, length(live_k),
                    if (length(rival)) names(which.max(rival)) else "-", if (length(rival)) max(rival) else 0L))
    }
}
cat(sprintf("TOTAL cells equal %d, unequal/unmatched %d\n", tot_eq, tot_ne))
bad <- bad + (tot_ne != 0L) + (tot_eq == 0L)

## ---- CHECK C ----
cat("\n== CHECK C: workplace referents should retain fewest responses ==\n")
pi <- as.data.frame(s$per_item); pi <- pi[order(pi$n), ]
cat(paste(sprintf("%s=%d", pi$item, pi$n), collapse = "  "), "\n")
c_ok <- setequal(pi$item[1:2], c("boss", "colleagues"))
cat(sprintf("two smallest are {boss, colleagues}: %s (%d, %d vs next %d)\n",
            c_ok, pi$n[1], pi$n[2], pi$n[3]))
bad <- bad + !c_ok

cat("\nWHAT THIS DOES NOT ESTABLISH: B ties each IRW code to its raw LimeSurvey column\n",
    "on the respondents of 3 of the 50 export files only (sids 100102, 100103, 100105);\n",
    "the column->wording tie rests on the DMQs sheet's own `id` column (A), and no check\n",
    "here can detect an error inside that sheet. C separates only the {boss, colleagues}\n",
    "class. Direction rests on the published answer-code key and the sheet's '(1)'/'(5)'\n",
    "anchor suffixes, not on a data-side test. Midpoints 2-4 are unlabelled in the source\n",
    "and ship blank; the non-English administered wordings are not shipped or tested.\n", sep = "")

cat(if (bad == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

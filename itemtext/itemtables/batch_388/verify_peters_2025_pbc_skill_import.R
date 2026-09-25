# verify_peters_2025_pbc_skill_import.R  (batch_388)
#
# CLAIM UNDER TEST (Step 5b): each of the 14 live item codes carries the
# subskill-importance stem of the SAME subskill, taken from that code's own row
# of the study's DMQs question-definition sheet (Google Sheet key
# 1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc, worksheet 'en'):
#   walkfast -> "... being able to walk fast is…", declhug -> "... decline when
#   somebody wants to give me a hug is…", etc.,
# with resp=1 the bottom anchor "not at all important" and resp=5 the top
# anchor "extremely important".
#
# What would break if the mapping were wrong:
#   A. CODE RE-DERIVATION + TEXT: the sheet's `id` column holds the LimeSurvey
#      question code before the project's code shortening. Applying that
#      shortening (dmqReplacements in the project's CC0 build script:
#      Decline -> Decl, which is what turns PbcSkImDeclineGreeting/-Hug into the
#      raw columns PbcSkImDeclGreeting/-Hug) and the IRW script's rename
#      (data/peters_2025_covid19_risk_dcts.py: ^PbcSk(Pr|Im)(.+)$, Im ->
#      pbc_skill_import, tail lower-cased) must reproduce the live item set
#      one-to-one and onto, and each shipped stem/anchor must equal the row that
#      derives to that code. The DMQ_scales key must state uni codes 1..5 as
#      displayed (1)..(5), and the sheet's *_anchor_en must end "(1)" on the
#      bottom anchor and "(5)" on the top one (this is what fixes direction).
#   B. RAW -> LIVE CELL MATCH: for every respondent of four raw export files,
#      the value in raw column PbcSkIm<Subskill> must equal the live resp at
#      (that id, that item), cell for cell, with identical id sets. The best
#      rival column (any other PbcSkIm* column, or the same subskill's PbcSkPr*
#      presence column that feeds the sibling table pbc_skill_prob) is printed:
#      if the item<->column tie were permuted, the match against the rival
#      collapses.
#   C. CLASS CHECK (data-side, partial): the deployed survey definition
#      (gitlab.com/a-bc/your-covid-19-risk v1/operationalizations/limesurvey/
#      v1.01/limesurvey_survey_100101.lss) makes 7 of the 14 PbcSkIm questions
#      irrelevant for country ro00 (its relevance regex adds ^ro00$ for
#      DecCont, ChildBad, ChildReject, WalkFast, MeetCare, TellOthers,
#      TechTouch). So in the live table, ro00 respondents must have answered
#      exactly the other 7 codes. Hard-coded from that file (read 2026-09-24).

suppressMessages(library(irw))
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE  <- "peters_2025_pbc_skill_import"
SHEET  <- paste0("https://docs.google.com/spreadsheets/d/",
                 "1B9TLM1ro2yxEmfzWo99T6w0XADLeeJVXPvnFoEc0-vc",
                 "/gviz/tq?tqx=out:csv&sheet=en")
SCALES <- paste0("https://docs.google.com/spreadsheets/d/",
                 "1GFFeIrwW9KVZxRCr4QrmQcVKDc5aSRu6VI4oWdQVkvw",
                 "/gviz/tq?tqx=out:csv&sheet=en")
RAW    <- "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
CACHE  <- ".cache/peters_2025_pbc_skill_import/"
FILES  <- c("YCR-dataPipeline--sid-100101--rids-1-4849.csv",
            "YCR-dataPipeline--sid-100102--rids-1-141.csv",
            "YCR-dataPipeline--sid-100103--rids-1-1479.csv",
            "YCR-dataPipeline--sid-100105--rids-1-2450.csv")

args <- grep("^--file=", commandArgs(FALSE), value = TRUE)
items_csv <- if (length(args)) file.path(dirname(sub("^--file=", "", args[1])),
                 paste0(TABLE, "__items.csv")) else ""
if (!file.exists(items_csv))
    items_csv <- file.path("itemtables/batch_388", paste0(TABLE, "__items.csv"))
ship <- read.csv(items_csv, stringsAsFactors = FALSE)

bad <- 0L

## ---- CHECK A ----
sheet <- read.csv(SHEET, stringsAsFactors = FALSE, check.names = FALSE)
im <- sheet[grepl("^PbcSkIm", sheet$id), ]
shorten <- function(x) {
  reps <- c(generic = "gnrc", Decline = "Decl", Supermarket = "Sprmrkt",
            Neighbourhood = "Neighbrhd", NrmDeIde = "NrmDeId",
            Respons = "Rspns", Flip = "Fl")
  for (k in names(reps)) x <- gsub(k, reps[[k]], x)
  x
}
im$raw_col <- shorten(im$id)
im$pr_col  <- sub("^PbcSkIm", "PbcSkPr", im$raw_col)
im$derived <- tolower(sub("^PbcSkIm", "", im$raw_col))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live <- sort(s$items)
cat("== CHECK A: re-derive IRW codes from the sheet's own question codes ==\n")
miss_live  <- setdiff(live, im$derived); miss_sheet <- setdiff(im$derived, live)
cat(sprintf("sheet PbcSkIm rows: %d | live items: %d | live not derived: %d | derived not live: %d\n",
            nrow(im), length(live), length(miss_live), length(miss_sheet)))
bij <- length(miss_live) == 0 && length(miss_sheet) == 0 &&
       length(unique(im$derived)) == length(live)
bad <- bad + !bij
ok_txt <- 0L
for (i in order(im$derived)) {
    cd <- im$derived[i]; rows <- ship[ship$item == cd, ]
    st_ok <- identical(unique(rows$item_text), trimws(im$subquestion_en[i]))
    lo <- rows$option_text[rows$resp == 1]; hi <- rows$option_text[rows$resp == 5]
    mid <- rows$option_text[rows$resp %in% 2:4]
    an_ok <- identical(lo, trimws(im$bottom_anchor_bare[i])) &&
             identical(hi, trimws(im$top_anchor_bare[i])) && all(is.na(mid) | mid == "")
    dir_ok <- grepl("\\(1\\)$", im$bottom_anchor_en[i]) && grepl("\\(5\\)$", im$top_anchor_en[i])
    ok <- st_ok && an_ok && dir_ok
    ok_txt <- ok_txt + ok
    cat(sprintf("%-22s -> %-12s stem=%-5s anchors=%-5s dir(1..5)=%-5s %s\n", im$raw_col[i], cd,
                st_ok, an_ok, dir_ok, sub(".*distance from others, ", "", im$subquestion_en[i])))
}
cat(sprintf("shipped text equal to the deriving row: %d/%d\n", ok_txt, nrow(im)))
bad <- bad + (ok_txt != nrow(im))
sc <- read.csv(SCALES, stringsAsFactors = FALSE, check.names = FALSE)
uni <- sc[sc$scale_type == "uni", c("limesurvey_answer_code", "text_en")]
key_ok <- identical(as.integer(uni$limesurvey_answer_code), 1:5) &&
          identical(uni$text_en, sprintf("(%d)", 1:5))
cat(sprintf("DMQ_scales uni key: %s  -> %s\n",
            paste(uni$limesurvey_answer_code, uni$text_en, collapse = ", "), key_ok))
bad <- bad + !key_ok

## ---- CHECK B ----
d <- irw::irw_fetch(TABLE)
cat("\n== CHECK B: raw column PbcSkIm<X> vs live (id, item), cell for cell ==\n")
tot_eq <- 0L; tot_ne <- 0L
# pooled over files, per item: live cells, and cells matched by each rival column
pool_n <- setNames(integer(nrow(im)), im$derived)
pool_rival <- list()
for (f in FILES) {
    path <- cached_source(paste0(CACHE, f), paste0(RAW, f))
    r <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
    sid <- sub(".*sid-(\\d+).*", "\\1", f)
    r$gid <- paste0(sid, "-", r[[1]])
    lv <- d[d$id %in% r$gid, ]
    cat(sprintf("%s: %d raw rows, %d live rows for these ids\n", f, nrow(r), nrow(lv)))
    for (i in order(im$derived)) {
        cd <- im$derived[i]; col <- im$raw_col[i]
        v <- suppressWarnings(as.numeric(r[[col]]))
        keep <- !is.na(v) & v >= 1 & v <= 5
        raw_k <- setNames(v[keep], r$gid[keep])
        lvi <- lv[lv$item == cd, ]; live_k <- setNames(lvi$resp, lvi$id)
        same_ids <- setequal(names(raw_k), names(live_k))
        eq <- if (same_ids) sum(raw_k[names(live_k)] == live_k) else 0L
        ne <- length(live_k) - eq + if (same_ids) 0L else 1L
        rivals <- c(setdiff(im$raw_col, col), im$pr_col[i])
        rival <- sapply(rivals, function(rc) {
            rv <- suppressWarnings(as.numeric(r[[rc]]))[match(names(live_k), r$gid)]
            sum(!is.na(rv) & rv == live_k)
        })
        pool_n[cd] <- pool_n[cd] + length(live_k)
        pr <- pool_rival[[cd]]; if (is.null(pr)) pr <- setNames(numeric(0), character(0))
        for (rc in names(rival)) pr[rc] <- (if (is.na(pr[rc])) 0 else pr[rc]) + rival[[rc]]
        pool_rival[[cd]] <- pr
        tot_eq <- tot_eq + eq; tot_ne <- tot_ne + ne
        cat(sprintf("  %-12s n_live=%3d n_raw=%3d  cells equal %3d / %3d  (best rival %s: %d; own Pr column: %d)\n",
                    cd, length(live_k), length(raw_k), eq, length(live_k),
                    names(which.max(rival)), max(rival), rival[[im$pr_col[i]]]))
    }
}
cat(sprintf("TOTAL cells equal %d, unequal/unmatched %d\n", tot_eq, tot_ne))
cat("\nPooled over the 4 files: own column matches every live cell; best rival column:\n")
worst_rival <- 0
for (cd in sort(im$derived)) {
    pr <- pool_rival[[cd]]; b <- names(which.max(pr))
    share <- max(pr) / pool_n[[cd]]; worst_rival <- max(worst_rival, share)
    cat(sprintf("  %-12s own %3d/%3d | best rival %-20s %3d/%3d (%.2f)\n",
                cd, pool_n[[cd]], pool_n[[cd]], b, as.integer(max(pr)), pool_n[[cd]], share))
}
cat(sprintf("worst pooled rival share %.2f (a permutation needs 1.00)\n", worst_rival))
bad <- bad + (tot_ne != 0L) + (tot_eq == 0L) + (worst_rival >= 1)

## ---- CHECK C ----
cat("\n== CHECK C: country ro00 answered exactly the 7 codes the deployed .lss leaves relevant ==\n")
LSS_RO00_EXCLUDED <- c("deccont", "childbad", "childreject", "walkfast",
                       "meetcare", "tellothers", "techtouch")
ro <- table(d$item[d$cov_country == "ro00"])
ro <- ro[ro > 0]
cat(paste(sprintf("%s=%d", names(ro), as.integer(ro)), collapse = "  "), "\n")
c_ok <- setequal(names(ro), setdiff(live, LSS_RO00_EXCLUDED))
cat(sprintf("ro00 item set == live minus the 7 ro00-excluded questions: %s\n", c_ok))
bad <- bad + !c_ok

cat("\nWHAT THIS DOES NOT ESTABLISH: B ties each IRW code to its raw LimeSurvey column\n",
    "on the respondents of 4 of the 50 export files only (sids 100101 file 1, 100102,\n",
    "100103, 100105); the column->wording tie rests on the DMQs sheet's own `id` column\n",
    "(A), and no check here can detect an error inside that sheet. Direction rests on the\n",
    "published answer-code key and the sheet's '(1)'/'(5)' anchor suffixes, not on a\n",
    "data-side test. Midpoints 2-4 are unlabelled in the source and ship blank; the\n",
    "non-English administered wordings are not shipped or tested. C separates only the\n",
    "two 7-item classes, not items within a class.\n", sep = "")

cat(if (bad == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

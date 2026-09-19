# verify_MGSISGCLQ_Hollyhead_2018.R
#
# CLAIM UNDER TEST (two parts):
#   (a) item axis -- the IRW `item` codes ARE the column headers of the OSF deposit's
#       "MGSIS-5 and GCLQ Data.xlsx", so item_text is the administered wording of that
#       exact question. Falsifiable: re-derive the headers from the source file and
#       demand a character-for-character match with the live item set.
#   (b) resp axis -- GCLQ No=0 / Yes=1 and MGSIS Strongly Disagree=1 .. Strongly Agree=4.
#       Falsifiable by route 9: exactly the items that are CONSTANT in the raw file must
#       be the items that are constant live, and at the value the claimed map sends that
#       label to. Under the flipped GCLQ map those two items would sit at 1, not 0.
#
# Fetches live data via irw::irw_table_sets() (server-side aggregates, no export), and
# the source workbook from OSF.

suppressMessages({library(irw); library(openxlsx)})

TABLE <- "MGSISGCLQ_Hollyhead_2018"
XLSX_URL <- "https://osf.io/download/5bf3dae61f01ef00160e90e0/"   # osf.io/f8v5k
CACHE <- file.path(".cache", TABLE, "data.xlsx")

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    download.file(XLSX_URL, CACHE, mode = "wb", quiet = TRUE)
}
raw <- openxlsx::read.xlsx(CACHE)

DROP <- c("Start.time","Completion.time","Email","Name","Total.points","Quiz.feedback",
          "Are.you.a.resident.of.the.UK?","How.old.are.you?",
          paste0("Do.you.have.a.medical.condition.which.affects.your.lower.body.",
                 "or.could.impact.how.you.feel.about.your.genitals?"))
hdr <- names(raw)[!grepl("^(Points|Feedback)\\.-", names(raw))]
src_items <- setdiff(hdr, DROP)

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
live_items <- sort(s$items)

cat("--- (a) item axis: source headers vs live item codes ---\n")
cat(sprintf("source headers (after dropping metadata/demographic cols): %d\n", length(src_items)))
cat(sprintf("live item codes                                          : %d\n", length(live_items)))
only_src  <- setdiff(src_items, live_items)
only_live <- setdiff(live_items, src_items)
cat(sprintf("exact matches: %d/%d | only-in-source: %d | only-in-live: %d\n",
            length(intersect(src_items, live_items)), length(live_items),
            length(only_src), length(only_live)))
if (length(only_src))  cat("  only in source:", paste(only_src,  collapse = " | "), "\n")
if (length(only_live)) cat("  only in live  :", paste(only_live, collapse = " | "), "\n")
# the two characters most likely to break a naive re-derivation
cat("slash/question-mark survivors present live: ",
    sum(grepl("/", live_items)), " with '/', ", sum(grepl("\\?$", live_items)), " ending '?'\n", sep = "")
ok_a <- length(only_src) == 0 && length(only_live) == 0

cat("\n--- (b) resp axis: raw label counts vs live per-item resp levels (route 9) ---\n")
pi <- as.data.frame(s$per_item)
names(pi)[1] <- "item"
LIKERT <- c("Strongly Disagree" = 1, "Disagree" = 2, "Agree" = 3, "Strongly Agree" = 4)
mgsis <- grep("^I\\.", src_items, value = TRUE)

cat(sprintf("%-6s %-58s %5s %5s %5s %9s %9s %7s\n",
            "scale", "item (truncated)", "nRaw", "nLive", "lvls", "raw_min", "live_min", "live_max"))
ok_b <- TRUE
for (it in src_items) {
    v <- raw[[it]]; v <- v[!is.na(v)]
    is_mg <- it %in% mgsis
    mapped <- if (is_mg) unname(LIKERT[v]) else ifelse(v == "Yes", 1, ifelse(v == "No", 0, NA))
    row <- pi[pi$item == it, ]
    agree <- nrow(row) == 1 &&
             row$n             == length(v) &&
             row$n_resp_levels == length(unique(mapped)) &&
             row$resp_min      == min(mapped) &&
             row$resp_max      == max(mapped)
    ok_b <- ok_b && agree
    cat(sprintf("%-6s %-58s %5d %5d %5d %9d %9d %7d%s\n",
                if (is_mg) "MGSIS" else "GCLQ", substr(it, 1, 58),
                length(v), row$n, row$n_resp_levels, min(mapped), row$resp_min, row$resp_max,
                if (agree) "" else "   <-- MISMATCH"))
}

const_raw  <- src_items[vapply(src_items, function(i) length(unique(na.omit(raw[[i]]))) == 1, TRUE)]
const_live <- pi$item[pi$n_resp_levels == 1]
cat("\ndecisive cell -- items constant in the RAW file : ", paste(const_raw, collapse = " | "), "\n", sep = "")
cat("               items constant in the LIVE table: ", paste(const_live, collapse = " | "), "\n", sep = "")
cat("               their live value: ", paste(unique(pi$resp_min[pi$n_resp_levels == 1]), collapse = ","),
    " (both are all-'No' raw, so No=0; the flipped map would put them at 1)\n", sep = "")
ok_c <- setequal(const_raw, const_live) && all(pi$resp_min[pi$n_resp_levels == 1] == 0)

cat("\nNOTE ON SCOPE: (a) distinguishes every item from every other -- the code IS the wording,\n",
    "so a permutation is self-evidently impossible. (b) pins the GCLQ 0/1 direction outright via\n",
    "the two constant items. It does NOT independently pin the MGSIS 1-4 DIRECTION: the raw\n",
    "distribution is skewed toward agreement and a reversed map would mirror it, so that rests on\n",
    "the likert_map in data/MGSISGCLQ_Hollyhead_2018.r. No published per-item statistics exist for\n",
    "this OSF preprint to check it against.\n", sep = "")

cat(sprintf("\n(a) headers==codes: %s | (b) per-item counts/ranges: %s | (c) constant-item cell: %s\n",
            ok_a, ok_b, ok_c))
cat(if (ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

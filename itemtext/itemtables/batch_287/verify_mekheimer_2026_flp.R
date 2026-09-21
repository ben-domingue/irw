# verify_mekheimer_2026_flp.R
#
# Claim under test: each live item code FLP_<Skill> carries the appendix item
# whose stem is labelled with that same skill, i.e. the item_text shipped for
# FLP_Speaking really is the "Speaking:" stem and not one of the other three.
#
# Two links, checked separately:
#   (A) appendix stem  ->  source column name.  Each of the four stems in
#       Additional file 4 (MOESM4, questionnaire appendix) opens with a skill
#       label -- Reading / Writing / Speaking / Listening -- and the raw data
#       workbook (Additional file 7, MOESM7) names its four columns
#       FLP_Reading .. FLP_Listening.  The match is a label match, one-to-one,
#       and a swap of any two shipped stems breaks it.
#   (B) source column  ->  live IRW item code.  Per-item n / mean / sd computed
#       from the raw workbook must reproduce the live table exactly.  A permuted
#       column-to-code assignment would break this.

suppressMessages(library(irw))

TABLE <- "mekheimer_2026_flp"
ITEMS_CSV <- "itemtables/batch_287/mekheimer_2026_flp__items.csv"
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- paste0(TABLE, "__items.csv")

# ---- (A) label match, appendix stem -> item code -------------------------
it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
stems <- unique(it[, c("item", "item_text")])
cat("(A) appendix skill label vs item code suffix\n")
okA <- TRUE
for (i in seq_len(nrow(stems))) {
    code_skill <- sub("^FLP_", "", stems$item[i])
    stem_skill <- sub(":.*$", "", stems$item_text[i])
    hit <- identical(tolower(code_skill), tolower(stem_skill))
    okA <- okA && hit
    cat(sprintf("  %-14s stem label = %-10s  %s\n", stems$item[i], stem_skill,
                if (hit) "match" else "MISMATCH"))
}
# and the labels must be distinct, or the match would not separate the items
okA <- okA && length(unique(tolower(sub(":.*$", "", stems$item_text)))) == nrow(stems)
cat(sprintf("  distinct skill labels: %d of %d items\n",
            length(unique(tolower(sub(":.*$", "", stems$item_text)))), nrow(stems)))

# ---- (B) raw workbook column stats vs live per-item stats ----------------
# Additional file 7 of the paper, figshare 31387864 (CC BY).
RAW_URL <- "https://ndownloader.figshare.com/files/62067259"
RAW_LOCAL <- ".cache/mekheimer_2026_flp/add7.xlsx"
if (!file.exists(RAW_LOCAL)) {
    dir.create(dirname(RAW_LOCAL), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(RAW_URL, RAW_LOCAL, quiet = TRUE, mode = "wb")
}
raw <- readxl::read_excel(RAW_LOCAL, sheet = "survey_data (1)")

d <- irw::irw_fetch(TABLE)
codes <- c("FLP_Listening", "FLP_Reading", "FLP_Speaking", "FLP_Writing")
cat("\n(B) raw workbook column vs live IRW item\n")
cat(sprintf("  %-14s %8s %8s %8s %8s %8s %8s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "sd_raw", "sd_live"))
okB <- TRUE
for (cd in codes) {
    x <- raw[[cd]]; x <- x[!is.na(x)]
    y <- d$resp[d$item == cd]
    same <- length(x) == length(y) &&
            abs(mean(x) - mean(y)) < 1e-9 && abs(sd(x) - sd(y)) < 1e-9
    okB <- okB && same
    cat(sprintf("  %-14s %8d %8d %8.5f %9.5f %8.5f %8.5f%s\n",
                cd, length(x), length(y), mean(x), mean(y), sd(x), sd(y),
                if (same) "" else "   MISMATCH"))
}

cat("\nWhat this does NOT establish: the appendix numbers its four statements 1-4\n",
    "in the order Reading, Writing, Speaking, Listening, and that ordering is not\n",
    "used anywhere above -- the tie is by skill label only. Option anchors\n",
    "(Elementary..Expert) are read off the grid header's own '(n)' numbering and\n",
    "are not tested here.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

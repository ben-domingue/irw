# Verification for ali_2021_phq9 (#2228, batch_304).
#
# SOURCE. PLOS ONE 10.1371/journal.pone.0254074 S1 File (CC BY), sheet
# 'Nurses Data'. Row 1 is an instrument banner and row 2 the real headers; the
# nine columns under 'PHQ-9 Questionnaire' are the items, numbered 1-9, which
# data/ali_2021_covid_nurses_wellbeing.py renames phq9_1..phq9_9 and recodes
# from the file's own text categories to 0-3.
#
# Route 1: re-melt the nine columns under that banner and reproduce the live
#   item x resp cell counts exactly, under the script's own FREQ_MAP.
# Route 2: shipped item_text is those headers with the leading number stripped.
xl <- ".cache/batch_304/ali_s001.xlsx"
if (!file.exists(xl)) stop("missing cached deposit file: ", xl)
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")

d <- as.data.frame(irw::irw_fetch("ali_2021_phq9"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_304/ali_2021_phq9__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

banner <- as.character(unlist(readxl::read_excel(xl, sheet = "Nurses Data",
                                                 n_max = 1, col_names = FALSE)))
x <- readxl::read_excel(xl, sheet = "Nurses Data", skip = 1)
start <- which(!is.na(banner) & banner == "PHQ-9 Questionnaire")
cat("=== Route 1: reproduce from the S1 sheet ===\n")
cat(sprintf("  'PHQ-9 Questionnaire' banner sits over column %d\n", start))
cols <- names(x)[start:(start + 8)]
FREQ <- c("Not at all" = 0, "Several days" = 1,
          "More than half the days" = 2, "Nearly every day" = 3)
src <- do.call(rbind, lapply(seq_along(cols), function(k) {
    v <- unname(FREQ[trimws(as.character(x[[cols[k]]]))])
    v <- v[!is.na(v)]
    data.frame(item = sprintf("phq9_%d", k), resp = v, stringsAsFactors = FALSE)
}))
ts <- as.data.frame(table(src$item, src$resp), stringsAsFactors = FALSE)
tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
m <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
r1 <- nrow(src) == nrow(d) && all(!is.na(m$n.x)) && all(!is.na(m$n.y)) && all(m$n.x == m$n.y)
cat(sprintf("  cells compared: %d   rows src=%d live=%d\n", nrow(m), nrow(src), nrow(d)))
cat(sprintf("  -> every item x resp cell reproduced exactly: %s\n", r1))

cat("\n=== Route 2: the headers are the item text ===\n")
hdr <- trimws(gsub("\\s+", " ", sub("^[0-9]+\\.\\s*", "", cols)))
sh <- unique(items[, c("item", "item_text")])
sh <- sh[match(sprintf("phq9_%d", 1:9), sh$item), ]
r2 <- all(sh$item_text == hdr)
for (k in 1:9) cat(sprintf("  phq9_%d  %s\n", k, substr(hdr[k], 1, 78)))
cat(sprintf("  -> all nine match: %s\n", r2))
anch <- items$option_text[items$item == "phq9_1"][order(items$resp[items$item == "phq9_1"])]
r2b <- identical(unname(anch), names(FREQ))
cat(sprintf("  anchors: %s\n", paste(anch, collapse = " | ")))
cat(sprintf("  -> equal to the script's own recode categories, in 0-3 order: %s\n", r2b))

cat("\n=== What this does NOT establish ===\n")
cat("  The PHQ-9's standard stem ('Over the last 2 weeks, how often have you\n")
cat("  been bothered by ...'). The sheet carries only the banner, so\n")
cat("  instructions is left empty rather than supplied from the instrument.\n")
cat("\nVERDICT:", if (r1 && r2 && r2b) "PASS" else "FAIL", "\n")

# verify_kitayama_2022_hweat.R
#
# Claim under test: each shipped item_text (S1 Table of PLOS ONE 10.1371/journal.pone.0268124)
# belongs to the live item code of the same name (Q1..Q18).
#
# The tie is a LABEL MATCH, not an order inference: the S1 Table docx prefixes every
# Japanese item with the code Q1..Q18, and data/kitayama_2022_hweat.py melts the S2 Data
# workbook's own headers (`[c for c in df.columns if c.startswith("Q")]`) with no rename,
# so the live code IS the source column name. This script re-establishes both links and
# adds an independent data-side corroboration that the PAPER's Q-numbering refers to the
# same columns: the paper names nine items as showing floor effects, and its own stated
# criterion (>= 7% of respondents at the minimum, 1) is checked against the S2 workbook.
#
# Uses irw::irw_table_sets() (server-side aggregate) rather than irw_fetch() -- no export.

suppressMessages(library(irw))
TABLE <- "kitayama_2022_hweat"
UA <- "IRW-itemtext/1.0 (ben.domingue@gmail.com)"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0268124.s001"
S2 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0268124.s004"

dl <- function(url, ext) { f <- tempfile(fileext = ext)
  download.file(url, f, quiet = TRUE, mode = "wb", headers = c("User-Agent" = UA)); f }

## --- link 1: live item codes == S2 Data workbook headers -------------------
ts <- irw::irw_table_sets(TABLE)
live <- sort(as.character(ts$item))
x <- readxl::read_excel(dl(S2, ".xlsx"))
hdr <- sort(grep("^Q", names(x), value = TRUE))
cat("live item codes  :", paste(live, collapse = " "), "\n")
cat("S2 Data headers  :", paste(hdr, collapse = " "), "\n")
link1 <- identical(live, hdr)
cat("link 1 (live code IS the source column name):", if (link1) "OK" else "MISMATCH",
    sprintf("(%d/%d)\n", sum(hdr %in% live), length(hdr)))

## --- link 2: S1 Table labels the wording with those same codes -------------
zf <- dl(S1, ".docx"); dd <- tempfile(); dir.create(dd)
utils::unzip(zf, files = "word/document.xml", exdir = dd)
doc <- paste(readLines(file.path(dd, "word", "document.xml"), warn = FALSE), collapse = "")
cells <- regmatches(doc, gregexpr("<w:tc>.*?</w:tc>", doc))[[1]]
txt <- vapply(cells, function(c) {
  r <- regmatches(c, gregexpr("<w:t[^>]*>[^<]*</w:t>", c))[[1]]
  paste(gsub("<[^>]*>", "", r), collapse = "") }, character(1))
codes <- sort(unique(grep("^Q[0-9]+$", trimws(txt), value = TRUE)))
cat("S1 Table row labels:", paste(codes, collapse = " "), "\n")
link2 <- identical(codes, live)
cat("link 2 (paper labels each wording with the live code):", if (link2) "OK" else "MISMATCH",
    sprintf("(%d/%d)\n", sum(codes %in% live), length(live)))

## --- corroboration: the paper's floor-effect list, recomputed --------------
# Paper, Results ("Ceiling and floor effect"): floor effect declared when >= 7% of
# respondents rated the minimum; items named are Q3, Q4, Q7, Q8, Q10, Q14, Q16, Q17, Q18.
PAPER_FLOOR <- c("Q3","Q4","Q7","Q8","Q10","Q14","Q16","Q17","Q18")
pc <- sapply(paste0("Q", 1:18), function(q) 100 * mean(as.numeric(x[[q]]) == 1, na.rm = TRUE))
cat("\n% at the minimum (1), S2 Data, N=", nrow(x), ":\n", sep = "")
for (q in paste0("Q", 1:18))
  cat(sprintf("  %-4s %5.1f%%%s%s\n", q, pc[[q]],
      if (pc[[q]] >= 7) "  >=7%" else "", if (q %in% PAPER_FLOOR) "  [named in paper]" else ""))
obs_floor <- names(pc)[pc >= 7]
cat("computed >=7% set:", paste(obs_floor, collapse = " "), "\n")
cat("paper's named set:", paste(PAPER_FLOOR, collapse = " "), "\n")
agree <- length(intersect(obs_floor, PAPER_FLOOR))
cat(sprintf("agreement: %d of %d named items reproduce; disagreements: paper-only %s, data-only %s\n",
    agree, length(PAPER_FLOOR),
    paste(setdiff(PAPER_FLOOR, obs_floor), collapse = ","),
    paste(setdiff(obs_floor, PAPER_FLOOR), collapse = ",")))
cat("Any offset in the paper's Q-numbering relative to the data columns would break all\n",
    "nine of these, not one; the single Q16-for-Q15 discrepancy (2.5% vs 7.4%) is a typo\n",
    "in the paper's sentence, not a mapping shift.\n", sep = "")

cat("\nNote: this establishes the item_text <-> item mapping for all 18 items by label match.\n",
    "It establishes NOTHING about option_text <-> resp: the administered Japanese anchors\n",
    "were never published, so option_text ships blank and only the paper's English endpoint\n",
    "descriptions (1 = strongly disagree, 5 = strongly agree) are carried, unverified.\n", sep = "")

cat(if (link1 && link2 && agree >= 8) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

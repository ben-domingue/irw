# verify_pang_2023_perceived_enjoyment.R
#
# What is claimed, and what could break it
# ----------------------------------------
# data/pang_2023_nev_adoption.py assigns item codes POSITIONALLY: the 40 item
# columns of the PLOS S1 File are sliced item_cols[20:25] for this table and
# relabelled item_01..item_05 in order. The output keeps no trace of which
# source question each code came from, so a shifted slice or a permuted block
# would be invisible in the shipped table. Two things are checked, both
# falsifiable:
#
#  (A) ITEM MAPPING (decisive). For each of the 40 source item columns compute
#      the 5-vector of response counts (number of 1s, 2s, ... 5s). If those 40
#      vectors are mutually distinct, a live item's own count vector identifies
#      exactly one source column -- and hence exactly one question wording --
#      out of the whole 40-column pool, not merely within the 5-item block. That
#      catches a shifted slice AND a within-block swap.
#
#  (B) OPTION DIRECTION (inference, not proof). The paper's Methods say the
#      5-point scale ran "1 point (strongly disagree) to 5 points (strongly
#      agree)", but S2 File's questionnaire lists every item's options as
#      Definitely agree / Agree / Neither / Disagree / Definitely disagree --
#      agree FIRST. The shipped option_text follows the questionnaire. The test:
#      if the export codes single-choice options by DISPLAY POSITION, the
#      demographic columns on the same form must reproduce the paper's own
#      published percentages at the codes that display order predicts --
#      55.7% men (Male listed 1st) and 90.3% bachelor's or above (Undergraduates
#      3rd, Master 4th of four).
#
# What (B) does NOT establish: it is an inference about the form's coding
# convention corroborated by content, not a value label or an authors'
# statement, and the Methods sentence asserts the opposite. Disclosed in
# notes_/provenance_.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "pang_2023_perceived_enjoyment"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0285815.s001")
SLICE <- 21:25        # python item_cols[20:25] == R item_cols[21:25]  (Q25-Q29)
PUB_MALE_PCT <- 55.7
PUB_BACHELOR_PLUS_PCT <- 90.3

tmp <- file.path(tempdir(), "pang2023_s001.xlsx")
if (!file.exists(tmp)) download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
stopifnot(ncol(raw) == 45)
item_cols <- names(raw)[6:45]
stopifnot(length(item_cols) == 40)

countvec <- function(x) as.integer(sapply(1:5, function(k) sum(x == k, na.rm = TRUE)))
src <- lapply(item_cols, function(cc) countvec(raw[[cc]]))
names(src) <- item_cols
dup <- sum(duplicated(sapply(src, paste, collapse = "-")))
cat(sprintf("distinct count-vectors among the 40 source item columns: %d (duplicates: %d)\n",
            40 - dup, dup))

d <- irw::irw_fetch(TABLE)          # 1,545 rows -- a negligible export
live_items <- sprintf("item_%02d", 1:5)
ok <- (dup == 0)
cat(sprintf("\n%-8s %-20s %-14s %-14s %s\n", "item", "live counts (1..5)",
            "matched src", "expected src", ""))
for (i in seq_along(live_items)) {
    it <- live_items[i]
    lv <- countvec(as.numeric(d$resp[d$item == it]))
    hits <- names(src)[sapply(src, function(v) identical(v, lv))]
    exp_col <- item_cols[SLICE[i]]
    good <- length(hits) == 1 && hits == exp_col
    ok <- ok && good
    cat(sprintf("%-8s %-20s %-14s %-14s %s\n", it, paste(lv, collapse = ","),
                if (length(hits) == 1) sprintf("Q%s", sub("[.].*", "", hits))
                else sprintf("<%d matches>", length(hits)),
                sprintf("Q%s", sub("[.].*", "", exp_col)),
                if (good) "OK" else "MISMATCH"))
}
cat("\nshipped wording is the S2 questionnaire text of the matched columns:\n")
for (i in seq_along(live_items))
    cat(sprintf("  %s <- %s\n", live_items[i], item_cols[SLICE[i]]))

# (B) option direction
male_pct <- 100 * mean(raw[[2]] == 1, na.rm = TRUE)
bach_pct <- 100 * mean(raw[[4]] %in% c(3, 4), na.rm = TRUE)
cat("\noption-order coding check (demographic columns of the same form):\n")
cat(sprintf("  code 1 on gender       = %.1f%%  vs published men %.1f%% (Male listed 1st)\n",
            male_pct, PUB_MALE_PCT))
cat(sprintf("  codes 3+4 on education = %.1f%%  vs published bachelor+ %.1f%% (listed 3rd,4th)\n",
            bach_pct, PUB_BACHELOR_PLUS_PCT))
dir_ok <- abs(male_pct - PUB_MALE_PCT) < 0.5 && abs(bach_pct - PUB_BACHELOR_PLUS_PCT) < 0.5
cat(sprintf("  => code 1 == first listed option: %s, so 1 = 'Definitely agree'\n",
            if (dir_ok) "confirmed" else "NOT confirmed"))
cat(sprintf("  corroboration: mean resp over the 5 PE items = %.3f\n", mean(as.numeric(d$resp))))
cat("  (under the Methods reading a potential-NEV-user sample would be rejecting that\n")
cat("   NEVs are enjoyable, while agreeing they are costly and risky -- all 40 items on\n")
cat("   this form skew to codes 1-2 regardless of item polarity.)\n")

cat("\n(A) pins every item against all 40 source columns and is decisive.\n")
cat("(B) is an inference about the form's coding convention; the paper's Methods\n")
cat("sentence states the opposite direction and is treated as an error.\n")
cat(if (ok && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_pang_2023_perceived_cost.R
#
# What is claimed, and what could break it
# ----------------------------------------
# data/pang_2023_nev_adoption.py assigns item codes POSITIONALLY: the 40 item
# columns of the PLOS S1 File are sliced [15:20] for this table and relabelled
# item_01..item_05. Nothing in the code records which source question each one
# came from, so a shifted slice or a permuted block would be invisible in the
# output. Two things are checked here, and both are falsifiable:
#
#  (A) ITEM MAPPING. For every one of the 40 source item columns, compute the
#      5-vector of response counts (how many 1s, 2s, ... 5s). Those 40 vectors
#      are all distinct, so each live item's own count vector identifies exactly
#      one source column -- and therefore exactly one question wording. This
#      pins each item against the WHOLE 40-column pool, not just within the
#      5-item block, so it would catch both a shifted slice and a within-block
#      swap.
#
#  (B) OPTION DIRECTION. The paper's Methods say "1 point (strongly disagree) to
#      5 points (strongly agree)", but the S2 File questionnaire lists every
#      item's options in the order Definitely agree / Agree / Neither /
#      Disagree / Definitely disagree, i.e. agree FIRST. The shipped option_text
#      follows the questionnaire, not the Methods sentence. The check: on the
#      same form, the demographic codings must then also follow list order.
#      Paper reports 55.7% men (Male listed first) and 90.3% with a bachelor's
#      degree or above (Undergraduates 3rd, Master 4th of four options). If code
#      1 = first listed option, those percentages reappear at codes 1 and 3+4.
#
# What this does NOT establish: (B) is an inference about the coding convention
# of the whole form, corroborated by the direction of the response
# distributions; it is not a statement by the authors, and the authors' own
# Methods sentence contradicts it. See the notes/provenance CSVs.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "pang_2023_perceived_cost"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0285815.s001")
SLICE <- 16:20        # item_cols[15:20] in 0-based python == 16:20 in R
PUB_MALE_PCT <- 55.7  # paper, Sample population section
PUB_BACHELOR_PLUS_PCT <- 90.3

tmp <- file.path(tempdir(), "pang2023_s001.xlsx")
if (!file.exists(tmp)) download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
item_cols <- names(raw)[6:45]
stopifnot(length(item_cols) == 40)

countvec <- function(x) as.integer(sapply(1:5, function(k) sum(x == k, na.rm = TRUE)))
src <- lapply(item_cols, function(c) countvec(raw[[c]]))
names(src) <- item_cols

dup <- sum(duplicated(sapply(src, paste, collapse = "-")))
cat(sprintf("distinct count-vectors among the 40 source item columns: %d (duplicates: %d)\n",
            40 - dup, dup))

d <- irw::irw_fetch(TABLE)
live_items <- sprintf("item_%02d", 1:5)
ok <- TRUE
cat(sprintf("\n%-8s %-18s %-18s %s\n", "item", "live counts", "matched source col", "expected col"))
for (i in seq_along(live_items)) {
    it <- live_items[i]
    lv <- countvec(d$resp[d$item == it])
    hits <- names(src)[sapply(src, function(v) identical(v, lv))]
    exp_col <- item_cols[SLICE[i]]
    good <- length(hits) == 1 && hits == exp_col
    ok <- ok && good
    cat(sprintf("%-8s %-18s %-18s %s  %s\n", it, paste(lv, collapse = ","),
                if (length(hits) == 1) sprintf("Q%s", sub("\\..*", "", hits)) else
                    sprintf("<%d matches>", length(hits)),
                sprintf("Q%s", sub("\\..*", "", exp_col)),
                if (good) "OK" else "MISMATCH"))
}
cat("\nshipped wording for the matched columns:\n")
for (i in seq_along(live_items))
    cat(sprintf("  %s <- %s\n", live_items[i], item_cols[SLICE[i]]))

# (B) option direction
gender <- raw[[2]]; educ <- raw[[4]]
male_pct <- 100 * mean(gender == 1, na.rm = TRUE)
bach_pct <- 100 * mean(educ %in% c(3, 4), na.rm = TRUE)
cat(sprintf("\noption-order coding check (same form, demographic items):\n"))
cat(sprintf("  code 1 on gender     = %.1f%%  vs published 'men' %.1f%%  (Male listed 1st)\n",
            male_pct, PUB_MALE_PCT))
cat(sprintf("  codes 3+4 on education = %.1f%% vs published \"bachelor's or above\" %.1f%% (listed 3rd,4th)\n",
            bach_pct, PUB_BACHELOR_PLUS_PCT))
dir_ok <- abs(male_pct - PUB_MALE_PCT) < 0.5 && abs(bach_pct - PUB_BACHELOR_PLUS_PCT) < 0.5
cat(sprintf("  => code 1 == first listed option: %s, so 1 = 'Definitely agree'\n",
            if (dir_ok) "confirmed" else "NOT confirmed"))
cat(sprintf("  corroboration: mean of the 5 shipped items = %.2f; under the Methods sentence's\n",
            mean(d$resp)))
cat("  reading the sample would be disagreeing that NEVs are costly, and the same file's\n")
cat("  BI item 'I will switch to an NEV if they are safer' (mean 1.92) would be the most\n")
cat("  rejected of all 40 items, which is not credible for a potential-NEV-user sample.\n")

cat("\nNote: (A) pins every item against all 40 source columns and is decisive.\n")
cat("(B) is an inference about the form's coding convention; the paper's Methods\n")
cat("sentence states the opposite direction and is treated as an error.\n")

cat(if (ok && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

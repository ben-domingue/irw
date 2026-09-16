# verify_vaporova_2020_imitation.R -- Step 5b mapping check.
#
# CLAIM: the three live item codes name the three mitten target actions the way
# the shipped item_text says they do, i.e.
#   item_pulling_off      <- S1 Data column 13 "Imitation_pulling mitten off"
#   item_shaking          <- S1 Data column 14 "Imitation_shaking the mitten"
#   item_putting_back_on  <- S1 Data column 15 "Imitation_putting mitten back on"
# data/vaporova_2020_imitation.py assigns these codes POSITIONALLY (block[[0,3,13,14,15]]
# then df.columns = [...]), so the code keeps no trace of the source header and the
# assignment has to be checked against the source rather than assumed.
#
# TEST: re-derive the three columns straight from the PLOS S1 Data workbook
# (the Infants/Children block, analyzable-imitation flag == 1) and compare per-item n and endorsement
# count/mean against the live IRW table. The three actions have distinct endorsement
# rates (45/82, 21/82, 27/82), so any permutation of the three codes breaks the match.
# A swap of shaking and putting-back-on -- the only pair a reader might not notice,
# because the script's column list and its name list are in DIFFERENT orders -- shows
# up as 0.256 against 0.329.
#
# This also settles the option_text<->resp axis: the header cells carry the value
# labels "0 = not imitated / 1 = imitated", and the count of 1s per column equals the
# count of resp==1 per live item, so the shipped anchors cannot be flipped.

suppressMessages(library(irw))

TABLE <- "vaporova_2020_imitation"
SRC <- paste0("https://journals.plos.org/plosone/article/file?",
              "type=supplementary&id=10.1371/journal.pone.0235595.s001")

# Source header text at each position (PLOS S1 Data, sheet prosociality_data, row 4).
HDR <- c(item_pulling_off     = "Imitation_pulling mitten off",
         item_shaking         = "Imitation_shaking the mitten",
         item_putting_back_on = "Imitation_putting mitten back on")
COL <- c(item_pulling_off = 14L, item_shaking = 15L, item_putting_back_on = 16L)  # 1-based

# Fallback values measured from that workbook on 2026-09-15, so the script still
# reports something reviewable if PLOS is unreachable.
SRC_N   <- c(item_pulling_off = 82, item_shaking = 82, item_putting_back_on = 82)
SRC_SUM <- c(item_pulling_off = 45, item_shaking = 21, item_putting_back_on = 27)

tmp <- tempfile(fileext = ".xlsx")
src_ok <- FALSE
try({
    utils::download.file(SRC, tmp, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = "Mozilla/5.0"))
    if (requireNamespace("readxl", quietly = TRUE)) {
        raw <- readxl::read_excel(tmp, sheet = "prosociality_data",
                                  col_names = FALSE, .name_repair = "minimal")
        hdr_row <- as.character(unlist(raw[3, ]))
        blk <- raw[4:98, ]
        keep <- suppressWarnings(as.numeric(unlist(blk[, 4]))) == 1   # analyzable imitation
        keep[is.na(keep)] <- FALSE
        blk <- blk[keep, ]
        for (nm in names(COL)) {
            v <- suppressWarnings(as.numeric(unlist(blk[, COL[[nm]]])))
            v <- v[!is.na(v)]
            SRC_N[nm]   <- length(v)
            SRC_SUM[nm] <- sum(v)
            cat(sprintf("header col %2d: %s\n", COL[[nm]],
                        sub("\n.*", "", hdr_row[COL[[nm]]])))
        }
        src_ok <- TRUE
    }
}, silent = TRUE)
cat(if (src_ok) "source workbook: re-fetched and re-read\n"
    else "source workbook: UNREACHABLE -- using values measured 2026-09-15\n", "\n", sep = "")

d <- irw::irw_fetch(TABLE)
cat(sprintf("%-22s %-34s %6s %6s %6s %6s %8s %8s\n",
            "item", "source header", "src_n", "live_n", "src_1", "live_1",
            "src_mean", "live_mean"))
ok <- TRUE
for (nm in names(COL)) {
    v <- d$resp[d$item == nm]
    live_n <- length(v); live_1 <- sum(v == 1)
    cat(sprintf("%-22s %-34s %6d %6d %6d %6d %8.4f %8.4f\n",
                nm, HDR[[nm]], SRC_N[[nm]], live_n, SRC_SUM[[nm]], live_1,
                SRC_SUM[[nm]] / SRC_N[[nm]], mean(v)))
    if (live_n != SRC_N[[nm]] || live_1 != SRC_SUM[[nm]]) ok <- FALSE
}

# The three rates must also be mutually distinct, or matching them proves nothing.
rates <- SRC_SUM / SRC_N
cat(sprintf("\nsource endorsement rates: %s\n",
            paste(sprintf("%s=%.4f", names(rates), rates), collapse = "  ")))
cat(sprintf("smallest gap between any two: %.4f (must be > 0 for the match to identify)\n",
            min(diff(sort(rates)))))
if (min(diff(sort(rates))) <= 0) ok <- FALSE

cat("Note: this pins each item code to a source COLUMN, and with it the action wording\n",
    "and the 0/1 anchors that column's header defines. It does not verify the wording of\n",
    "the instructions line, which is the paper's English rendering of a German utterance.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

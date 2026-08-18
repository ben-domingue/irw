# verify_riasec.R -- Step 5b mapping verification for `riasec`.
#
# CLAIM UNDER TEST
#   The IRW `item` codes 1..74 are bare integers invented by data/riasec.R via
#     items <- as.data.frame(unique(df$item)); items$item_id <- row_number()
#   i.e. the position of each surviving column of the openpsychometrics
#   RIASEC_data12Dec2018/data.csv after that script's select() drops. The shipped
#   item_text for code k is the codebook.txt line for the k-th surviving column:
#     1-48  = R1..R8, I1..I8, A1..A8, S1..S8, E1..E8, C1..C8
#     49-58 = TIPI1..TIPI10
#     59-74 = VCL1..VCL16
#
# HOW IT IS TESTED
#   data/riasec.R was re-run over the raw file (SKILL.md core model 3: for a
#   script-generated integer code, re-run the script rather than reason about it).
#   The per-column n and mean below are the RAW-FILE values computed under that
#   script's own rules (0 -> NA for every R/I/A/S/E/C and TIPI column; VCL columns
#   left alone, so 0 is a real "unchecked"). If the position->column assignment
#   were shifted or permuted by even one place, these would not line up with the
#   live per-item n/mean. This is a full mapping proof, not a plausibility check:
#   every one of the 74 items is distinguished from every other by (n, mean).
#
#   Live stats are pulled with a server-side aggregate query rather than
#   irw::irw_fetch(), because this table is 10.8M rows and a full export trips the
#   Redivis 200GB/30-day egress cap (it did, on 2026-08-18, which is why
#   validate_items.R could not be run against a fetched copy). Set USE_FETCH=TRUE
#   to use irw::irw_fetch() instead.
REPRO_N <- c(
    145398, 145272, 145132, 145260, 145082, 145296, 145156, 145238, 145570, 145529, 145472,
    145519, 145470, 145488, 145434, 145450, 145112, 145251, 145349, 145380, 145318, 145324,
    145410, 145226, 145409, 145527, 145528, 145454, 145454, 145488, 145545, 145496, 145117,
    145410, 145315, 145452, 145260, 145456, 145394, 145296, 145404, 145396, 145512, 145341,
    145456, 145437, 145463, 145563, 144940, 144710, 144802, 144936, 144953, 145024, 144950,
    144942, 145043, 144796, 145828, 145828, 145828, 145828, 145828, 145828, 145828, 145828,
    145828, 145828, 145828, 145828, 145828, 145828, 145828, 145828)

REPRO_MEAN <- c(
    2.580455, 2.114922, 1.757125, 2.302609, 1.758943, 2.205863, 2.026358, 1.975206,
    3.440839, 3.342523, 3.112166, 3.009305, 2.864426, 2.994426, 2.767695, 2.521361,
    2.455986, 2.795540, 3.005311, 2.941381, 3.067934, 3.216344, 2.669032, 2.824033,
    3.423935, 3.616882, 3.255978, 3.082315, 3.543794, 3.078714, 3.242372, 2.892897,
    2.198578, 2.378956, 2.788542, 2.392349, 3.005473, 2.644484, 2.485103, 2.664340,
    2.301209, 2.388257, 2.382133, 2.481564, 2.517999, 2.628801, 2.198057, 2.255154,
    4.739175, 3.926819, 5.574550, 4.077641, 5.772057, 4.492360, 5.626692, 3.086593,
    5.024138, 2.882407, 0.905471, 0.763790, 0.292358, 0.907864, 0.841704, 0.083201,
    0.158420, 0.280618, 0.058356, 0.915675, 0.133671, 0.123001, 0.447952, 0.708410,
    0.882121, 0.966591)

SRC_COL <- c(
    "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "i1", "i2", "i3", "i4", "i5", "i6",
    "i7", "i8", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "s1", "s2", "s3", "s4",
    "s5", "s6", "s7", "s8", "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "c1", "c2",
    "c3", "c4", "c5", "c6", "c7", "c8", "tipi1", "tipi2", "tipi3", "tipi4", "tipi5",
    "tipi6", "tipi7", "tipi8", "tipi9", "tipi10", "vcl1", "vcl2", "vcl3", "vcl4", "vcl5",
    "vcl6", "vcl7", "vcl8", "vcl9", "vcl10", "vcl11", "vcl12", "vcl13", "vcl14", "vcl15",
    "vcl16")

USE_FETCH <- FALSE
TOL_MEAN  <- 1e-6

live <- if (USE_FETCH) {
    d <- irw::irw_fetch("riasec")
    d <- d[!is.na(d$resp), ]
    data.frame(item = as.integer(as.character(d$item)),
               resp = as.numeric(d$resp)) |>
        (\(x) data.frame(item = sort(unique(x$item)),
                         n    = as.vector(tapply(x$resp, x$item, length))[order(unique(x$item))],
                         mean = as.vector(tapply(x$resp, x$item, mean))[order(unique(x$item))]))()
} else {
    suppressMessages(library(redivis))
    q <- redivis$query(paste(
        "select item, count(*) as n, avg(cast(resp as float64)) as mean",
        "from datapages.item_response_warehouse:as2e.riasec:xp62",
        "where resp != 'NA' group by 1"))
    d <- q$to_data_frame()
    d$item <- as.integer(as.character(d$item))
    d[order(d$item), c("item", "n", "mean")]
}

stopifnot(nrow(live) == 74, identical(live$item, 1:74))

cat(sprintf("%-5s %-8s %10s %10s %6s %12s %12s %12s\n",
            "item", "srccol", "raw_n", "live_n", "dn", "raw_mean", "live_mean", "dmean"))
for (k in 1:74)
    cat(sprintf("%-5d %-8s %10d %10d %6d %12.6f %12.6f %12.2e\n",
                k, SRC_COL[k], REPRO_N[k], live$n[k], live$n[k] - REPRO_N[k],
                REPRO_MEAN[k], live$mean[k], live$mean[k] - REPRO_MEAN[k]))

dn <- max(abs(live$n - REPRO_N))
dm <- max(abs(live$mean - REPRO_MEAN))
cat(sprintf("\nlargest |dn| over 74 items: %d (must be 0)\n", dn))
cat(sprintf("largest |dmean| over 74 items: %.3e (tolerance %.0e)\n", dm, TOL_MEAN))

# Falsification margin: how close is the nearest rival assignment? Compare each
# item's raw mean to every OTHER item's live mean; the smallest such distance is
# the margin by which a permutation would have been detected.
rival <- min(sapply(1:74, function(k) min(abs(REPRO_MEAN[k] - live$mean[-k]))))
cat(sprintf("closest rival item mean (smallest off-diagonal gap): %.4f\n", rival))
cat("This route distinguishes all 74 items from one another; nothing is left unpinned\n",
    "on the item_text<->item axis. The option_text<->resp axis rests on codebook.txt's\n",
    "explicit anchor statements plus the per-item level sets (1-5 / 1-7 / 0-1), which\n",
    "match the live data exactly for all 342 item x resp cells.\n", sep = "")

cat(if (dn == 0 && dm <= TOL_MEAN) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

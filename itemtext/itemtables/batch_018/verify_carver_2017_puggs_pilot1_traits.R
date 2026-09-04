# verify_carver_2017_puggs_pilot1_traits.R
#
# CLAIM UNDER TEST -- that IRW item code TTk carries the trait named at row k of
# the first pilot's Table of Traits, i.e.
#   TT1 = Coronary heart disease ... TT20 = Blood group (ABO).
#
# The chain has two links and this script exercises both:
#   (a) code -> source column. data/carver_2017_puggs_items.py melts pilot 1's
#       raw file (S5 Table) on its own headers TT1..TT20, so the IRW code IS the
#       source column name. Falsifiable prediction: re-running that filter over
#       the raw workbook must reproduce the LIVE per-item n and resp range for
#       all 20 items. A permuted column assignment breaks it -- the fingerprints
#       are sharp (TT10 n=156 vs TT2 n=204; TT20 spans 4-5 only; TT2 starts at 2;
#       TT12 and TT18 top out at 4).
#   (b) source column -> trait. The pilot-1 Code Book (S4 Table) prints the trait
#       inside the code itself: "TT1 (coronary heart disease)" ... "TT20 (Blood
#       group ABO)", and the questionnaire (S3 Table) lists the same 20 traits in
#       the same order. That is a label match, not an order inference. It is
#       corroborated here by content: the observed per-trait mean genetic
#       attribution is checked against the Code Book's own per-trait "Expected
#       answer" (Spearman), which no permutation of the labels would preserve.
#
# WHAT THIS DOES NOT ESTABLISH: link (a) alone cannot separate the pairs that
# share both n and range (e.g. TT2/TT7 at n=204; TT11/TT19 at n=202). Those are
# separated by link (b)'s label match and by the mean/expected-answer agreement,
# not by the counts.
#
# Live data comes from irw::irw_table_sets(per_item = TRUE) -- server-side
# aggregates, no table export.

suppressMessages({library(irw); library(readxl)})

TABLE <- "carver_2017_puggs_pilot1_traits"
S5 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0169808.s005")

ITEMS <- paste0("TT", 1:20)
TRAITS <- c("Coronary heart disease","Height","Bipolar disorder","Diabetes","Colour blindness",
            "Schizophrenia","Alcoholism","Breast cancer","Interest in fashion",
            "Haemofilia blood disorder","Addictive gambling behaviour","Political beliefs",
            "Intelligence in adults","Major depression","Tourette syndrome (tics disorder)",
            "Attention Deficit Hyperactivity Disorder (ADHD)","Asthma","Violent behaviour",
            "Religious beliefs","Blood group (ABO)")
# S4 Table (pilot-1 Code Book), "Expected answer" column, in TT1..TT20 order.
EXPECTED <- c(3,4,4,2,5,4,3,2,1,5,2,1,4,3,4,4,4,2,1,5)

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(S5, tmp, quiet = TRUE, mode = "wb")
raw <- readxl::read_excel(tmp, sheet = "Sheet1")

live <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)$per_item
live <- as.data.frame(live)

cat(sprintf("%-5s %-38s %6s %6s %9s %9s %6s %4s\n",
            "item", "trait (S3/S4 Table)", "n_raw", "n_live", "rng_raw", "rng_live", "mean", "exp"))
ok <- TRUE; obs_mean <- numeric(20)
for (k in seq_along(ITEMS)) {
    v <- suppressWarnings(as.numeric(raw[[ITEMS[k]]]))
    v <- v[!is.na(v) & v != 6 & v != 99 & v >= 1 & v <= 5]   # script's own filter
    lr <- live[live$item == ITEMS[k], ]
    obs_mean[k] <- mean(v)
    hit <- length(v) == lr$n && min(v) == lr$resp_min && max(v) == lr$resp_max
    ok <- ok && hit
    cat(sprintf("%-5s %-38s %6d %6d %9s %9s %6.2f %4d%s\n", ITEMS[k], TRAITS[k],
                length(v), lr$n, sprintf("%d-%d", min(v), max(v)),
                sprintf("%d-%d", lr$resp_min, lr$resp_max), obs_mean[k], EXPECTED[k],
                if (hit) "" else "  <- MISMATCH"))
}

rho <- suppressWarnings(cor(obs_mean, EXPECTED, method = "spearman"))
cat(sprintf("\n(a) per-item n and resp range reproduce live for all 20 items: %s\n", ok))
cat(sprintf("(b) Spearman(observed mean, Code Book expected answer) = %.3f over 20 traits\n", rho))
cat("    extremes behave: Blood group (ABO) ", sprintf("%.2f", obs_mean[20]),
    " / Colour blindness ", sprintf("%.2f", obs_mean[5]),
    " at the genetic end; Political beliefs ", sprintf("%.2f", obs_mean[12]),
    " / Religious beliefs ", sprintf("%.2f", obs_mean[19]),
    " at the environmental end.\n", sep = "")
cat("Note: (a) cannot separate items sharing both n and range (TT2/TT7, TT11/TT19);\n",
    "the Code Book's explicit \"TTk (trait)\" labels and (b) are what do.\n", sep = "")

cat(if (ok && rho >= 0.6) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

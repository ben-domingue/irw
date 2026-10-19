# Step 5b for kembara_2026_civic_agency (#3077, 2026-10-19a batch).
#
# THE CLAIM. The item text comes from sheet "A6. Survey Instrument" of the
# deposit's own workbook (figshare 32414913), which prints Code / Dimension /
# Item (Indonesian) / Item (English) with codes Q1-Q6. mapping_basis is
# paper_explicit, not data_labels: the stem is stated for each code in a
# codebook sheet rather than carried as a column label, so the tie between
# code and stem rests on the deposit using Q1-Q6 consistently across its
# sheets. That is what this script falsifies.
#
# THE ROUTE (route 1, per-item descriptive statistics). Sheet
# "A2. Descriptive Statistics" publishes, per code, n / M / SD / Min / Max and
# the complete 1-5 frequency distribution -- and it labels each code with the
# same six dimensions A6 does, in Indonesian where A6 gives English. If the
# shipped response table's Q3 column were not the deposit's Q3, its mean, SD
# and frequency vector would not reproduce A2's published row for Q3.
#
# The means alone would NOT be enough: Q1 (3.5536) and Q2 (3.5714) are 0.018
# apart, inside the ~0.02 band item_stats.R flags as a tie. The frequency
# vectors separate all six outright, so this script compares those as well and
# requires them to match exactly.
#
# WHAT THIS DOES NOT ESTABLISH. It confirms code <-> response column <->
# published statistics, and A2 and A6 agree on which dimension each code is.
# It cannot confirm that the authors assigned the right stem to the right
# dimension in the first place -- no statistical route can, and the stems are
# this study's own.
#
# Offline-tolerant: the published values are hard-coded (they came from the
# deposit and will not change), and the response data is read from the staged
# CSV when the table is not live yet.

TABLE <- "kembara_2026_civic_agency"
STAGED <- file.path("automated_finding", "irw_output", paste0(TABLE, ".csv"))

# Sheet "A2. Descriptive Statistics", Table A2.1 and A2.2 (figshare 32414913).
PUBLISHED <- data.frame(
    item = c("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"),
    n    = c(392, 392, 392, 392, 392, 392),
    M    = c(3.5536, 3.5714, 3.5000, 3.2653, 3.8138, 4.3393),
    SD   = c(1.0522, 0.9962, 0.7467, 0.7610, 0.8751, 0.7221),
    min  = c(1, 1, 1, 1, 1, 2),
    max  = c(5, 5, 5, 5, 5, 5),
    stringsAsFactors = FALSE
)
# Table A2.2, frequency of each score 1..5, per item.
FREQ <- rbind(
    Q1 = c(17, 35, 136, 122, 82),
    Q2 = c(9, 45, 125, 139, 74),
    Q3 = c(1, 20, 190, 144, 37),
    Q4 = c(1, 53, 198, 121, 19),
    Q5 = c(3, 23, 106, 172, 88),
    Q6 = c(0, 2, 52, 149, 189)
)
TOL_M <- 0.005
TOL_SD <- 0.005

d <- if (file.exists(STAGED)) {
    cat("response data: staged CSV", STAGED, "\n\n")
    read.csv(STAGED, stringsAsFactors = FALSE)
} else {
    suppressMessages(library(irw))
    cat("response data: live irw_fetch\n\n")
    irw::irw_fetch(TABLE)
}

cat(sprintf("%-5s %6s %6s %9s %9s %8s %8s %8s\n",
            "item", "n_pub", "n_obs", "M_pub", "M_obs", "dM",
            "SD_pub", "SD_obs"))
worst_m <- 0
worst_sd <- 0
for (i in seq_len(nrow(PUBLISHED))) {
    it <- PUBLISHED$item[i]
    r <- d$resp[d$item == it]
    dm <- mean(r) - PUBLISHED$M[i]
    dsd <- sd(r) - PUBLISHED$SD[i]
    worst_m <- max(worst_m, abs(dm))
    worst_sd <- max(worst_sd, abs(dsd))
    cat(sprintf("%-5s %6d %6d %9.4f %9.4f %8.4f %8.4f %8.4f\n",
                it, PUBLISHED$n[i], length(r), PUBLISHED$M[i], mean(r), dm,
                PUBLISHED$SD[i], sd(r)))
}

cat("\nfrequency distributions (published vs observed, scores 1-5)\n")
freq_ok <- TRUE
for (it in PUBLISHED$item) {
    r <- factor(d$resp[d$item == it], levels = 1:5)
    obs <- as.integer(table(r))
    ok <- identical(obs, as.integer(FREQ[it, ]))
    freq_ok <- freq_ok && ok
    cat(sprintf("%-5s pub %-22s obs %-22s %s\n", it,
                paste(FREQ[it, ], collapse = ","),
                paste(obs, collapse = ","),
                if (ok) "match" else "MISMATCH"))
}

range_ok <- all(vapply(PUBLISHED$item, function(it) {
    r <- d$resp[d$item == it]
    min(r) == PUBLISHED$min[PUBLISHED$item == it] &&
        max(r) == PUBLISHED$max[PUBLISHED$item == it]
}, logical(1)))

cat(sprintf("\nlargest deviation: mean %.4f (tol %.3f), SD %.4f (tol %.3f)\n",
            worst_m, TOL_M, worst_sd, TOL_SD))
cat(sprintf("observed min/max match the published per-item range: %s\n",
            range_ok))
cat("Note: this separates all six items (Q1 and Q2 differ by 0.018 in mean, so\n",
    "the frequency vectors are what distinguish them). It confirms the code-to-\n",
    "column tie and that A2 and A6 agree on each code's dimension; it cannot\n",
    "confirm the authors' own stem-to-dimension assignment.\n", sep = "")

pass <- freq_ok && range_ok && worst_m <= TOL_M && worst_sd <= TOL_SD
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

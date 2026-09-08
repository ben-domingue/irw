# verify_jutte_2024_loneliness.R
#
# CLAIM BEING TESTED (Step 5b). Two things, neither of them plumbing:
#
#  (a) The live item code Loneliness_Ix IS the source column Loneliness_Ix_w{1,2}
#      of the study's SPSS deposit (PLOS S3 File), for each x and each wave.
#      data/jutte_2024_loneliness_battery.py strips the _w1/_w2 suffix -- a
#      number-preserving rename -- and the paper ties the numbers to words
#      ("Item 1:..alone?, Item 2:..lonely?, Item3:..left out?"). If the shipped
#      item_text for two of the three items were swapped, the code->column tie
#      is what would have to be wrong, so it is tested cell-for-cell: every
#      item x wave x resp-level frequency in the live table must equal the
#      frequency in the corresponding .sav column. The three items' response
#      distributions differ, so this discriminates them.
#
#  (b) The shipped anchor direction (resp 0 = "never" ... resp 6 = "very
#      frequently"). The paper reports the 3-item loneliness composite as
#      mean 2.69 pre-lockdown and 2.56 during lockdown on its 1-7 scale; the
#      live table stores 0-6. Ascending direction predicts live_mean + 1 hits
#      those values; the reversed reading predicts 8 - live_mean (i.e. ~5.3).
#
# Not established here: nothing about the German wording respondents actually
# read (the deposit publishes none) -- see provenance.

suppressMessages(library(irw))

TABLE <- "jutte_2024_loneliness"
SAV   <- file.path("..", "..", ".cache", TABLE, "s003.sav")
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0296423.s003")

if (!file.exists(SAV)) {
    dir.create(dirname(SAV), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(SI_URL, SAV, mode = "wb", quiet = TRUE)
}
src <- haven::read_sav(SAV)

d <- irw::irw_fetch(TABLE)
d$wave <- as.integer(d$wave)

ok <- TRUE

cat("(a) live item x wave x resp counts vs the S3 File's own columns\n")
cat(sprintf("%-16s %5s %26s %26s  %s\n", "item", "wave",
            "live counts (resp 0..6)", "sav counts (resp 0..6)", "match"))
for (x in 1:3) {
    it <- sprintf("Loneliness_I%d", x)
    for (w in 1:2) {
        live <- as.integer(table(factor(d$resp[d$item == it & d$wave == w], levels = 0:6)))
        col  <- sprintf("Loneliness_I%d_w%d", x, w)
        sv   <- as.integer(table(factor(as.numeric(src[[col]]), levels = 0:6)))
        same <- identical(live, sv)
        ok <- ok && same
        cat(sprintf("%-16s %5d %26s %26s  %s\n", it, w,
                    paste(live, collapse = ","), paste(sv, collapse = ","),
                    if (same) "yes" else "NO"))
    }
}

cat("\n(b) anchor direction: composite mean vs the paper's Table 3\n")
PUB <- c(`1` = 2.69, `2` = 2.56)
for (w in 1:2) {
    sub <- d[d$wave == w, ]
    per_id <- tapply(sub$resp, sub$id, mean)
    asc <- mean(per_id) + 1
    rev <- 8 - mean(per_id)
    hit <- abs(asc - PUB[[as.character(w)]]) <= 0.01
    ok <- ok && hit
    cat(sprintf("wave %d: published %.2f | ascending (0=never) %.3f | reversed reading %.3f -> %s\n",
                w, PUB[[as.character(w)]], asc, rev,
                if (hit) "ascending" else "MISMATCH"))
}

cat("\nNote: this pins each live item code to its source column and pins the\n",
    "0=never..6=very frequently direction. The words themselves come from the\n",
    "paper's own item numbering, which is a label match, not a statistic.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

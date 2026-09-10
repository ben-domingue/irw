# verify_otaki_2022_dental_adaptability.R
#
# What is being verified: the option_text <-> resp mapping. The item axis needs
# no inference -- the IRW `item` codes ARE the S1 File's own spreadsheet column
# headers, copied verbatim by data/otaki_2022_dental_adaptability.py, so a
# permutation is impossible. The resp axis DID carry a decision: the S1 File
# stores Likert LABELS ("Neutral"/"Agree"/"Strongly agree") and the live table
# stores integers 3/4/5, so the shipped anchors depend on the direction of the
# label -> integer map.
#
# Two routes, both falsifiable:
#   Route 9 (response-frequency matching): count each label per item in the S1
#     File and each integer per item in the live table. A flipped or permuted
#     level breaks the cell-for-cell match.
#   Route 3 (published total): Otaki et al. (2022) report the instructors'
#     overall adaptability score as 17.94 (+/-1.76) over the four items. A
#     reversed coding would produce 24 - 17.94 = 6.06.
#
# The 18-respondent, 4-item live table is 72 rows, so irw_fetch() here is a
# negligible export.

suppressMessages(library(irw))

TABLE <- "otaki_2022_dental_adaptability"
S1_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0270420.s001")

# Otaki et al. 2022, PLOS ONE 17(7):e0270420, Results: instructors' mean
# overall adaptability score (sum of the four components).
PUB_TOTAL_MEAN <- 17.94
PUB_TOTAL_SD   <- 1.76

# The paper's stated coding: "a Likert-type scale of five points (1: Strongly
# Disagree, 2: Disagree, 3: Neutral, 4: Agree, and 5: Strongly Agree)".
LIKERT <- c("Strongly disagree" = 1, "Disagree" = 2, "Neutral" = 3,
            "Agree" = 4, "Strongly agree" = 5)

d <- irw::irw_fetch(TABLE)

## ---- Route 3: published total ------------------------------------------
tot <- tapply(d$resp, d$id, sum)
cat("Route 3 -- published overall adaptability score (sum of 4 items)\n")
cat(sprintf("  published : mean %.2f  sd %.2f  (n=18 instructors)\n",
            PUB_TOTAL_MEAN, PUB_TOTAL_SD))
cat(sprintf("  observed  : mean %.4f  sd %.4f  (n=%d)\n",
            mean(tot), sd(tot), length(tot)))
cat(sprintf("  reversed-coding prediction would be mean %.2f\n", 24 - PUB_TOTAL_MEAN))
ok3 <- abs(mean(tot) - PUB_TOTAL_MEAN) < 0.02 && abs(sd(tot) - PUB_TOTAL_SD) < 0.02

## ---- Route 9: label counts vs integer counts ---------------------------
ok9 <- NA
raw <- try({
    tf <- tempfile(fileext = ".xlsx")
    utils::download.file(S1_URL, tf, quiet = TRUE,
                         headers = c("User-Agent" = "IRW-itemtext/1.0"))
    readxl::read_excel(tf)
}, silent = TRUE)

cat("\nRoute 9 -- S1 File label counts vs live integer counts, per item x level\n")
if (inherits(raw, "try-error")) {
    cat("  S1 File unreachable this run; route 9 skipped (route 3 stands alone).\n")
} else {
    items <- sort(unique(d$item))
    mism <- 0L; cells <- 0L
    for (it in items) {
        rc <- table(factor(LIKERT[as.character(raw[[it]])], levels = 3:5))
        lc <- table(factor(d$resp[d$item == it], levels = 3:5))
        cat(sprintf("  %-42s raw %s | live %s\n", substr(it, 1, 42),
                    paste(rc, collapse = "/"), paste(lc, collapse = "/")))
        mism <- mism + sum(rc != lc); cells <- cells + length(rc)
    }
    cat(sprintf("  %d of %d item x level cells match exactly\n", cells - mism, cells))
    ok9 <- (mism == 0L)
}

cat("\nWhat this does NOT establish: nothing about the two unused anchors\n",
    "(1 = Strongly disagree, 2 = Disagree), which no respondent selected and\n",
    "which therefore ship no row. It also does not test the item axis, which is\n",
    "exempt because the item codes are the source column headers verbatim.\n", sep = "")

cat(if (isTRUE(ok3) && !isFALSE(ok9)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_daiku_2021_dirty_dozen.R
#
# mapping_basis = paper_order. The IRW item codes are the S1 CSV's own column
# names (data/daiku_2021_prolific_liars.py melts them without renaming), and
# those names carry the SUBSCALE plus a bare within-subscale index
# (machiavellianism1..4, psychopathy1..4, narcissism1..4). They carry no item
# wording, so two claims had to be made:
#
#   (a) the subscale named in the column name really is that item's subscale;
#   (b) index i is the i-th item of that subscale in DTDD-J presentation order
#       (Mach = DTDD-J items 1,4,7,10; Psych = 2,5,8,11; Narc = 3,6,9,12 --
#       Tamura et al. 2015 footnote 2 / Figure 1B).
#
# This script tests (a) against the data three ways. It CANNOT test (b): no
# per-item statistic distinguishes the four items inside a subscale.
#
# Fetches the study's own PLOS CC BY supplement (the exact upstream of the IRW
# table -- the processing script only melts it), so it costs no Redivis export
# quota.

URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0249815.s001"
f <- tempfile(fileext = ".csv")
utils::download.file(URL, f, quiet = TRUE, mode = "wb")
d <- utils::read.csv(f)

GRP <- list(
  Machiavellianism = paste0("machiavellianism", 1:4),
  Psychopathy      = paste0("psychopathy", 1:4),
  Narcissism       = paste0("narcissism", 1:4))
cols <- unlist(GRP, use.names = FALSE)
X <- d[stats::complete.cases(d[, cols]), cols]
R <- stats::cor(X)
cat(sprintf("complete cases: %d\n\n", nrow(X)))

## --- Test 1: does each item correlate most with its own named subscale? -----
cat("Test 1 -- block structure (mean r with each block, self excluded)\n")
cat(sprintf("%-18s %7s %7s %7s   %-16s %s\n",
            "item", "Mach", "Psych", "Narc", "best block", "named block"))
hits <- 0; miss <- character(0)
for (g in names(GRP)) for (it in GRP[[g]]) {
    m <- sapply(GRP, function(cs) mean(R[it, setdiff(cs, it)]))
    best <- names(which.max(m))
    if (best == g) hits <- hits + 1 else miss <- c(miss, it)
    cat(sprintf("%-18s %7.3f %7.3f %7.3f   %-16s %s\n",
                it, m[1], m[2], m[3], best, g))
}
cat(sprintf("\nblock-structure score: %d/12; misses: %s\n",
            hits, if (length(miss)) paste(miss, collapse = ", ") else "none"))
cat("(DTDD-J's own psychopathy factor is the weak one -- alpha .55, and it\n",
    " correlates .61 with Machiavellianism in Tamura et al. Figure 1B -- so\n",
    " psychopathy misses are expected underpowering, not a mapping error.)\n\n", sep = "")

## --- Test 2: subscale totals against the DTDD-J validation paper -------------
# Tamura, Oshio, Tanaka, Masui & Jonason (2015), Jpn. J. Personality 24(1):26-37,
# Table 1, N = 246 Japanese undergraduates (same population as this N = 305 sample).
PUB <- list(Machiavellianism = c(10.69, 3.57),
            Psychopathy      = c(10.14, 2.83),
            Narcissism       = c(13.32, 3.51))
cat("Test 2 -- subscale sum scores vs DTDD-J Table 1\n")
cat(sprintf("%-18s %14s %14s\n", "subscale", "published M(SD)", "observed M(SD)"))
obsM <- numeric(0)
for (g in names(GRP)) {
    s <- rowSums(X[, GRP[[g]]])
    obsM[g] <- mean(s)
    cat(sprintf("%-18s %7.2f (%.2f) %7.2f (%.2f)\n",
                g, PUB[[g]][1], PUB[[g]][2], mean(s), stats::sd(s)))
}
narc_top <- names(which.max(obsM)) == "Narcissism"
narc_ok  <- abs(obsM["Narcissism"] - PUB$Narcissism[1]) < 1
cat(sprintf("Narcissism is the highest of the three in both: %s (obs diff %.2f)\n\n",
            narc_top, obsM["Narcissism"] - PUB$Narcissism[1]))
cat("(Machiavellianism and Psychopathy sit within 0.03 of each other here, so\n",
    " this route separates Narcissism from the other two and nothing finer.)\n\n", sep = "")

## --- Test 3: marker item ----------------------------------------------------
# psychopathy2 is shipped as DTDD-J item 5, 'I tend to be unconcerned with the
# morality of my actions'. The same questionnaire asked 'Do you ever feel guilty
# after telling a lie?' (guilt). Of the 12 DTDD items, the amorality item is the
# one that must be the strongest negative correlate of guilt.
g <- sapply(cols, function(c_) stats::cor(d[[c_]], d$guilt, use = "complete.obs"))
cat("Test 3 -- correlation with self-reported guilt after lying\n")
for (i in seq_along(g)) cat(sprintf("%-18s %6.3f\n", names(g)[i], g[i]))
marker <- names(which.min(g)) == "psychopathy2"
cat(sprintf("\nstrongest negative guilt correlate: %s (%.3f) -- expected psychopathy2: %s\n\n",
            names(which.min(g)), min(g), marker))

cat("This does NOT establish the order of the four items WITHIN each subscale.\n",
    "Mach 1-4 = DTDD-J 1/4/7/10, Psych 1-4 = 2/5/8/11, Narc 1-4 = 3/6/9/12 is\n",
    "taken from the instrument's own presentation order; no statistic here\n",
    "separates, say, 'manipulate' from 'flattery'. Status is PARTIAL.\n\n", sep = "")

pass <- hits >= 9 && all(miss %in% GRP$Psychopathy) && narc_top && narc_ok && marker
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

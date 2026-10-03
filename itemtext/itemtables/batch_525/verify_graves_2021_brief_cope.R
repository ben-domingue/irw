# verify_graves_2021_brief_cope.R -- Step 5b mapping check (batch_525).
#
# Claim: live item BCn is Brief COPE item n in Carver's (1997) canonical numbering,
# so item_text for BCn is Carver's item n.
#
# Route (3, subscale totals): the study's own S1 Dataset (PLOS ONE
# 10.1371/journal.pone.0255634.s001) stores, beside BC1..BC28, the authors' fourteen
# 2-item subscale scores (Self_Distraction, Active_Coping, ...). For each composite we
# search ALL 378 unordered pairs of BC columns for the pair whose row-wise sum
# reproduces it exactly, and require that pair to be unique and to equal Carver's
# published scoring key. Then we tie the live table to those S1 columns by per-item
# mean and n (the processing script melts by column name, BCn -> item BCn).
#
# What this does NOT establish: order WITHIN each 2-item pair (e.g. BC1 vs BC19, both
# Self-distraction). A within-pair swap reproduces every composite identically, so the
# route pins 14 pair memberships, not 28 positions -> PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "graves_2021_brief_cope"
S1_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0255634.s001"
CACHE <- file.path("itemtext", ".cache", TABLE, "S1.csv")
if (!file.exists(CACHE)) CACHE <- file.path(".cache", TABLE, "S1.csv")

# Carver (1997) scoring key, https://www.psy.miami.edu/faculty/ccarver/brief-cope.html
KEY <- list(Self_Distraction = c(1, 19), Active_Coping = c(2, 7), Denial = c(3, 8),
            Substance_Use = c(4, 11), Emotional_Support = c(5, 15),
            Instru_Support = c(10, 23), Behavioral_Disengage = c(6, 16),
            Venting = c(9, 21), Pos_Reframe = c(12, 17), Planning = c(14, 25),
            Humor = c(18, 28), Acceptance = c(20, 24), Religion = c(22, 27),
            Self_Blame = c(13, 26))

s1 <- if (file.exists(CACHE)) read.csv(CACHE, stringsAsFactors = FALSE) else
    read.csv(url(S1_URL), stringsAsFactors = FALSE)
num <- function(x) suppressWarnings(as.numeric(trimws(as.character(x))))
bc <- sapply(paste0("BC", 1:28), function(v) num(s1[[v]]))

pairs <- combn(28, 2)
ok_all <- TRUE
cat(sprintf("%-22s %-10s %-22s %-8s %s\n", "composite", "Carver", "pairs reproducing it",
            "rows", "result"))
for (nm in names(KEY)) {
    comp <- num(s1[[nm]])
    hits <- character(0)
    for (k in seq_len(ncol(pairs))) {
        s <- bc[, pairs[1, k]] + bc[, pairs[2, k]]
        use <- !is.na(s) & !is.na(comp)
        if (sum(use) > 0 && all(s[use] == comp[use]))
            hits <- c(hits, paste0("{", pairs[1, k], ",", pairs[2, k], "}"))
    }
    want <- paste0("{", KEY[[nm]][1], ",", KEY[[nm]][2], "}")
    s <- bc[, KEY[[nm]][1]] + bc[, KEY[[nm]][2]]
    use <- !is.na(s) & !is.na(comp)
    good <- length(hits) == 1 && hits == want
    ok_all <- ok_all && good
    cat(sprintf("%-22s %-10s %-22s %-8d %s\n", nm, want, paste(hits, collapse = " "),
                sum(use), if (good) "unique match" else "MISMATCH"))
}

# Tie the live table to the S1 columns.
d <- irw::irw_fetch(TABLE)
live_m <- tapply(d$resp, d$item, mean)[paste0("BC", 1:28)]
live_n <- tapply(d$resp, d$item, length)[paste0("BC", 1:28)]
s1_m <- colMeans(bc, na.rm = TRUE)
s1_n <- colSums(!is.na(bc))
cat("\nitem   S1_mean  live_mean  S1_n  live_n\n")
for (i in 1:28) cat(sprintf("%-6s %7.4f %9.4f %5d %7d\n", paste0("BC", i), s1_m[i],
                            live_m[i], s1_n[i], live_n[i]))
tie <- max(abs(s1_m - live_m)) < 1e-9 && all(s1_n == live_n)
cat(sprintf("\nlive vs S1: max |mean diff| = %.2e, n identical for all 28: %s\n",
            max(abs(s1_m - live_m)), all(s1_n == live_n)))
cat("Not established: order within each of the 14 pairs (a within-pair swap reproduces\n",
    "every composite), so this pins pair membership only -- status PARTIAL.\n", sep = "")

cat(if (ok_all && tie) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# Step 5b verification for jo_2023_sno.
#
# CLAIM UNDER TEST: the live item code SNOk carries the wording that the paper's
# S1 Appendix (Table A1, "List of Constructs and Items") prints against the label
# "SNOk" (Jo & Baek 2023, PLOS ONE 10.1371/journal.pone.0283997).
# mapping_basis = paper_explicit.
#
# The chain has two links and this script tests the second, which is the only one
# that could silently break:
#   (a) appendix label -> source column name. The appendix prints the codes SNO1,
#       SNO2, SNO3, and the S1 File CSV's header carries exactly those three names.
#       This is a literal label match, not an order inference.
#   (b) source column -> live IRW item code. data/jo_2023_social_networking.py
#       melts value_vars=["SNO1","SNO2","SNO3"] with var_name="item", so the code
#       IS the source column name. A shifted or permuted assignment would show up
#       as mismatched response distributions.
#
# FALSIFIABLE PREDICTION for (b): for each item, the count of respondents at each
# of the 7 scale points must match the corresponding raw S1 column cell for cell.
# The three columns are distinguishable: SNO1 differs grossly (mean 5.84 vs 6.10 /
# 6.12), and the near-tied SNO2/SNO3 are separated by their level counts
# (4:30 vs 29, 5:57 vs 59, 6:70 vs 69, 7:180 vs 181) -- so any transposition of
# the three codes breaks at least one cell.
#
# This does NOT re-check item or resp sets (validate_items.R did that), and it does
# NOT establish anything about option_text: the study never published its scale
# anchors, so option_text ships blank.

suppressMessages(library(irw))
TABLE <- "jo_2023_sno"
ITEMS <- c("SNO1", "SNO2", "SNO3")

# Raw S1 File counts at scale points 1..7, read from the deposit
# (https://doi.org/10.1371/journal.pone.0283997.s002, PLOS ONE_COVID-19_Korea+Vietnam_345.csv),
# columns SNO1/SNO2/SNO3, n=345 each. Hard-coded so the script runs offline; the
# fetch below is attempted first and overrides them when it succeeds.
RAW <- rbind(SNO1 = c(5, 2, 6, 48, 57, 79, 148),
             SNO2 = c(1, 1, 6, 30, 57, 70, 180),
             SNO3 = c(1, 1, 5, 29, 59, 69, 181))
colnames(RAW) <- 1:7

src <- try({
  tf <- tempfile(fileext = ".zip"); dd <- tempfile(); dir.create(dd)
  utils::download.file("https://doi.org/10.1371/journal.pone.0283997.s002", tf,
                       quiet = TRUE, mode = "wb")
  utils::unzip(tf, exdir = dd)
  f <- list.files(dd, pattern = "\\.csv$", full.names = TRUE, recursive = TRUE)[1]
  read.csv(f, fileEncoding = "latin1", check.names = FALSE)
}, silent = TRUE)

if (!inherits(src, "try-error") && all(ITEMS %in% names(src))) {
  RAW <- t(sapply(ITEMS, function(i) as.vector(table(factor(src[[i]], levels = 1:7)))))
  colnames(RAW) <- 1:7
  cat("Raw S1 File fetched from the PLOS deposit; counts recomputed.\n\n")
} else {
  cat("Raw S1 File not reachable; using the hard-coded counts read from it.\n\n")
}

d <- irw::irw_fetch(TABLE)
LIVE <- t(sapply(ITEMS, function(i) as.vector(table(factor(d$resp[d$item == i], levels = 1:7)))))
colnames(LIVE) <- 1:7

cat(sprintf("%-6s %-8s %s\n", "item", "source", "counts at resp 1..7"))
ok <- TRUE
for (i in ITEMS) {
  cat(sprintf("%-6s %-8s %s   (n=%d, mean %.4f)\n", i, "raw S1",
              paste(sprintf("%4d", RAW[i, ]), collapse = " "), sum(RAW[i, ]),
              sum(RAW[i, ] * 1:7) / sum(RAW[i, ])))
  cat(sprintf("%-6s %-8s %s   (n=%d, mean %.4f)\n", "", "live IRW",
              paste(sprintf("%4d", LIVE[i, ]), collapse = " "), sum(LIVE[i, ]),
              sum(LIVE[i, ] * 1:7) / sum(LIVE[i, ])))
  if (!identical(as.integer(RAW[i, ]), as.integer(LIVE[i, ]))) ok <- FALSE
}

cat("\nRival mappings (each transposition of the three codes), cells mismatched vs live:\n")
perms <- list(c(2, 1, 3), c(1, 3, 2), c(3, 2, 1), c(2, 3, 1), c(3, 1, 2))
for (p in perms) {
  n <- sum(RAW[p, ] != LIVE)
  cat(sprintf("  %-18s %d of 21 cells differ\n",
              paste(ITEMS, "<-", ITEMS[p], collapse = ", "), n))
  if (n == 0) ok <- FALSE
}

cat(sprintf("\nIdentity mapping: %d of 21 cells differ\n", sum(RAW != LIVE)))
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

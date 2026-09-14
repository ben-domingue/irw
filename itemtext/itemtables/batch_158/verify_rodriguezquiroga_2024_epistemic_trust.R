# verify_rodriguezquiroga_2024_epistemic_trust.R -- Step 5b, route 1
#
# CLAIM UNDER TEST: live item code e<i> carries the responses to item <i> of the
# Argentine ETMCQ as numbered in S1 Appendix A of PLOS ONE 10.1371/journal.pone.0311352,
# whose wording is what this table ships.
#
# FALSIFIABLE PREDICTION: the paper's Table 3 publishes, per item number, the Study 1
# M, SD, skewness and kurtosis (N = 1018). If e3 and e4 were swapped, e3's four moments
# would land on published item 4, not item 3.
#
# DATA: the study's own S2 Table (the deposit the IRW table was built from). Fetching it
# rather than irw_fetch() is deliberate -- irw_fetch exports the whole table against the
# 200GB/30d cap, and data/rodriguezquiroga_2024_epistemic_trust.py is a pure pass-through
# (ITEM_COLS = [f"e{i}" for i in 1..15]; df.melt(value_vars=ITEM_COLS) with no rename), so
# live item "e<i>" IS S2 column "e<i>". The live item/resp SETS are re-confirmed here with
# irw_table_sets(), which is server-side and free.

suppressMessages(library(irw))

TABLE <- "rodriguezquiroga_2024_epistemic_trust"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0311352.s002")

# Paper Table 3, Study 1 column: M, SD, skewness, kurtosis, for item 1..15.
PUB <- data.frame(
  item = 1:15,
  M    = c(4.5, 5.4, 3.9, 4.0, 3.0, 2.9, 5.1, 5.5, 4.3, 3.4, 3.7, 2.7, 5.1, 3.5, 3.8),
  SD   = c(1.8, 1.5, 1.7, 1.7, 1.7, 1.6, 1.4, 1.3, 1.6, 1.7, 1.7, 1.7, 1.6, 1.6, 1.8),
  skew = c(-0.43, -1.11, 0.07, -0.03, 0.58, 0.67, -0.79, -1.09, -0.19, 0.29, 0.09,
           0.82, -0.80, 0.29, -0.007),
  kurt = c(-0.91, 0.60, -0.86, -0.88, -0.75, -0.47, 0.27, 1.03, -0.69, -0.86, -1.00,
           -0.45, -0.18, -0.80, -1.15))

tmp <- tempfile(fileext = ".csv")
utils::download.file(URL, tmp, quiet = TRUE,
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
d <- utils::read.csv2(tmp, check.names = FALSE, fileEncoding = "UTF-8-BOM")
cat(sprintf("S2 Table: %d respondents, %d item columns\n", nrow(d), sum(grepl("^e\\d+$", names(d)))))

skewness <- function(x) { n <- length(x); m <- mean(x); s <- sd(x)
    (n / ((n - 1) * (n - 2))) * sum(((x - m) / s)^3) }
kurtosis <- function(x) { n <- length(x); m <- mean(x); s <- sd(x)
    ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * sum(((x - m) / s)^4) -
        (3 * (n - 1)^2) / ((n - 2) * (n - 3)) }

obs <- t(sapply(1:15, function(i) { x <- d[[paste0("e", i)]]
    c(M = mean(x), SD = sd(x), skew = skewness(x), kurt = kurtosis(x)) }))

# Distance in the 4 moments, scaled so each contributes comparably.
dist_mat <- matrix(NA_real_, 15, 15,
                   dimnames = list(paste0("e", 1:15), paste0("paper item ", 1:15)))
for (i in 1:15) for (j in 1:15)
    dist_mat[i, j] <- abs(obs[i, "M"]    - PUB$M[j])    / 0.05 +
                      abs(obs[i, "SD"]   - PUB$SD[j])   / 0.05 +
                      abs(obs[i, "skew"] - PUB$skew[j]) / 0.005 +
                      abs(obs[i, "kurt"] - PUB$kurt[j]) / 0.005

cat(sprintf("\n%-5s %-32s %-32s %8s %8s\n", "code", "observed (M SD skew kurt)",
            "published item (M SD skew kurt)", "best", "2nd/best"))
ok <- TRUE
for (i in 1:15) {
    o <- order(dist_mat[i, ])
    best <- o[1]
    ratio <- dist_mat[i, o[2]] / max(dist_mat[i, best], 1e-9)
    hit <- (best == i) && ratio > 5
    ok <- ok && hit
    cat(sprintf("e%-4d %-32s %-32s %8.1f %8.1f  %s\n", i,
        sprintf("%.2f %.2f %+.3f %+.3f", obs[i,1], obs[i,2], obs[i,3], obs[i,4]),
        sprintf("#%d: %.1f %.1f %+.3f %+.3f", best, PUB$M[best], PUB$SD[best],
                PUB$skew[best], PUB$kurt[best]),
        dist_mat[i, best], ratio, if (hit) "OK" else "MISMATCH"))
}

# Free, server-side confirmation that the codes/levels shipped are the live ones.
ts <- irw::irw_table_sets(TABLE)
li <- sort(unique(as.character(ts$item))); lr <- sort(unique(as.numeric(ts$resp)))
cat(sprintf("\nlive item set == e1..e15: %s ; live resp set == 1..7: %s\n",
            identical(li, sort(paste0("e", 1:15))), identical(lr, as.numeric(1:7))))

cat("\nWhat this does NOT establish: it verifies the code->paper-item-number tie only.\n",
    "It cannot detect an error in Appendix A's own numbering, and it does not check the\n",
    "option_text->resp direction (1 = muy en desacuerdo ... 7 = muy de acuerdo), which\n",
    "rests on the printed anchor row of Appendix A rather than on the data.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

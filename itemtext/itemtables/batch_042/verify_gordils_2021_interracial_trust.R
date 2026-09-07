# verify_gordils_2021_interracial_trust.R  --  Step 5b evidence, re-runnable.
#
# WHAT IS BEING VERIFIED, and what is not.
#
# The IRW item codes TRUST1..TRUST4 ARE the source spreadsheets' own column names
# (data/gordils_2021_interracial.py melts df[["id"] + ["TRUST1".."TRUST4"]]), so no
# renaming or positional step exists. The one inference this extraction makes on the
# item_text axis is that appendix S1's four unnumbered "Perceived Interracial Trust"
# sentences are listed in column order (mapping_basis = paper_order). NO data route can
# test that: all four items share one 1-7 scale, the scale has no subscales, no reverse-
# worded items, no marker item, and the paper publishes no per-item statistics. That axis
# is therefore UNVERIFIED and the sidecar says so.
#
# What this script DOES verify, decisively, is the OTHER mapping axis --
# option_text <-> resp, i.e. that the shipped anchors run 1 = "Not at all" (low trust)
# ... 7 = "Completely" (high trust) rather than the reverse. The paper analyses the
# REVERSE-scored composite MISTRUST = MEAN(8 - TRUSTn) (S3 Data syntax, line 142) and
# publishes an exact test on it: Study 1 HRC vs LRC, t(845) = 3.32, 95% CI [.14, .53],
# d = .23. Recomputing that from the raw columns under the shipped direction must
# reproduce those numbers; under the flipped direction the effect changes sign.
# Reproducing it also confirms instrument identity (Step 3b): these four columns really
# are the paper's interracial-mistrust scale, not another measure from the same battery.
#
# No full-table export: per-item n is taken from irw::irw_table_sets() (server-side).

suppressMessages(library(irw))

TABLE <- "gordils_2021_interracial_trust"
ITEMS <- c("TRUST1", "TRUST2", "TRUST3", "TRUST4")

PUB_T   <- 3.32          # paper, Study 1 mistrust, t(845)
PUB_DF  <- 845
PUB_CI  <- c(0.14, 0.53)
PUB_D   <- 0.23

url <- function(s) paste0("https://journals.plos.org/plosone/article/file",
                          "?type=supplementary&id=10.1371/journal.pone.0245671.", s)

get_xlsx <- function(s) {
    f <- file.path(tempdir(), paste0(s, ".xlsx"))
    if (!file.exists(f))
        utils::download.file(url(s), f, mode = "wb", quiet = TRUE,
                             headers = c("User-Agent" = "IRW-itemtext/1.0"))
    d <- as.data.frame(readxl::read_excel(f, sheet = "Sheet1"))
    d$AttentionCheck <- suppressWarnings(as.numeric(d$AttentionCheck))
    d[!is.na(d$AttentionCheck) & d$AttentionCheck == 2, , drop = FALSE]
}

s1 <- get_xlsx("s004")   # Study 1
s4 <- get_xlsx("s007")   # Study 2

num <- function(d) {
    m <- sapply(d[ITEMS], function(x) suppressWarnings(as.numeric(x)))
    m[m < 1 | m > 7] <- NA
    m
}

## ---- (0) tie the raw files to the live table, without exporting it ----------
m <- rbind(num(s1), num(s4))
recon_n <- colSums(!is.na(m))
ts <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(ts$per_item)
live_n <- setNames(pi$n[match(ITEMS, pi$item)], ITEMS)

cat("-- per-item n: reconstruction from the PLOS spreadsheets vs live IRW --\n")
cat(sprintf("%-8s %12s %12s %8s\n", "item", "reconstructed", "live", "diff"))
for (i in ITEMS)
    cat(sprintf("%-8s %12d %12d %8d\n", i, recon_n[[i]], live_n[[i]],
                recon_n[[i]] - live_n[[i]]))
n_ok <- all(recon_n == live_n)
cat("per-item n identical:", n_ok, "\n\n")

## ---- (1) the published t-test, under the SHIPPED anchor direction -----------
m1  <- num(s1)
mis <- rowMeans(8 - m1, na.rm = FALSE)          # paper's MISTRUST composite
grp <- s1$Condition                              # "PCOMP 6.27" = HRC, "PCOMP 1.73" = LRC
hi  <- mis[grp == "PCOMP 6.27"]; hi <- hi[!is.na(hi)]
lo  <- mis[grp == "PCOMP 1.73"]; lo <- lo[!is.na(lo)]

sp   <- sqrt(((length(hi) - 1) * var(hi) + (length(lo) - 1) * var(lo)) /
             (length(hi) + length(lo) - 2))
se   <- sp * sqrt(1 / length(hi) + 1 / length(lo))
diff <- mean(hi) - mean(lo)
tval <- diff / se
dfv  <- length(hi) + length(lo) - 2
ci   <- diff + c(-1.96, 1.96) * se
dval <- diff / sp

cat("-- Study 1 mistrust = MEAN(8 - TRUST1..4), HRC vs LRC --\n")
cat(sprintf("  n HRC = %d, n LRC = %d;  M(HRC) = %.3f, M(LRC) = %.3f\n",
            length(hi), length(lo), mean(hi), mean(lo)))
cat(sprintf("%-14s %12s %12s\n", "", "published", "recomputed"))
cat(sprintf("%-14s %12.2f %12.3f\n", "t",  PUB_T,  tval))
cat(sprintf("%-14s %12d %12d\n",    "df", PUB_DF, dfv))
cat(sprintf("%-14s %12s %12s\n",    "95% CI",
            sprintf("[%.2f, %.2f]", PUB_CI[1], PUB_CI[2]),
            sprintf("[%.2f, %.2f]", ci[1], ci[2])))
cat(sprintf("%-14s %12.2f %12.3f\n", "Cohen d", PUB_D, dval))

## ---- (2) the counterfactual: flipped anchors --------------------------------
trust <- rowMeans(m1, na.rm = FALSE)
fh <- mean(trust[grp == "PCOMP 6.27"], na.rm = TRUE)
fl <- mean(trust[grp == "PCOMP 1.73"], na.rm = TRUE)
cat(sprintf("\n  counterfactual (1 = 'Completely' ... 7 = 'Not at all'): the same test on the\n"))
cat(sprintf("  UN-reversed composite gives HRC %.3f vs LRC %.3f, difference %+.3f -- the\n",
            fh, fl, fh - fl))
cat("  opposite sign to the published effect, so the shipped anchor direction is the\n")
cat("  only one consistent with the paper.\n")

t_ok  <- abs(tval - PUB_T) <= 0.02 && dfv == PUB_DF
ci_ok <- all(abs(round(ci, 2) - PUB_CI) <= 0.01)
d_ok  <- abs(dval - PUB_D) <= 0.01
sign_ok <- (fh - fl) < 0

cat("\nNOT ESTABLISHED by this script: which of the four appendix sentences belongs to\n",
    "TRUST1 vs TRUST2 vs TRUST3 vs TRUST4. That rests on appendix presentation order\n",
    "alone (mapping_basis = paper_order); no per-item statistics, range structure,\n",
    "subscale split, keying asymmetry or marker item exists to test it, so the\n",
    "verification status for this table is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (n_ok && t_ok && ci_ok && d_ok && sign_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

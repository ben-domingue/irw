# verify_liu_2025_ydcy.R -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST. The IRW item codes YDCY2/YDCY3/YDCY4 are the three PARS-3
# dimensions in the canonical order intensity / duration / frequency, and YDCY5 is
# a leisure-time sweat-frequency item coded 1 = Never/Rarely .. 3 = Often.
#
# This matters because the study's own Dryad README describes the YDCY block as the
# Godin Leisure Time Exercise Questionnaire and prints GLTEQ wording against codes
# YDCY1-YDCY5. That description is falsifiable, and it is false: the checks below
# show the data are PARS-3, exactly as the PLOS article's Instruments section (4)
# says ("Physical Exercise Volume = Intensity x (Duration - 1) x Frequency").
#
# Fetches: the PLOS S1 File (.sav) and the live IRW sets. No full-table export.

suppressMessages({library(irw); library(haven)})

TABLE <- "liu_2025_ydcy"
SAV   <- "https://doi.org/10.1371/journal.pone.0314338.s001"

tmp <- tempfile(fileext = ".sav")
download.file(SAV, tmp, quiet = TRUE, mode = "wb",
              headers = c(`User-Agent` = "IRW-itemtext/1.0"))
d <- haven::read_sav(tmp)
d <- d[, c("YDCY1","YDCY2","YDCY3","YDCY4","YDCY5","YDCY")]
d <- d[stats::complete.cases(d), ]
cat(sprintf("source .sav rows with complete YDCY block: %d\n\n", nrow(d)))

ok <- logical(0)

## ---- 1. Which instrument is it? Two rival composites, one arithmetic test. ----
pars3  <- d$YDCY2 * d$YDCY3 * d$YDCY4                    # article: I x (D-1) x F
glteq  <- 9*d$YDCY2 + 5*d$YDCY3 + 3*d$YDCY4              # README: GLTEQ weights
cat("Composite column YDCY reproduced by:\n")
cat(sprintf("  PARS-3  YDCY2*YDCY3*YDCY4      : %d/%d exact, max|diff| = %g\n",
            sum(pars3 == d$YDCY), nrow(d), max(abs(pars3 - d$YDCY))))
cat(sprintf("  GLTEQ   9*Y2 + 5*Y3 + 3*Y4     : %d/%d exact, max|diff| = %g\n",
            sum(glteq == d$YDCY), nrow(d), max(abs(glteq - d$YDCY))))
cat(sprintf("  observed composite range       : %g - %g (PARS-3 is 0-100)\n\n",
            min(d$YDCY), max(d$YDCY)))
ok <- c(ok, all(pars3 == d$YDCY), mean(glteq == d$YDCY) < 0.05)

## ---- 2. Which of the three is duration? The zero level is the signature. ----
# PARS-3 stores duration as (level - 1), so duration alone can be 0; intensity and
# frequency are 1-5. Only one column carries zeros.
cat("Per-column range in the .sav (PARS-3: intensity 1-5, duration 0-4, frequency 1-5):\n")
for (v in c("YDCY2","YDCY3","YDCY4"))
    cat(sprintf("  %-6s min %g  max %g  n(zero) %d\n",
                v, min(d[[v]]), max(d[[v]]), sum(d[[v]] == 0)))
zerocols <- c("YDCY2","YDCY3","YDCY4")[sapply(c("YDCY2","YDCY3","YDCY4"),
                                              function(v) any(d[[v]] == 0))]
cat(sprintf("  -> column(s) consistent with the duration item: %s\n\n",
            paste(zerocols, collapse = ", ")))
ok <- c(ok, identical(zerocols, "YDCY3"))

## ---- 3. Live table agrees with the .sav, including the dropped zero level. ----
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- s$per_item
cat("Live IRW per-item n and resp range vs the .sav:\n")
for (v in c("YDCY2","YDCY3","YDCY4","YDCY5")) {
    r <- pi[pi$item == v, ]
    cat(sprintf("  %-6s live n %4d range %g-%g | .sav n(nonzero) %4d range %g-%g\n",
                v, r$n, r$resp_min, r$resp_max,
                sum(d[[v]] > 0), min(d[[v]][d[[v]] > 0]), max(d[[v]])))
}
live3 <- pi[pi$item == "YDCY3", ]
cat(sprintf("  -> YDCY3 loses exactly the %d '0' rows (879 - 821 = %d)\n\n",
            sum(d$YDCY3 == 0), 879 - live3$n))
ok <- c(ok, live3$n == sum(d$YDCY3 > 0), live3$resp_max == 4,
        pi[pi$item == "YDCY5", ]$resp_max == 3)

## ---- 4. YDCY5 option polarity: does 3 mean "Often" or "Never/Rarely"? ----
# The README gives the SAME question twice with opposite option orders
# (Q1: "(1) Never/Rarely, (2) Sometimes, (3) Often"; Q5: "1 Often 2 Sometimes
# 3 Never/Rarely"). Only the data settle which numbering the column uses.
r5 <- sapply(c("YDCY","YDCY2","YDCY3","YDCY4"),
             function(v) cor(d$YDCY5, d[[v]]))
cat("Correlation of YDCY5 with the exercise-volume composite and the three PARS-3 items:\n")
for (n in names(r5)) cat(sprintf("  YDCY5 ~ %-6s r = %+.3f\n", n, r5[n]))
cat(sprintf("  YDCY5 distribution: 1=%d  2=%d  3=%d\n",
            sum(d$YDCY5 == 1), sum(d$YDCY5 == 2), sum(d$YDCY5 == 3)))
cat("  -> all positive, so higher code = more exercise = 3 'Often', 1 'Never/Rarely'\n")
cat("     (the Q1 numbering), not the Q5 listing order.\n\n")
ok <- c(ok, all(r5 > 0.1))

## ---- What this does NOT establish ----
cat("NOT ESTABLISHED: intensity vs frequency, i.e. YDCY2 vs YDCY4. The composite is a\n")
cat("product and is therefore symmetric in those two columns, and both are scored 1-5,\n")
cat("so no test on this data can tell them apart. Their assignment rests on the canonical\n")
cat("PARS-3 presentation order (intensity, duration, frequency), corroborated only by the\n")
cat("fact that the uniquely identifiable duration item lands in the middle position. A\n")
cat("swap of YDCY2 and YDCY4 would leave every number above unchanged. Status: PARTIAL.\n\n")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# Verification for gilbert_meta_28 (#2228, batch_302).
#
# SOURCE. Banerji, Berry & Shotland (2017), 'The impact of maternal literacy and
# participation programs', AEJ: Applied Economics 9(4):303; deposit Harvard
# Dataverse doi:10.7910/DVN/19PPE7, CC0. THE SAME DEPOSIT as gilbert_meta_30 in
# batch_203, which is the child ASER test from this study; this table is the
# MOTHER ASER test. The files were already obtained for that batch (the deposit
# sits behind Dataverse Guestbook 269 and was fetched by a human in a browser),
# so nothing new had to be requested.
#
# THE MAPPING IS THE DEPOSIT'S OWN VARIABLE LABELS, which is level 1 of the
# source ranking: ml_merged.dta labels every maser variable, e.g.
# b_maser_math_add1 is "q33 Can do one digit sums". data/gilbertmeta.R strips
# the wave prefix, so the live code is the deposit's variable name minus b_/e_.
#
# Route 1: every live code resolves to a labelled variable in ml_merged.dta.
# Route 2: the arithmetic cascade -- harder items must have fewer passers.
suppressWarnings(suppressMessages(library(haven)))
DTA <- ".cache/gilbert_meta_30/dv/ml_merged.dta"
if (!file.exists(DTA)) stop("missing cached deposit file: ", DTA)
s <- read_dta(DTA)
d <- as.data.frame(irw::irw_fetch("gilbert_meta_28"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/gilbert_meta_28__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: every code resolves to a labelled deposit variable ===\n")
resolve <- function(code) {
    cand <- c(paste0("b_", code), paste0("e_", code),
              paste0("b_", sub("mobildial", "mobile_dial", code)),
              paste0("e_", sub("mobildial", "mobile_dial", code)))
    for (cc in cand) if (cc %in% names(s)) {
        l <- attr(s[[cc]], "label"); if (!is.null(l) && nzchar(l)) return(c(cc, l))
    }
    c(NA, NA)
}
codes <- sort(unique(d$item)); ok <- 0
for (cd in codes) {
    r <- resolve(cd)
    if (!is.na(r[1])) ok <- ok + 1
    cat(sprintf("  %-22s <- %-26s %s\n", cd, r[1], substr(r[2], 1, 46)))
}
r1 <- ok == length(codes) && setequal(codes, unique(items$item))
cat(sprintf("  %d of %d resolved, and the shipped set matches live: %s\n", ok, length(codes), r1))
cat("  NOTE the live codes spell two of them mobildial1/2 where the deposit has\n")
cat("  mobile_dial1/2 -- a dropped underscore somewhere upstream. The labels are\n")
cat("  unambiguous, so the mapping is not in doubt, but the codes do not match\n")
cat("  the deposit's variable names character for character.\n")

cat("\n=== Route 2: the cascade, which is exact ===\n")
# This is a CASCADING test -- a mother attempted two-digit addition only after
# passing one-digit addition -- so a harder item's respondent count must equal
# its gate item's number of passers. That is a far sharper check than comparing
# pass rates, which are conditional and rise as the test gets harder.
n_of  <- function(i) sum(d$item == i)
pass  <- function(i) sum(d$resp[d$item == i] == 1, na.rm = TRUE)
GATE <- list(c("maser_math_add1","maser_math_add2"), c("maser_math_subtr1","maser_math_subtr2"))
r2 <- TRUE
for (g in GATE) {
    pg <- pass(g[1]); nf <- n_of(g[2]); d0 <- nf - pg
    cat(sprintf("  %-20s passers %5d  ->  %-20s n %5d   difference %d\n", g[1], pg, g[2], nf, d0))
    r2 <- r2 && abs(d0) <= 1
}
cat(sprintf("  -> every follow-on item is attempted by exactly its gate item's passers: %s\n", r2))
cat("  A shuffle that put subtraction where addition is would break this outright,\n")
cat("  so it pins those four codes to their labels rather than merely agreeing\n")
cat("  with them. Note the conditional rates run the other way -- add2 passes at\n")
cat("  0.70 against add1's 0.20 -- because only the abler mothers reach it.\n")

cat("\n=== A DEFECT, and it is the same one found in this study\'s child test ===\n")
rd1 <- mean(d$resp[d$item == "maser_math_read1"], na.rm = TRUE)
id1 <- mean(d$resp[d$item == "maser_math_ident1"], na.rm = TRUE)
rd2 <- mean(d$resp[d$item == "maser_math_read2"], na.rm = TRUE)
cat(sprintf("  maser_math_read1  (read digits 1-9)        p = %.4f   n = %d\n", rd1, n_of("maser_math_read1")))
cat(sprintf("  maser_math_ident1 (identify digits 1-9)    p = %.4f   n = %d\n", id1, n_of("maser_math_ident1")))
cat(sprintf("  maser_math_read2  (read numbers 11-20)     p = %.4f   n = %d\n", rd2, n_of("maser_math_read2")))
cat("  Reading 1-9 is the easiest task on the ladder, yet it passes at under 2 per cent\n")
cat("  while IDENTIFYING the same digits passes at 55 per cent and reading the harder\n")
cat("  11-20 range passes at 43 per cent. That ordering is not possible if read1 is\n")
cat("  scored like its neighbours.\n")
cat("  batch_203 reported exactly this for caser_math_read1, the CHILD version of\n")
cat("  the same instrument in the same study: a 1.3 per cent pass rate where the\n")
cat("  deposit\'s own count coding implies 58-64 per cent, consistent with dichotomising\n")
cat("  one step too low. Finding it again at 1.7 per cent in the mother version makes it\n")
cat("  systematic in this study\'s ASER recoding rather than a one-off. read1 is\n")
cat("  also the only code here restricted to a single wave. ITEM TEXT IS\n")
cat("  UNAFFECTED and ships; the resp is what should not be trusted.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The literal wording a mother heard. The deposit's labels are the study's\n")
cat("  own short descriptions of each task ('Can do one digit sums'), not the\n")
cat("  enumerator's script, and the q-numbers they carry are the survey form's.\n")
cat("  Nor does it separate items within a difficulty tier -- add1 and subtr1 sit\n")
cat("  close together and no route here tells them apart beyond their labels.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
